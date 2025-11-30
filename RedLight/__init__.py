"""
RedLight DL - Professional Adult Content Downloader

A powerful and feature-rich downloader for adult content.
Includes programmable API support for building custom scripts and bots!
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

# Multi-site support
from .sites import SiteRegistry
from .sites.pornhub import PornHubDownloader
from .sites.eporner import EpornerDownloader, EpornerSearch
from .multi_search import MultiSiteSearch

__version__ = "1.0.11"
__author__ = "RedLight Team"
__description__ = "RedLight DL - Professional adult content downloader with CLI & API"

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
    # Multi-site support
    "SiteRegistry",
    "EpornerDownloader",
    "EpornerSearch",
    "PornHubDownloader",
]





