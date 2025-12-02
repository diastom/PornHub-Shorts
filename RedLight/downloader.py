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
from .converter import VideoConverter


class CustomHLSDownloader:
    """
    PH Shorties Downloader - A robust tool to download HLS streams from PH Shorties.
    Features: Quality selection, Proxy support, Auto-retry, Speed limiting, and FFmpeg conversion.
    """

    def __init__(self, output_name: str = None, headers: dict | None = None, 
                 keep_ts: bool = False, proxy: str = None, progress_callback=None, speed_limit: str = None):
        self.output_name = Path(output_name) if output_name else None
        self.keep_ts = keep_ts
        self.session = requests.Session()
        self.progress_callback = progress_callback
        self.speed_limit = self._parse_speed_limit(speed_limit) if speed_limit else None
        
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
    
    def _parse_speed_limit(self, limit_str: str) -> int:
        limit_str = limit_str.upper().strip()
        
        multipliers = {
            'K': 1024,
            'M': 1024 * 1024,
            'G': 1024 * 1024 * 1024
        }
        
        for suffix, multiplier in multipliers.items():
            if limit_str.endswith(suffix):
                try:
                    value = float(limit_str[:-1])
                    return int(value * multiplier)
                except ValueError:
                    return None
        
        try:
            return int(limit_str)
        except ValueError:
            return None

    def _sanitize_filename(self, title: str) -> str:
        title = re.sub(r'^Watch the XXX short\s*-\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+on\s+Pornhub.*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*-\s*Pornhub.*$', '', title, flags=re.IGNORECASE)
        
        cleaned = re.sub(r'[\\/*?:"<>|]', "", title)
        cleaned = " ".join(cleaned.split())
        
        if not cleaned:
            return f"video_{int(time.time())}"
            
        return cleaned[:200]

    def extract_video_info(self, page_url: str) -> str:
        
        self.session.headers.update({'Referer': page_url})
        
        try:
            response = self.session.get(page_url, timeout=15)
            response.raise_for_status()
            html_content = response.text
            

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


            streams = {}
            shorties_id = self._extract_shorties_id(page_url)
            
            all_media_defs = re.findall(r'mediaDefinitions["\']?\s*[:=]\s*(\[.+?\])', html_content)
            
            for media_def_match in all_media_defs:
                try:
                    definitions = json.loads(media_def_match)
                    
                    for video in definitions:
                        if video.get('format') == 'hls' and video.get('videoUrl'):
                            video_url = video['videoUrl']
                            if not video_url:
                                continue
                            
                            video_url = video_url.replace('\\/', '/')
                            
                            quality = video.get('quality')
                            if isinstance(quality, list):
                                quality = quality[0]
                            
                            if quality:
                                try:
                                    q_int = int(quality)
                                    streams[q_int] = video_url
                                except ValueError:
                                    streams[quality] = video_url
                            else:
                                q_match = re.search(r'(\d{3,4})[Pp]', video_url)
                                if q_match:
                                    streams[int(q_match.group(1))] = video_url
                                else:
                                    streams['unknown'] = video_url
                    
                    if streams:
                        break
                        
                except Exception as e:
                    pass


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

    def extract_video_id(self, url: str) -> str:
        """Extracts video ID from URL."""
        match = re.search(r'viewkey=([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
        return "unknown"
    
    def _extract_shorties_id(self, url: str) -> str:
        """Extracts shorties ID from shorties URL."""
        match = re.search(r'/shorties/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
        return None

    def download_subtitles(self, html_content: str, output_base: Path) -> bool:
        """Attempts to find and download subtitles."""
        try:
            # Look for captions in mediaDefinitions
            media_def_match = re.search(r'mediaDefinitions\s*[:=]\s*(\[.+?\])', html_content)
            if media_def_match:
                definitions = json.loads(media_def_match.group(1))
                for video in definitions:
                    if video.get('format') == 'srt' or video.get('format') == 'vtt':
                        sub_url = video.get('videoUrl')
                        if sub_url:
                            ext = video.get('format', 'srt')
                            sub_path = output_base.with_suffix(f".{ext}")
                            
                            response = self.session.get(sub_url)
                            if response.status_code == 200:
                                with open(sub_path, 'wb') as f:
                                    f.write(response.content)
                                return True
            return False
        except Exception:
            return False

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

            response = self.session.get(m3u8_url, timeout=10)
            if response.status_code == 403:
                raise PermissionError("403 Forbidden. Server rejected the request (Check Referer/User-Agent).")
            response.raise_for_status()
            playlist_content = response.text
            
            if "#EXT-X-STREAM-INF" in playlist_content:
                qualities = self._get_qualities(playlist_content, m3u8_url)
                
                if not qualities:
                    pass
                else:
                    sorted_keys = sorted([k for k in qualities.keys() if isinstance(k, int)], reverse=True)
                    
                    selected_url = None
                    selected_res = None

                    if preferred_quality == 'best':
                        selected_res = sorted_keys[0] if sorted_keys else list(qualities.keys())[0]
                    elif preferred_quality == 'worst':
                        selected_res = sorted_keys[-1] if sorted_keys else list(qualities.keys())[-1]
                    else:
                        try:
                            req_q = int(preferred_quality)
                            if req_q in qualities:
                                selected_res = req_q
                            elif sorted_keys:
                                selected_res = min(sorted_keys, key=lambda x:abs(x-req_q))
                            else:
                                selected_res = list(qualities.keys())[0]
                        except ValueError:
                             selected_res = sorted_keys[0] if sorted_keys else list(qualities.keys())[0]

                    selected_url = qualities[selected_res]
                    
                    response = self.session.get(selected_url)
                    response.raise_for_status()
                    playlist_content = response.text
                    m3u8_url = selected_url

            segments = self._parse_media_playlist(playlist_content, m3u8_url)
            total_segments = len(segments)
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
            
            converter = VideoConverter()
            return converter.ConvertTsToMp4(self.output_name, self.keep_ts)

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
        
        # Resume logic: Skip if already downloaded
        if filename.exists() and filename.stat().st_size > 0:
            return filename

        retries = 5
        for attempt in range(retries):
            try:
                response = self.session.get(url, stream=True, timeout=20)
                if response.status_code != 200:
                    raise requests.RequestException(f"Status {response.status_code}")
                
                # Check content-length if available
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) == 0:
                    raise requests.RequestException("Empty content-length")
                
                bytes_downloaded = 0
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # Filter out keep-alive chunks
                            f.write(chunk)
                            bytes_downloaded += len(chunk)
                
                # Validate downloaded file
                if bytes_downloaded == 0 or not filename.exists() or filename.stat().st_size == 0:
                    if filename.exists():
                        filename.unlink()
                    raise requests.RequestException(f"Downloaded file is empty (got {bytes_downloaded} bytes)")
                
                return filename
            except (requests.RequestException, ConnectionError) as e:
                if attempt < retries - 1:
                    time.sleep(0.5 * attempt)
                    continue
                else:
                    raise Exception(f"Failed to download segment {index} after {retries} retries: {e}")
        raise Exception(f"Failed to download segment after {retries} retries")


