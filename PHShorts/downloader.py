import requests
import re
from urllib.parse import urljoin, unquote
import concurrent.futures
import shutil
from pathlib import Path
import sys
import subprocess
import html
import time
import json


class CustomHLSDownloader:
    """
    PH Shorties Downloader - A robust tool to download HLS streams from PH Shorties.
    Features: Quality selection, Proxy support, Auto-retry, and FFmpeg conversion.
    """

    def __init__(self, output_name: str = None, headers: dict | None = None, 
                 keep_ts: bool = False, proxy: str = None, progress_callback=None):
        self.output_name = Path(output_name) if output_name else None
        self.keep_ts = keep_ts
        self.session = requests.Session()
        self.progress_callback = progress_callback
        
        # Proxy Configuration
        if proxy:
            self.session.proxies.update({
                'http': proxy,
                'https': proxy
            })

        # Default Headers (mimicking a real browser)
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/' 
        }
        
        if headers:
            default_headers.update(headers)
        
        self.session.headers.update(default_headers)

    def _sanitize_filename(self, title: str) -> str:
        # Remove site branding
        title = re.sub(r'^Watch the XXX short\s*-\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+on\s+Pornhub.*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*-\s*Pornhub.*$', '', title, flags=re.IGNORECASE)
        
        # Remove filesystem illegal chars
        cleaned = re.sub(r'[\\/*?:"<>|]', "", title)
        cleaned = " ".join(cleaned.split())
        
        if not cleaned:
            return f"video_{int(time.time())}"
            
        return cleaned[:200]

    def extract_video_info(self, page_url: str) -> str:
        """Scrapes the page for title and m3u8 link."""
        
        self.session.headers.update({'Referer': page_url})
        
        try:
            response = self.session.get(page_url, timeout=15)
            response.raise_for_status()
            html_content = response.text
            
            # --- Title Extraction ---
            if self.output_name is None:
                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
                if not title_match:
                    title_match = re.search(r'<title>(.*?)</title>', html_content)

                if title_match:
                    raw_title = html.unescape(title_match.group(1))
                    clean_title = self._sanitize_filename(raw_title)
                    self.output_name = Path(f"{clean_title}.ts")
                else:
                    self.output_name = Path("downloaded_video.ts")
            else:
                if self.output_name.suffix != '.ts':
                    self.output_name = self.output_name.with_suffix('.ts')

            # --- M3U8 Extraction ---
            streams = {}
            
            # Method 1: Try to parse mediaDefinitions from flashvars
            media_def_match = re.search(r'mediaDefinitions\s*[:=]\s*(\[.+?\])', html_content)
            if media_def_match:
                try:
                    json_str = media_def_match.group(1)
                    # Simple cleanup if needed (though usually valid JSON in PH)
                    definitions = json.loads(json_str)
                    
                    for video in definitions:
                        if video.get('format') == 'hls' and video.get('videoUrl'):
                            video_url = video['videoUrl']
                            if not video_url: continue
                            
                            # Fix slashes
                            video_url = video_url.replace('\\/', '/')
                            
                            quality = video.get('quality')
                            if isinstance(quality, list): quality = quality[0]
                            
                            if quality:
                                try:
                                    q_int = int(quality)
                                    streams[q_int] = video_url
                                except ValueError:
                                    streams[quality] = video_url
                            else:
                                # Try to guess from URL
                                q_match = re.search(r'(\d{3,4})[Pp]', video_url)
                                if q_match:
                                    streams[int(q_match.group(1))] = video_url
                                else:
                                    streams['unknown'] = video_url
                except Exception as e:
                    pass

            # Method 2: Fallback to regex if no streams found
            if not streams:
                patterns = [
                    r'"videoUrl"\s*:\s*"([^"]+m3u8[^"]*)"',
                    r'src\s*:\s*"([^"]+m3u8[^"]*)"',
                    r'file\s*:\s*"([^"]+m3u8[^"]*)"',
                    r'(https?:\\?/\\?/[^"\s]+\.m3u8[^"\s]*)'
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, html_content)
                    for match in matches:
                        clean_url = match.replace('\\/', '/')
                        if "master.m3u8" in clean_url or "index.m3u8" in clean_url:
                            if not clean_url.startswith('http'):
                                 continue
                            
                            # Try to extract quality from URL
                            q_match = re.search(r'(\d{3,4})[Pp]', clean_url)
                            if q_match:
                                streams[int(q_match.group(1))] = clean_url
                            else:
                                streams['unknown'] = clean_url

            if not streams:
                raise ValueError("No compatible HLS stream found in page source.")
            
            return streams

        except requests.exceptions.ProxyError:
            raise ConnectionError("Cannot connect to proxy. Check your proxy settings.")
        except Exception as e:
            raise RuntimeError(f"Extraction failed: {e}")

    def _get_qualities(self, playlist_content: str, base_url: str) -> dict:
        """Parses Master Playlist and returns dict {height: url}."""
        lines = playlist_content.splitlines()
        qualities = {}
        
        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF"):
                # Extract resolution (e.g., RESOLUTION=720x1280)
                res_match = re.search(r'RESOLUTION=\d+x(\d+)', line)
                
                url = lines[i+1].strip()
                if not url.startswith("http"):
                    url = urljoin(base_url, url)
                
                if res_match:
                    height = int(res_match.group(1))
                    qualities[height] = url
                else:
                    # Fallback for streams without explicit resolution tag
                    qualities[f"stream_{i}"] = url
                    
        return qualities

    def download_stream(self, m3u8_url: str, preferred_quality: str = 'best'):
        
        try:
            # 1. Get Playlist
            response = self.session.get(m3u8_url, timeout=10)
            if response.status_code == 403:
                raise PermissionError("403 Forbidden. Server rejected the request (Check Referer/User-Agent).")
            response.raise_for_status()
            playlist_content = response.text
            
            # 2. Handle Master Playlist & Quality Selection
            if "#EXT-X-STREAM-INF" in playlist_content:
                qualities = self._get_qualities(playlist_content, m3u8_url)
                
                if not qualities:
                    pass  # Use raw URL
                else:
                    # Sort qualities by resolution (if integer keys)
                    sorted_keys = sorted([k for k in qualities.keys() if isinstance(k, int)], reverse=True)
                    
                    selected_url = None
                    selected_res = None

                    if preferred_quality == 'best':
                        selected_res = sorted_keys[0] if sorted_keys else list(qualities.keys())[0]
                    elif preferred_quality == 'worst':
                        selected_res = sorted_keys[-1] if sorted_keys else list(qualities.keys())[-1]
                    else:
                        # Try to find exact match (e.g., '720')
                        try:
                            req_q = int(preferred_quality)
                            # Find closest match
                            if req_q in qualities:
                                selected_res = req_q
                            elif sorted_keys:
                                # Logic: find closest resolution
                                selected_res = min(sorted_keys, key=lambda x:abs(x-req_q))
                            else:
                                selected_res = list(qualities.keys())[0]
                        except ValueError:
                             selected_res = sorted_keys[0] if sorted_keys else list(qualities.keys())[0]

                    selected_url = qualities[selected_res]
                    
                    # Fetch final media playlist
                    response = self.session.get(selected_url)
                    response.raise_for_status()
                    playlist_content = response.text
                    m3u8_url = selected_url # Update base URL for segments

            # 3. Encryption Check
            encrypted = "#EXT-X-KEY" in playlist_content

            # 4. Parse Segments
            segments = self._parse_media_playlist(playlist_content, m3u8_url)
            total_segments = len(segments)

            # 5. Download Loop with Progress Bar
            temp_dir = Path("temp_segments")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            
            downloaded_files = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_to_segment = {
                    executor.submit(self._download_segment, seg_url, idx, temp_dir): idx 
                    for idx, seg_url in enumerate(segments)
                }
                
                completed = 0
                for future in concurrent.futures.as_completed(future_to_segment):
                    idx = future_to_segment[future]
                    try:
                        file_path = future.result()
                        downloaded_files.append((idx, file_path))
                        completed += 1
                        if self.progress_callback:
                            self.progress_callback(completed, total_segments)
                    except Exception as e:
                        pass 

            downloaded_files.sort(key=lambda x: x[0])
            
            with open(self.output_name, 'wb') as outfile:
                for _, segment_file in downloaded_files:
                    with open(segment_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            shutil.rmtree(temp_dir)
            
            return self.convert_to_mp4()

        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise RuntimeError(f"Critical failure: {e}")

    def _parse_media_playlist(self, content: str, base_url: str) -> list[str]:
        lines = content.splitlines()
        segments = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if not line.startswith("http"):
                line = urljoin(base_url, line)
            segments.append(line)
        return segments

    def _download_segment(self, url: str, index: int, save_dir: Path) -> Path:
        filename = save_dir / f"segment_{index:04d}.ts"
        retries = 5
        for attempt in range(retries):
            try:
                response = self.session.get(url, stream=True, timeout=20)
                if response.status_code != 200:
                    raise requests.RequestException(f"Status {response.status_code}")
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return filename
            except (requests.RequestException, ConnectionError):
                time.sleep(0.5 * attempt)
                continue
        raise Exception(f"Failed to download segment after {retries} retries")

    def convert_to_mp4(self):
        input_file = self.output_name
        output_file = self.output_name.with_suffix('.mp4')
        
        if self.keep_ts:
            return str(input_file)

        if not shutil.which("ffmpeg"):
            return str(input_file)

        try:
            cmd = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-i', str(input_file), 
                '-c', 'copy', 
                '-bsf:a', 'aac_adtstoasc',
                str(output_file)
            ]
            subprocess.run(cmd, check=True)
            if input_file.exists():
                input_file.unlink()
            return str(output_file)
        except subprocess.CalledProcessError:
            return str(input_file)
