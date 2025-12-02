"""
RedLight Sites Module - Multi-site support infrastructure.

This module provides the base architecture for supporting multiple adult content sites.
"""

from .base import BaseSiteDownloader, BaseSiteSearch
from .registry import SiteRegistry

# Import site implementations
from .pornhub import PornHubDownloader, PornHubSearch
from .eporner import EpornerDownloader, EpornerSearch
from .spankbang import SpankBangDownloader, SpankBangSearch
from .xvideos import XVideosDownloader, XVideosSearch

_registry = SiteRegistry()

_registry.register_site(
    name="pornhub",
    downloader_class=PornHubDownloader,
    search_class=PornHubSearch
)

_registry.register_site(
    name="eporner",
    downloader_class=EpornerDownloader,
    search_class=EpornerSearch
)

_registry.register_site(
    name="spankbang",
    downloader_class=SpankBangDownloader,
    search_class=SpankBangSearch
)

_registry.register_site(
    name="xvideos",
    downloader_class=XVideosDownloader,
    search_class=XVideosSearch
)

__all__ = [
    "BaseSiteDownloader",
    "BaseSiteSearch",
    "SiteRegistry",
    "PornHubDownloader",
    "PornHubSearch",
    "EpornerDownloader",
    "EpornerSearch",
    "SpankBangDownloader",
    "SpankBangSearch",
    "XVideosDownloader",
    "XVideosSearch",
]
