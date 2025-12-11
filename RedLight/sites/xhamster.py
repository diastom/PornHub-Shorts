import re
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .base import BaseSiteDownloader, BaseSiteSearch
from ..downloader import CustomHLSDownloader


class XHamsterDownloader(BaseSiteDownloader):
    
    FALLBACK_DOMAINS = ['xhamster2.com', 'xhamster.desi', 'xhamster3.com']
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://xhamster.com',
            'Referer': 'https://xhamster.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
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
        
        title, hls_url = self._extract_info(url)
        
        output_file = None
        if filename:
            output_file = output_path / filename
        else:
            safe_title = self._sanitize_filename(title)
            output_file = output_path / f"{safe_title}.ts"
        
        downloader = CustomHLSDownloader(
            output_name=str(output_file),
            headers=self.headers,
            keep_ts=keep_original,
            proxy=proxy,
            progress_callback=on_progress
        )
        
        result_path = downloader.download_stream(hls_url, preferred_quality=quality)
        
        return str(result_path)
    
    def get_info(self, url: str) -> Dict[str, Any]:
        
        title, hls_url = self._extract_info(url)
        
        available_qualities = self._get_qualities_from_master(hls_url)
        
        video_id = self._extract_video_id(url)
        
        return {
            "title": title,
            "available_qualities": available_qualities,
            "video_id": video_id,
            "site": "xhamster"
        }
    
    def list_qualities(self, url: str) -> List[int]:
        
        info = self.get_info(url)
        return info["available_qualities"]
    
    @staticmethod
    def is_supported_url(url: str) -> bool:
        
        url_lower = url.lower()
        return any(domain in url_lower for domain in ['xhamster.com', 'xhamster2.com', 'xhamster3.com', 'xhamster.desi'])
    
    @staticmethod
    def get_site_name() -> str:
        
        return "xhamster"
    
    def _extract_info(self, url: str) -> tuple:
        
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        
        if '"sources"' in response.text or '"h264"' in response.text:
            return self._parse_html(response.text, url)
        
        video_path = re.search(r'xhamster\d?\.(?:com|desi)(/videos/[^\s?#]+)', url)
        if not video_path:
            raise RuntimeError("Invalid xHamster URL format")
        
        for fallback_domain in self.FALLBACK_DOMAINS:
            fallback_url = f'https://{fallback_domain}{video_path.group(1)}'
            try:
                response = self.session.get(fallback_url, timeout=15)
                response.raise_for_status()
                
                if '"sources"' in response.text or '"h264"' in response.text:
                    return self._parse_html(response.text, fallback_url)
            except Exception:
                continue
        
        raise RuntimeError("Failed to extract video info: geo-blocked or unavailable")
    
    def _parse_html(self, content: str, url: str) -> tuple:
        
        title = "xhamster_video"
        hls_url = None
        
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
        if not title_match:
            title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            raw_title = title_match.group(1)
            title = re.sub(r'\s*[-|]?\s*xHamster.*$', '', raw_title, flags=re.IGNORECASE).strip()
            title = re.sub(r'[\\/*?:"<>|]', "", title)
            if not title:
                title = "xhamster_video"
        
        h264_match = re.search(r'"h264"\s*:\s*\[\s*\{\s*"url"\s*:\s*"([^"]+)"', content)
        if h264_match:
            hls_url = h264_match.group(1).replace('\\/', '/')
        else:
            av1_match = re.search(r'"av1"\s*:\s*\[\s*\{\s*"url"\s*:\s*"([^"]+)"', content)
            if av1_match:
                hls_url = av1_match.group(1).replace('\\/', '/')
        
        if not hls_url:
            m3u8_match = re.search(r'"(https://[^"]+\.m3u8[^"]*)"', content)
            if m3u8_match:
                hls_url = m3u8_match.group(1).replace('\\/', '/')
                        
        if not hls_url:
            raise ValueError("No HLS stream found on page")
        
        return title, hls_url
    
    def _get_qualities_from_master(self, hls_url: str) -> List[int]:
        
        quality_info = re.search(r'multi=([^/]+)', hls_url)
        if quality_info:
            qualities_str = quality_info.group(1)
            quality_matches = re.findall(r':(\d{3,4})p', qualities_str)
            if quality_matches:
                return sorted([int(q) for q in quality_matches], reverse=True)
        
        try:
            response = self.session.get(hls_url, timeout=10)
            response.raise_for_status()
            
            qualities = []
            for line in response.text.splitlines():
                if line.startswith("#EXT-X-STREAM-INF"):
                    res_match = re.search(r'RESOLUTION=\d+x(\d+)', line)
                    if res_match:
                        qualities.append(int(res_match.group(1)))
            
            if qualities:
                return sorted(set(qualities), reverse=True)
        except Exception:
            pass
        
        return [1080, 720, 480, 240, 144]
    
    def _sanitize_filename(self, title: str) -> str:
        
        cleaned = re.sub(r'[\\/*?:"<>|]', "", title)
        cleaned = " ".join(cleaned.split())
        return cleaned[:200] if cleaned else f"video_{int(time.time())}"
    
    def _extract_video_id(self, url: str) -> str:
        
        match = re.search(r'/videos/([^/]+)', url)
        if match:
            return match.group(1)
        return "unknown"


class XHamsterSearch(BaseSiteSearch):
    
    def __init__(self):
        self.base_url = "https://xhamster2.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
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
            search_query = query.replace(' ', '+')
            search_url = f"{self.base_url}/search/{search_query}"
            
            if page > 1:
                search_url += f"?page={page}"
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            video_items = soup.select('div.thumb-list__item, article.thumb-list__item')
            
            if not video_items:
                video_items = soup.select('[data-video-id], .video-thumb')
            
            for item in video_items[:30]:
                try:
                    link_elem = item.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    video_url = link_elem['href']
                    if not video_url.startswith('http'):
                        video_url = urljoin(self.base_url, video_url)
                    
                    if '/videos/' not in video_url:
                        continue
                    
                    title = link_elem.get('title', '')
                    if not title:
                        title_elem = item.select_one('.video-thumb-info__name, .thumb-image-container__title')
                        title = title_elem.text.strip() if title_elem else ''
                    
                    if not title:
                        img_elem = item.find('img')
                        title = img_elem.get('alt', '') if img_elem else 'Unknown'
                    
                    thumb_elem = item.find('img')
                    thumbnail = ''
                    if thumb_elem:
                        thumbnail = thumb_elem.get('src') or thumb_elem.get('data-src') or ''
                    
                    duration_elem = item.select_one('.thumb-image-container__duration, .duration')
                    duration_str = duration_elem.text.strip() if duration_elem else ''
                    
                    views_elem = item.select_one('.video-thumb-info__views, .views')
                    views_str = views_elem.text.strip() if views_elem else ''
                    
                    results.append({
                        "title": title.strip(),
                        "url": video_url,
                        "duration": duration_str,
                        "views": views_str,
                        "thumbnail": thumbnail,
                        "site": "xhamster"
                    })
                except Exception:
                    continue
            
            return results
            
        except Exception:
            return []
    
    @staticmethod
    def get_site_name() -> str:
        
        return "xhamster"
    
    def get_search_filters(self) -> Dict[str, List[str]]:
        
        return {
            "sort_by": ["relevance", "newest", "views", "rating"],
            "duration": ["short", "medium", "long"]
        }
