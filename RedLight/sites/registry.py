"""
Site Registry - Manages all supported sites and provides auto-detection.
"""

from typing import Dict, List, Optional, Type
from .base import BaseSiteDownloader, BaseSiteSearch
from .pornhub import PornHubDownloader, PornHubSearch
from .eporner import EpornerDownloader, EpornerSearch
from .spankbang import SpankBangDownloader, SpankBangSearch
from .xvideos import XVideosDownloader, XVideosSearch


class SiteRegistry:
    """
    Singleton registry for managing all supported adult content sites.
    
    Provides site detection, downloader selection, and search management.
    """
    
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
        return cls._instance
    
    def register_site(
        self,
        name: str,
        downloader_class: Type[BaseSiteDownloader],
        search_class: Type[BaseSiteSearch]
    ) -> None:
        """Register a new site with its downloader and search classes."""
        self._sites[name.lower()] = {
            "name": name.lower(),
            "downloader": downloader_class,
            "search": search_class
        }
    
    def get_downloader_for_url(self, url: str) -> Optional[BaseSiteDownloader]:
        """Auto-detect site from URL and return appropriate downloader instance."""
        for site_info in self._sites.values():
            downloader_class = site_info["downloader"]
            if downloader_class.is_supported_url(url):
                return downloader_class()
        return None
    
    def get_downloader_by_name(self, site_name: str) -> Optional[BaseSiteDownloader]:
        """Get downloader instance by site name."""
        site_info = self._sites.get(site_name.lower())
        if site_info:
            return site_info["downloader"]()
        return None
    
    def get_search_by_name(self, site_name: str) -> Optional[BaseSiteSearch]:
        """Get search instance by site name."""
        site_info = self._sites.get(site_name.lower())
        if site_info:
            return site_info["search"]()
        return None
    
    def get_all_sites(self) -> List[Dict[str, str]]:
        """Get list of all registered sites."""
        sites = []
        for name, info in self._sites.items():
            sites.append({
                "name": name,
                "display_name": name.title()
            })
        return sorted(sites, key=lambda x: x["name"])
    
    def get_all_searchers(self) -> Dict[str, BaseSiteSearch]:
        """Get all search instances for searching across all sites."""
        return {
            name: info["search"]()
            for name, info in self._sites.items()
        }
    
    def detect_site(self, url: str) -> Optional[str]:
        """Detect site name from URL."""
        for site_info in self._sites.values():
            downloader_class = site_info["downloader"]
            if downloader_class.is_supported_url(url):
                return site_info["name"]
        return None
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is supported by any registered site."""
        return self.detect_site(url) is not None
    
    @property
    def site_count(self) -> int:
        """Get number of registered sites."""
        return len(self._sites)
