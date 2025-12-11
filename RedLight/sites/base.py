from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any


class BaseSiteDownloader(ABC):
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_info(self, url: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def list_qualities(self, url: str) -> List[int]:
        pass
    
    @staticmethod
    @abstractmethod
    def is_supported_url(url: str) -> bool:
        pass
    
    @staticmethod
    @abstractmethod
    def get_site_name() -> str:
        pass


class BaseSiteSearch(ABC):
    
    @abstractmethod
    def search(
        self,
        query: str,
        page: int = 1,
        sort_by: str = "relevance",
        duration: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        pass
    
    @staticmethod
    @abstractmethod
    def get_site_name() -> str:
        pass
    
    @abstractmethod
    def get_search_filters(self) -> Dict[str, List[str]]:
        pass
