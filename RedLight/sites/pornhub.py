from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

from .base import BaseSiteDownloader, BaseSiteSearch
from ..downloader import CustomHLSDownloader
from ..search import PornHubSearch as OriginalPornHubSearch


class PornHubDownloader(BaseSiteDownloader):
    
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
        
        output_file = None
        if filename:
            output_file = output_path / filename
        
        downloader = CustomHLSDownloader(
            output_name=str(output_file) if output_file else None,
            keep_ts=keep_original,
            proxy=proxy,
            progress_callback=on_progress
        )
        
        streams = downloader.extract_video_info(url)
        
        if not output_file and downloader.output_name:
            final_output = output_path / downloader.output_name.name
            downloader.output_name = final_output
        
        if isinstance(streams, dict):
            quality_keys = sorted([k for k in streams.keys() if isinstance(k, int)], reverse=True)
            if quality_keys:
                m3u8_url = streams[quality_keys[0]]
            else:
                m3u8_url = list(streams.values())[0]
        else:
            m3u8_url = streams
        
        result_path = downloader.download_stream(m3u8_url, preferred_quality=quality)
        
        return str(result_path)
    
    def get_info(self, url: str) -> Dict[str, Any]:

        downloader = CustomHLSDownloader()
        
        streams = downloader.extract_video_info(url)
        
        video_id = downloader.extract_video_id(url)
        
        title = downloader.output_name.stem if downloader.output_name else "Unknown"
        
        available_qualities = []
        if isinstance(streams, dict):
            available_qualities = sorted([k for k in streams.keys() if isinstance(k, int)], reverse=True)
        
        return {
            "title": title,
            "available_qualities": available_qualities,
            "video_id": video_id,
            "site": "pornhub"
        }
    
    def list_qualities(self, url: str) -> List[int]:

        info = self.get_info(url)
        return info["available_qualities"]
    
    @staticmethod
    def is_supported_url(url: str) -> bool:

        url_lower = url.lower()
        return "pornhub.com" in url_lower or "pornhubpremium.com" in url_lower
    
    @staticmethod
    def get_site_name() -> str:

        return "pornhub"


class PornHubSearch(BaseSiteSearch):
    
    def __init__(self):
        self.searcher = OriginalPornHubSearch()
    
    def search(
        self,
        query: str,
        page: int = 1,
        sort_by: str = "mostviewed",
        duration: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:

        try:
            results = self.searcher.search(query, page=page, sort_by=sort_by, duration=duration)
            
            for result in results:
                result["site"] = "pornhub"
            
            return results
        except Exception:
            return []
    
    @staticmethod
    def get_site_name() -> str:

        return "pornhub"
    
    def get_search_filters(self) -> Dict[str, List[str]]:

        return {
            "sort_by": ["mostviewed", "toprated", "newest"],
            "duration": ["short", "medium", "long"]
        }
