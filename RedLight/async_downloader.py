import asyncio
from pathlib import Path
from typing import Optional, Callable, Dict, List, Union, Any
from concurrent.futures import ThreadPoolExecutor
from .sites import SiteRegistry


class AsyncVideoDownloader:
    
    def __init__(
        self,
        output_dir: str = "./downloads",
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        max_workers: int = 2
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.proxy = proxy
        self.headers = headers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
    
    async def download(
        self,
        url: str,
        quality: str = "best",
        filename: Optional[str] = None,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> str:
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            self.executor,
            self._sync_download,
            url,
            quality,
            filename,
            on_progress
        )
        
        return result
    
    def _sync_download(
        self,
        url: str,
        quality: str,
        filename: Optional[str],
        on_progress: Optional[Callable]
    ) -> str:
        registry = SiteRegistry()
        downloader = registry.get_downloader_for_url(url)
        
        if not downloader:
            raise ValueError(f"Unsupported URL: {url}")
        
        return downloader.download(
            url=url,
            quality=quality,
            output_dir=str(self.output_dir),
            filename=filename,
            keep_original=False,
            proxy=self.proxy,
            on_progress=on_progress
        )
    
    async def get_info(self, url: str) -> Dict[str, Union[str, List[int]]]:
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            self.executor,
            self._sync_get_info,
            url
        )
        
        return result
    
    def _sync_get_info(self, url: str) -> Dict:
        registry = SiteRegistry()
        downloader = registry.get_downloader_for_url(url)
        
        if not downloader:
            raise ValueError(f"Unsupported URL: {url}")
        
        return downloader.get_info(url)
    
    async def list_qualities(self, url: str) -> List[int]:
        info = await self.get_info(url)
        return info["available_qualities"]
    
    def shutdown(self):
        self.executor.shutdown(wait=True)
