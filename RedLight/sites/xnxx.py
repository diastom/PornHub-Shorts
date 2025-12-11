import re
import requests
import subprocess
import shutil
import concurrent.futures
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from urllib.parse import unquote

from .base import BaseSiteDownloader, BaseSiteSearch


class XNXXDownloader(BaseSiteDownloader):
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.xnxx.com/',
        }
        self.session.headers.update(self.headers)
    
    def download(
        self,
        url: str,
        quality: str = "best",
        output_dir: str = "./downloads",
        filename: Optional[str] = None,
        keep_original: bool = False,
        proxy: Optional[str] = None,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> str:
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        title, links = self._extract_info(url)
        
        selected_quality, selected_url = self._select_quality(links, quality)
        
        if filename:
            output_file = output_path / filename
        else:
            ext = ".mp4" if "HLS" not in selected_quality else ".ts"
            safe_title = self._sanitize_filename(title)
            output_file = output_path / f"{safe_title}_{selected_quality.replace(' ','')}{ext}"
        
        if '.m3u8' in selected_url:
            self._download_hls_ffmpeg(selected_url, str(output_file))
        else:
            self._download_with_progress(selected_url, str(output_file), on_progress)
        
        return str(output_file)
    
    def get_info(self, url: str) -> Dict[str, Any]:
        
        title, links = self._extract_info(url)
        
        available_qualities = []
        for quality_name in links.keys():
            if "High" in quality_name:
                available_qualities.append(720)
            elif "Low" in quality_name:
                available_qualities.append(480)
            elif "HLS" in quality_name:
                available_qualities.append(1080)
        
        available_qualities = sorted(set(available_qualities), reverse=True)
        
        video_id = self._extract_video_id(url)
        
        return {
            "title": title,
            "available_qualities": available_qualities,
            "video_id": video_id,
            "site": "xnxx"
        }
    
    def list_qualities(self, url: str) -> List[int]:
        
        info = self.get_info(url)
        return info["available_qualities"]
    
    @staticmethod
    def is_supported_url(url: str) -> bool:
        
        return "xnxx.com" in url.lower()
    
    @staticmethod
    def get_site_name() -> str:
        
        return "xnxx"
    
    def _extract_info(self, url: str) -> tuple:
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return self._parse_html(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to extract video info: {e}")
    
    def _parse_html(self, content: str) -> tuple:
        
        import html as html_lib
        
        title_match = re.search(r"html5player\.setVideoTitle\(['\"](.+?)['\"]\)", content)
        if not title_match:
            title_match = re.search(r'<title>(.*?)</title>', content)
        
        title = "xnxx_video"
        if title_match:
            raw = html_lib.unescape(title_match.group(1))
            title = re.sub(r'\s*-\s*XNXX.*$', '', raw, flags=re.IGNORECASE)
            title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
        
        links = {}
        
        hq_match = re.search(r"html5player\.setVideoUrlHigh\(['\"](.+?)['\"]\)", content)
        if hq_match and hq_match.group(1):
            links['High Quality'] = unquote(hq_match.group(1))
        
        lq_match = re.search(r"html5player\.setVideoUrlLow\(['\"](.+?)['\"]\)", content)
        if lq_match and lq_match.group(1):
            links['Low Quality'] = unquote(lq_match.group(1))
        
        hls_match = re.search(r"html5player\.setVideoHLS\(['\"](.+?)['\"]\)", content)
        if hls_match and hls_match.group(1):
            links['HLS (Adaptive)'] = unquote(hls_match.group(1))
        
        if not links:
            raise ValueError("No video links found in page")
        
        return title, links
    
    def _select_quality(self, links: Dict[str, str], quality: str) -> tuple:
        
        if quality == 'best':
            if 'HLS (Adaptive)' in links:
                return 'HLS', links['HLS (Adaptive)']
            elif 'High Quality' in links:
                return 'High', links['High Quality']
            else:
                return list(links.keys())[0], list(links.values())[0]
        
        elif quality == 'worst':
            if 'Low Quality' in links:
                return 'Low', links['Low Quality']
            else:
                return list(links.keys())[-1], list(links.values())[-1]
        
        else:
            try:
                req_q = int(quality)
                if req_q >= 720 and 'High Quality' in links:
                    return 'High', links['High Quality']
                elif req_q < 720 and 'Low Quality' in links:
                    return 'Low', links['Low Quality']
                elif 'HLS (Adaptive)' in links:
                    return 'HLS', links['HLS (Adaptive)']
            except ValueError:
                pass
            
            return list(links.keys())[0], list(links.values())[0]
    
    def _download_hls_ffmpeg(self, url: str, filename: str):
        
        if not shutil.which("ffmpeg"):
            raise RuntimeError("FFmpeg is required for HLS downloads. Please install FFmpeg.")
        
        if not filename.endswith(".mp4"):
            filename = filename.replace(".ts", ".mp4")
        
        cmd = ['ffmpeg', '-y', '-i', url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', filename]
        subprocess.run(cmd, check=True, capture_output=True)
    
    def _download_with_progress(
        self,
        url: str,
        filename: str,
        on_progress: Optional[Callable[[int, int], None]] = None
    ):
        
        try:
            head = self.session.head(url, allow_redirects=True)
            file_size = int(head.headers.get('content-length', 0))
        except:
            file_size = 0
        
        if file_size == 0:
            self._download_single(url, filename)
            return
        
        num_threads = 8
        with open(filename, 'wb') as f:
            f.truncate(file_size)
        
        chunk_size = file_size // num_threads
        ranges = [
            (i * chunk_size, (i + 1) * chunk_size - 1 if i < num_threads - 1 else file_size - 1)
            for i in range(num_threads)
        ]
        
        completed = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(self._download_chunk, url, filename, start, end)
                for start, end in ranges
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    written = future.result()
                    completed += written
                    if on_progress:
                        on_progress(completed, file_size)
                except Exception:
                    pass
    
    def _download_chunk(self, url: str, filename: str, start: int, end: int) -> int:
        
        headers = self.session.headers.copy()
        headers['Range'] = f'bytes={start}-{end}'
        
        response = self.session.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'r+b') as f:
            f.seek(start)
            written = 0
            for chunk in response.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    written += len(chunk)
        
        return written
    
    def _download_single(self, url: str, filename: str):
        
        with self.session.get(url, stream=True) as response:
            response.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)
    
    def _sanitize_filename(self, title: str) -> str:
        
        cleaned = re.sub(r'[\\/*?:"<>|]', "", title)
        cleaned = " ".join(cleaned.split())
        return cleaned[:200] if cleaned else f"video_{int(time.time())}"
    
    def _extract_video_id(self, url: str) -> str:
        
        match = re.search(r'/video-([a-z0-9]+)/', url)
        if match:
            return match.group(1)
        return "unknown"


class XNXXSearch(BaseSiteSearch):
    
    def __init__(self):
        self.base_url = "https://www.xnxx.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def search(
        self,
        query: str,
        page: int = 1,
        sort_by: str = "relevance",
        duration: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        
        try:
            search_url = f"{self.base_url}/search/{query.replace(' ', '+')}"
            
            if page > 1:
                search_url += f"/{page-1}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            video_items = soup.find_all('div', class_='thumb-block')
            
            for item in video_items[:20]:
                try:
                    link_elem = item.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    video_url = link_elem['href']
                    if not video_url.startswith('http'):
                        video_url = self.base_url + video_url
                    
                    title = link_elem.get('title', '').strip()
                    if not title:
                        title_elem = item.find('p', class_='title')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                    if not title:
                        url_match = re.search(r'/video-[^/]+/(.+)$', video_url)
                        if url_match:
                            title = url_match.group(1).replace('_', ' ').replace('-', ' ')
                    
                    thumb_elem = item.find('img')
                    thumbnail = ''
                    if thumb_elem:
                        thumbnail = thumb_elem.get('data-src') or thumb_elem.get('src') or ''
                    
                    duration_elem = item.find('span', class_='duration')
                    duration_str = duration_elem.text.strip() if duration_elem else ''
                    
                    results.append({
                        "title": title,
                        "url": video_url,
                        "duration": duration_str,
                        "thumbnail": thumbnail,
                        "site": "xnxx"
                    })
                except Exception:
                    continue
            
            return results
            
        except Exception:
            return []
    
    @staticmethod
    def get_site_name() -> str:
        
        return "xnxx"
    
    def get_search_filters(self) -> Dict[str, List[str]]:
        
        return {
            "sort_by": ["relevance", "rating", "length", "views", "date"],
            "duration": []
        }
