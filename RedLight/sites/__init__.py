from .base import BaseSiteDownloader, BaseSiteSearch
from .registry import SiteRegistry

from .pornhub import PornHubDownloader, PornHubSearch
from .eporner import EpornerDownloader, EpornerSearch
from .spankbang import SpankBangDownloader, SpankBangSearch
from .xvideos import XVideosDownloader, XVideosSearch
from .xhamster import XHamsterDownloader, XHamsterSearch
from .xnxx import XNXXDownloader, XNXXSearch

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

_registry.register_site(
    name="xhamster",
    downloader_class=XHamsterDownloader,
    search_class=XHamsterSearch
)

_registry.register_site(
    name="xnxx",
    downloader_class=XNXXDownloader,
    search_class=XNXXSearch
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
    "XHamsterDownloader",
    "XHamsterSearch",
    "XNXXDownloader",
    "XNXXSearch",
]
