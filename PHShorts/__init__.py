"""
PH Shorts Downloader - Download Shorts from PornHub with ease!

A lightweight and powerful alternative to yt-dlp for PornHub Shorts.
Now with programmable API support for building custom scripts and bots!
"""

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

__version__ = "1.0.7"
__author__ = "PH Shorts DL Team"
__description__ = "Download PornHub Shorts videos with a beautiful CLI interface"

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
    # Metadata
    "MetadataEditor",
    # Async API
    "AsyncVideoDownloader",
    # Advanced
    "CustomHLSDownloader",
]





