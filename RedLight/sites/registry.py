from typing import Dict, List, Optional, Type
from .base import BaseSiteDownloader, BaseSiteSearch
from .pornhub import PornHubDownloader, PornHubSearch
from .eporner import EpornerDownloader, EpornerSearch
from .spankbang import SpankBangDownloader, SpankBangSearch
from .xvideos import XVideosDownloader, XVideosSearch
from .xhamster import XHamsterDownloader, XHamsterSearch
from .xnxx import XNXXDownloader, XNXXSearch


class SiteRegistry:
    
    _instance = None
    _sites: Dict[str, Dict] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SiteRegistry, cls).__new__(cls)
            cls._instance._sites = {}
            cls._instance.register_site("pornhub", PornHubDownloader, PornHubSearch)
            cls._instance.register_site("eporner", EpornerDownloader, EpornerSearch)
            cls._instance.register_site("spankbang", SpankBangDownloader, SpankBangSearch)
            cls._instance.register_site("xvideos", XVideosDownloader, XVideosSearch)
            cls._instance.register_site("xhamster", XHamsterDownloader, XHamsterSearch)
            cls._instance.register_site("xnxx", XNXXDownloader, XNXXSearch)
        return cls._instance
    
    def register_site(
        self,
        name: str,
        downloader_class: Type[BaseSiteDownloader],
        search_class: Type[BaseSiteSearch]
    ) -> None:
        self._sites[name.lower()] = {
            "name": name.lower(),
            "downloader": downloader_class,
            "search": search_class
        }
    
    def get_downloader_for_url(self, url: str) -> Optional[BaseSiteDownloader]:
        for site_info in self._sites.values():
            downloader_class = site_info["downloader"]
            if downloader_class.is_supported_url(url):
                return downloader_class()
        return None
    
    def get_downloader_by_name(self, site_name: str) -> Optional[BaseSiteDownloader]:
        site_info = self._sites.get(site_name.lower())
        if site_info:
            return site_info["downloader"]()
        return None
    
    def get_search_by_name(self, site_name: str) -> Optional[BaseSiteSearch]:
        site_info = self._sites.get(site_name.lower())
        if site_info:
            return site_info["search"]()
        return None
    
    def get_all_sites(self) -> List[Dict[str, str]]:
        sites = []
        for name, info in self._sites.items():
            sites.append({
                "name": name,
                "display_name": name.title()
            })
        return sorted(sites, key=lambda x: x["name"])
    
    def get_all_searchers(self) -> Dict[str, BaseSiteSearch]:
        return {
            name: info["search"]()
            for name, info in self._sites.items()
        }
    
    def detect_site(self, url: str) -> Optional[str]:
        for site_info in self._sites.values():
            downloader_class = site_info["downloader"]
            if downloader_class.is_supported_url(url):
                return site_info["name"]
        return None
    
    def is_supported_url(self, url: str) -> bool:
        return self.detect_site(url) is not None
    
    @property
    def site_count(self) -> int:
        return len(self._sites)
