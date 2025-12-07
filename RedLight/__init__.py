# Core downloader class (for advanced usage)
from .downloader import CustomHLSDownloader

# High-level API (recommended for most users)
from .api import (
    VideoDownloader,
    DownloadVideo,
    GetVideoInfo,
    ListAvailableQualities,
    # Resume/Pause (NEW in v1.0.14)
    StartResumableDownload,
    PauseDownload,
    ResumeDownload,
    CancelDownload,
    GetActiveDownloads,
    GetPausedDownloads,
    # History (NEW in v1.0.14)
    GetDownloadHistory,
    ClearDownloadHistory,
    ExportHistory,
    # Statistics (NEW in v1.0.14)
    GetStatistics,
    GetStatsBySite,
    GetStatsByQuality,
    GetStatsByDate,
    # Notifications (NEW in v1.0.14)
    EnableNotifications,
    SetNotificationSound,
    SendNotification,
)

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

# Resume Manager (NEW in v1.0.14)
from .resume_manager import ResumeManager, DownloadState, GetResumeManager

# Notifications (NEW in v1.0.14)
from .notifications import NotificationManager, GetNotifier

# Statistics (NEW in v1.0.14)
from .statistics import DownloadStatistics, GetStatistics

# Database
from .database import DatabaseManager

# Configuration (NEW in v1.0.14)
from .config import (
    Config,
    ConfigManager,
    GetConfig,
    SaveConfig,
    ResetConfig,
    CreateDefaultConfig
)

# Retry with exponential backoff (NEW in v1.0.14)
from .retry import smart_retry, RetryHandler, retry_with_backoff

# Fast downloads with aria2c (NEW in v1.0.14)
from .aria2_downloader import (
    Aria2cDownloader,
    PythonDownloader,
    IsAria2cAvailable,
    get_fast_downloader
)

# Progress bar utilities (NEW in v1.0.14)
from .progress_bar import (
    ProgressCallback,
    EnhancedProgress,
    create_download_progress,
    format_speed,
    format_eta,
    format_size
)

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
    # Resume/Pause (NEW in v1.0.14)
    "StartResumableDownload",
    "PauseDownload",
    "ResumeDownload",
    "CancelDownload",
    "GetActiveDownloads",
    "GetPausedDownloads",
    "ResumeManager",
    "DownloadState",
    # History (NEW in v1.0.14)
    "GetDownloadHistory",
    "ClearDownloadHistory",
    "ExportHistory",
    "DatabaseManager",
    # Statistics (NEW in v1.0.14)
    "GetStatistics",
    "GetStatsBySite",
    "GetStatsByQuality",
    "GetStatsByDate",
    "DownloadStatistics",
    # Notifications (NEW in v1.0.14)
    "EnableNotifications",
    "SetNotificationSound",
    "SendNotification",
    "NotificationManager",
    # Configuration (NEW in v1.0.14)
    "Config",
    "ConfigManager",
    "GetConfig",
    "SaveConfig",
    "ResetConfig",
    "CreateDefaultConfig",
    # Retry (NEW in v1.0.14)
    "smart_retry",
    "RetryHandler",
    "retry_with_backoff",
    # Aria2c (NEW in v1.0.14)
    "Aria2cDownloader",
    "PythonDownloader",
    "IsAria2cAvailable",
    "get_fast_downloader",
    # Progress Bar (NEW in v1.0.14)
    "ProgressCallback",
    "EnhancedProgress",
    "create_download_progress",
    "format_speed",
    "format_eta",
    "format_size",
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


