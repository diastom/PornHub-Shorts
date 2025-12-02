# Core downloader class (for advanced usage)
from .downloader import CustomHLSDownloader

# High-level API (recommended for most users)
from .api import VideoDownloader, DownloadVideo, GetVideoInfo, ListAvailableQualities

# Batch downloads
from .batch import BatchDownloader

# Format conversion
from .converter import VideoConverter

# Playlist/Channel
from .playlist import PlaylistDownloader

# Metadata
from .metadata import MetadataEditor

# Search
from .search import PornHubSearch

# Async API (for bots and async applications)
from .async_downloader import AsyncVideoDownloader

from .sites import SiteRegistry
from .sites.pornhub import PornHubDownloader
from .sites.eporner import EpornerDownloader, EpornerSearch
from .sites.spankbang import SpankBangDownloader, SpankBangSearch
from .sites.xvideos import XVideosDownloader, XVideosSearch
from .multi_search import MultiSiteSearch

from .version import __version__, __author__, __description__

__all__ = [
    # Main API
    "VideoDownloader",
    "DownloadVideo",
    "GetVideoInfo",
    "ListAvailableQualities",
    # Batch
    "BatchDownloader",
    # Conversion
    "VideoConverter",
    # Playlist
    "PlaylistDownloader",
    # Search
    "PornHubSearch",
    "MultiSiteSearch",
    # Metadata
    "MetadataEditor",
    # Async API
    "AsyncVideoDownloader",
    # Advanced
    "CustomHLSDownloader",
    "SiteRegistry",
    "EpornerDownloader",
    "EpornerSearch",
    "PornHubDownloader",
    "SpankBangDownloader",
    "SpankBangSearch",
    "XVideosDownloader",
    "XVideosSearch",
]





