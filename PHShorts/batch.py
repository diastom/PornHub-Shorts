"""
Batch Download Module - Download multiple videos efficiently.

This module provides batch downloading capabilities with support for
concurrent or sequential downloads, progress tracking, and error handling.
"""

from typing import List, Dict, Optional, Callable
from pathlib import Path
import concurrent.futures
from .api import DownloadVideo


class BatchDownloader:
    """
    Download multiple videos in batch mode.
    
    Supports both concurrent (parallel) and sequential downloads with
    comprehensive progress tracking and error handling.
    
    Example:
        >>> from PHShorts import BatchDownloader
        >>> 
        >>> downloader = BatchDownloader(concurrent=True, max_workers=3)
        >>> downloader.AddUrls(["url1", "url2", "url3"])
        >>> results = downloader.DownloadAll()
        >>> print(f"Downloaded {len(results)} videos")
    """
    
    def __init__(
        self,
        output_dir: str = "./downloads",
        concurrent: bool = False,
        max_workers: int = 3,
        quality: str = "best",
        keep_ts: bool = False
    ):
        """
        Initialize BatchDownloader.
        
        Args:
            output_dir: Directory to save downloaded videos
            concurrent: If True, download videos simultaneously; if False, one-by-one
            max_workers: Maximum number of concurrent downloads (only if concurrent=True)
            quality: Default quality for all downloads
            keep_ts: If True, keep original .ts file (skips MP4 conversion)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.concurrent = concurrent
        self.max_workers = max_workers
        self.quality = quality
        self.keep_ts = keep_ts
        self.urls: List[str] = []
        
    def AddUrls(self, urls: List[str]) -> None:
        """
        Add URLs to the download queue.
        
        Args:
            urls: List of video URLs to download
        """
        self.urls.extend(urls)
    
    def AddUrl(self, url: str) -> None:
        """
        Add a single URL to the download queue.
        
        Args:
            url: Video URL to download
        """
        self.urls.append(url)
    
    def ClearQueue(self) -> None:
        """Clear all URLs from the download queue."""
        self.urls.clear()
    
    def DownloadAll(
        self,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_complete: Optional[Callable[[str, str], None]] = None,
        on_error: Optional[Callable[[str, Exception], None]] = None
    ) -> Dict[str, str]:
        """
        Download all queued videos.
        
        Args:
            on_progress: Callback(completed, total, current_url) called after each video
            on_complete: Callback(url, path) called when a video downloads successfully
            on_error: Callback(url, exception) called when a download fails
        
        Returns:
            Dictionary mapping successful URLs to their file paths
            
        Example:
            >>> def progress(completed, total, url):
            ...     print(f"[{completed}/{total}] Downloading: {url}")
            >>> 
            >>> results = downloader.DownloadAll(on_progress=progress)
        """
        if not self.urls:
            return {}
        
        results = {}
        errors = {}
        
        if self.concurrent:
            # Concurrent downloads
            results, errors = self._download_concurrent(on_progress, on_complete, on_error)
        else:
            # Sequential downloads
            results, errors = self._download_sequential(on_progress, on_complete, on_error)
        
        return results
    
    def _download_sequential(
        self,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> tuple[Dict[str, str], Dict[str, Exception]]:
        """Download videos one by one."""
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
        """Download videos in parallel."""
        results = {}
        errors = {}
        total = len(self.urls)
        completed = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all downloads
            future_to_url = {
                executor.submit(self._download_single, url): url
                for url in self.urls
            }
            
            # Process completed downloads
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
        """Download a single video (used by concurrent downloader)."""
        return DownloadVideo(
            url=url,
            output_dir=str(self.output_dir),
            quality=self.quality,
            keep_ts=self.keep_ts
        )
    
    @property
    def QueueSize(self) -> int:
        """Get the number of URLs in the queue."""
        return len(self.urls)
