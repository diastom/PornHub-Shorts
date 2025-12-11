from typing import List, Dict, Optional, Callable
from pathlib import Path
import concurrent.futures
from .api import DownloadVideo


class BatchDownloader:
    
    def __init__(
        self,
        output_dir: str = "./downloads",
        concurrent: bool = False,
        max_workers: int = 3,
        quality: str = "best",
        keep_ts: bool = False
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.concurrent = concurrent
        self.max_workers = max_workers
        self.quality = quality
        self.keep_ts = keep_ts
        self.urls: List[str] = []
        
    def AddUrls(self, urls: List[str]) -> None:
        self.urls.extend(urls)
    
    def AddUrl(self, url: str) -> None:
        self.urls.append(url)
    
    def ClearQueue(self) -> None:
        self.urls.clear()
    
    def DownloadAll(
        self,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_complete: Optional[Callable[[str, str], None]] = None,
        on_error: Optional[Callable[[str, Exception], None]] = None
    ) -> Dict[str, str]:
        if not self.urls:
            return {}
        
        results = {}
        errors = {}
        
        if self.concurrent:
            results, errors = self._download_concurrent(on_progress, on_complete, on_error)
        else:
            results, errors = self._download_sequential(on_progress, on_complete, on_error)
        
        return results
    
    def _download_sequential(
        self,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> tuple[Dict[str, str], Dict[str, Exception]]:
        results = {}
        errors = {}
        total = len(self.urls)
        
        for idx, url in enumerate(self.urls, 1):
            try:
                if on_progress:
                    on_progress(idx - 1, total, url)
                
                video_path = DownloadVideo(
                    url=url,
                    output_dir=str(self.output_dir),
                    quality=self.quality,
                    keep_ts=self.keep_ts
                )
                
                results[url] = video_path
                
                if on_complete:
                    on_complete(url, video_path)
                    
            except Exception as e:
                errors[url] = e
                if on_error:
                    on_error(url, e)
        
        return results, errors
    
    def _download_concurrent(
        self,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> tuple[Dict[str, str], Dict[str, Exception]]:
        results = {}
        errors = {}
        total = len(self.urls)
        completed = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self._download_single, url): url
                for url in self.urls
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                completed += 1
                
                try:
                    video_path = future.result()
                    results[url] = video_path
                    
                    if on_progress:
                        on_progress(completed, total, url)
                    
                    if on_complete:
                        on_complete(url, video_path)
                        
                except Exception as e:
                    errors[url] = e
                    
                    if on_progress:
                        on_progress(completed, total, url)
                    
                    if on_error:
                        on_error(url, e)
        
        return results, errors
    
    def _download_single(self, url: str) -> str:
        return DownloadVideo(
            url=url,
            output_dir=str(self.output_dir),
            quality=self.quality,
            keep_ts=self.keep_ts
        )
    
    @property
    def QueueSize(self) -> int:
        return len(self.urls)
