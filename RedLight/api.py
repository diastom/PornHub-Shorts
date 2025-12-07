"""
RedLight API - Simple helper functions for quick usage.

This module provides high-level functions for downloading videos
and extracting metadata without dealing with classes directly.
Supports multiple adult content sites with automatic detection.

v1.0.14: Added Resume/Pause, Download History, Statistics, and Notifications APIs.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, List, Union, Any
from .downloader import CustomHLSDownloader
from .sites import SiteRegistry
from .resume_manager import GetResumeManager
from .database import DatabaseManager
from .statistics import GetStatistics
from .notifications import GetNotifier


# =============================================================================
# Core Download Functions
# =============================================================================

def DownloadVideo(
    url: str,
    output_dir: str = "./downloads",
    quality: str = "best",
    filename: Optional[str] = None,
    keep_ts: bool = False,
    proxy: Optional[str] = None,
    on_progress: Optional[Callable[[int, int], None]] = None
) -> str:
    """
    Download a video from any supported site (auto-detected).
    
    Args:
        url: Video URL from any supported site
        output_dir: Directory to save the video (default: "./downloads")
        quality: Video quality - "best", "worst", or specific height like "720"
        filename: Custom filename (optional, auto-detected from video title if not provided)
        keep_ts: If True, keep original file (for HLS: .ts, for MP4: original format)
        proxy: HTTP/HTTPS proxy (optional)
        on_progress: Callback function (downloaded, total) for progress tracking
    
    Returns:
        Path to the downloaded video file
        
    Raises:
        ValueError: If URL is from an unsupported site
        
    Example:
        >>> from RedLight import DownloadVideo
        >>> # Works with PornHub
        >>> video_path = DownloadVideo("https://pornhub.com/...")
        >>> # Also works with Eporner
        >>> video_path = DownloadVideo("https://eporner.com/...")
    """
    # Get appropriate downloader for the URL
    registry = SiteRegistry()
    downloader = registry.get_downloader_for_url(url)
    
    if not downloader:
        raise ValueError(f"Unsupported URL. Supported sites: {', '.join([s['name'] for s in registry.get_all_sites()])}")
    
    # Download using site-specific downloader
    return downloader.download(
        url=url,
        quality=quality,
        output_dir=output_dir,
        filename=filename,
        keep_original=keep_ts,
        proxy=proxy,
        on_progress=on_progress
    )


def GetVideoInfo(url: str) -> Dict[str, Union[str, List[int]]]:
    """
    Get video metadata without downloading (supports all sites).
    
    Args:
        url: Video URL from any supported site
    
    Returns:
        Dictionary containing:
            - title: Video title
            - available_qualities: List of available quality heights
            - video_id: Extracted video ID
            - site: Site name (e.g., "pornhub", "eporner")
            
    Raises:
        ValueError: If URL is from an unsupported site
            
    Example:
        >>> from RedLight import GetVideoInfo
        >>> info = GetVideoInfo("https://pornhub.com/...")
        >>> print(f"Title: {info['title']}")
        >>> print(f"Site: {info['site']}")
    """
    registry = SiteRegistry()
    downloader = registry.get_downloader_for_url(url)
    
    if not downloader:
        raise ValueError(f"Unsupported URL. Supported sites: {', '.join([s['name'] for s in registry.get_all_sites()])}")
    
    return downloader.get_info(url)


def ListAvailableQualities(url: str) -> List[int]:
    """
    List all available quality options for a video (supports all sites).
    
    Args:
        url: Video URL from any supported site
    
    Returns:
        List of available quality heights (e.g., [1080, 720, 480])
        
    Example:
        >>> from RedLight import ListAvailableQualities
        >>> qualities = ListAvailableQualities("https://eporner.com/...")
        >>> print(f"Available: {qualities}")
    """
    info = GetVideoInfo(url)
    return info["available_qualities"]


# =============================================================================
# Resume/Pause Download Functions (NEW in v1.0.14)
# =============================================================================

def StartResumableDownload(
    url: str,
    output_dir: str = "./downloads",
    quality: str = "best",
    filename: Optional[str] = None,
    proxy: Optional[str] = None
) -> str:
    """
    Start a resumable download and get a download ID.
    
    This creates a download that can be paused and resumed later.
    
    Args:
        url: Video URL from any supported site
        output_dir: Directory to save the video
        quality: Video quality
        filename: Custom filename (optional)
        proxy: HTTP/HTTPS proxy (optional)
    
    Returns:
        Download ID that can be used to pause/resume
        
    Example:
        >>> from RedLight import StartResumableDownload, PauseDownload
        >>> download_id = StartResumableDownload("https://...")
        >>> # Later, pause it
        >>> PauseDownload(download_id)
    """
    from .resume_manager import get_resume_manager
    
    manager = get_resume_manager()
    
    # Get video info
    info = GetVideoInfo(url)
    registry = SiteRegistry()
    site_name = registry.detect_site(url)
    
    # Create download entry
    output_path = str(Path(output_dir) / (filename or f"{info['title']}.mp4"))
    download_id = manager.create_download(
        url=url,
        output_path=output_path,
        quality=quality,
        site=site_name,
        title=info.get('title', '')
    )
    
    return download_id


def PauseDownload(download_id: str) -> bool:
    """
    Pause an active download.
    
    Args:
        download_id: Download ID from StartResumableDownload
        
    Returns:
        True if successfully paused
        
    Example:
        >>> from RedLight import PauseDownload
        >>> PauseDownload("abc123")
    """
    from .resume_manager import get_resume_manager
    return get_resume_manager().pause_download(download_id)


def ResumeDownload(download_id: str) -> Optional[Dict[str, Any]]:
    """
    Resume a paused download.
    
    Args:
        download_id: Download ID to resume
        
    Returns:
        Download state dictionary if resumable, None otherwise
        
    Example:
        >>> from RedLight import ResumeDownload
        >>> state = ResumeDownload("abc123")
        >>> if state:
        ...     print(f"Resuming: {state['title']}")
    """
    from .resume_manager import get_resume_manager
    state = get_resume_manager().resume_download(download_id)
    return state.to_dict() if state else None


def CancelDownload(download_id: str) -> bool:
    """
    Cancel a download and remove its state.
    
    Args:
        download_id: Download ID to cancel
        
    Returns:
        True if successfully cancelled
    """
    from .resume_manager import get_resume_manager
    return get_resume_manager().cancel_download(download_id)


def GetActiveDownloads() -> List[Dict[str, Any]]:
    """
    Get list of active (downloading) downloads.
    
    Returns:
        List of download state dictionaries
        
    Example:
        >>> from RedLight import GetActiveDownloads
        >>> active = GetActiveDownloads()
        >>> for d in active:
        ...     print(f"{d['title']}: {d['progress_percent']:.1f}%")
    """
    from .resume_manager import get_resume_manager
    downloads = get_resume_manager().list_active_downloads()
    return [d.to_dict() for d in downloads]


def GetPausedDownloads() -> List[Dict[str, Any]]:
    """
    Get list of paused downloads.
    
    Returns:
        List of download state dictionaries
        
    Example:
        >>> from RedLight import GetPausedDownloads
        >>> paused = GetPausedDownloads()
        >>> for d in paused:
        ...     print(f"{d['title']}: paused at {d['progress_percent']:.1f}%")
    """
    from .resume_manager import get_resume_manager
    downloads = get_resume_manager().list_paused_downloads()
    return [d.to_dict() for d in downloads]


# =============================================================================
# Download History Functions (NEW in v1.0.14)
# =============================================================================

def GetDownloadHistory(
    limit: int = 50,
    site: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get download history.
    
    Args:
        limit: Maximum number of entries to return
        site: Filter by site name (optional)
        
    Returns:
        List of history entries with url, title, filename, quality, date, etc.
        
    Example:
        >>> from RedLight import GetDownloadHistory
        >>> history = GetDownloadHistory(limit=10)
        >>> for item in history:
        ...     print(f"{item['title']} - {item['quality']}p")
    """
    from .database import DatabaseManager
    db = DatabaseManager()
    return db.get_history(limit=limit, site=site)


def ClearDownloadHistory(older_than_days: Optional[int] = None) -> int:
    """
    Clear download history.
    
    Args:
        older_than_days: Only clear entries older than this many days.
                        If None, clears all history.
                        
    Returns:
        Number of entries deleted
        
    Example:
        >>> from RedLight import ClearDownloadHistory
        >>> deleted = ClearDownloadHistory(older_than_days=30)
        >>> print(f"Deleted {deleted} old entries")
    """
    from .database import DatabaseManager
    db = DatabaseManager()
    return db.clear_history(older_than_days=older_than_days)


def ExportHistory(
    format: str = "json",
    filepath: Optional[str] = None
) -> str:
    """
    Export download history to file.
    
    Args:
        format: Export format - "json" or "csv"
        filepath: Output file path. If None, returns data as string.
        
    Returns:
        Exported data as string, or filepath if saved to file
        
    Example:
        >>> from RedLight import ExportHistory
        >>> # Get as JSON string
        >>> data = ExportHistory(format="json")
        >>> # Or save to file
        >>> ExportHistory(format="csv", filepath="history.csv")
    """
    from .database import DatabaseManager
    db = DatabaseManager()
    return db.export_history(format=format, filepath=filepath)


# =============================================================================
# Statistics Functions (NEW in v1.0.14)
# =============================================================================

def GetStatistics() -> Dict[str, Any]:
    """
    Get comprehensive download statistics.
    
    Returns:
        Dictionary with:
        - total_downloads: Total number of downloads
        - total_size: Total downloaded size in bytes
        - avg_quality: Average quality
        - top_site: Most used site
        - first_download: Date of first download
        - last_download: Date of last download
        
    Example:
        >>> from RedLight import GetStatistics
        >>> stats = GetStatistics()
        >>> print(f"Total downloads: {stats['total_downloads']}")
    """
    from .statistics import get_statistics
    return get_statistics().get_summary()


def GetStatsBySite() -> Dict[str, Dict[str, Any]]:
    """
    Get statistics grouped by site.
    
    Returns:
        Dictionary with site names as keys:
        {"pornhub": {"count": 50, "size": 1024000, "avg_quality": 720}, ...}
        
    Example:
        >>> from RedLight import GetStatsBySite
        >>> by_site = GetStatsBySite()
        >>> for site, stats in by_site.items():
        ...     print(f"{site}: {stats['count']} downloads")
    """
    from .statistics import get_statistics
    return get_statistics().get_by_site()


def GetStatsByQuality() -> Dict[str, int]:
    """
    Get statistics grouped by quality.
    
    Returns:
        Dictionary with quality as keys: {"1080": 50, "720": 30, ...}
    """
    from .statistics import get_statistics
    return get_statistics().get_by_quality()


def GetStatsByDate(days: int = 30) -> List[Dict[str, Any]]:
    """
    Get daily download statistics.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of daily stats: [{"date": "2024-01-15", "count": 5}, ...]
    """
    from .statistics import get_statistics
    return get_statistics().get_by_date(days=days)


# =============================================================================
# Notification Functions (NEW in v1.0.14)
# =============================================================================

def EnableNotifications(enabled: bool = True, sound: bool = True):
    """
    Enable or disable desktop notifications.
    
    Args:
        enabled: Enable notifications (default: True)
        sound: Enable notification sounds (default: True)
        
    Example:
        >>> from RedLight import EnableNotifications
        >>> EnableNotifications(enabled=True, sound=False)
    """
    from .notifications import get_notifier
    notifier = get_notifier()
    
    if enabled:
        notifier.enable()
    else:
        notifier.disable()
    
    if sound:
        notifier.enable_sound()
    else:
        notifier.disable_sound()


def SetNotificationSound(path: Optional[str] = None):
    """
    Set custom notification sound file.
    
    Args:
        path: Path to sound file, or None for system default
    """
    from .notifications import get_notifier
    get_notifier().set_sound_file(path)


def SendNotification(title: str, message: str, notif_type: str = "info"):
    """
    Send a custom notification.
    
    Args:
        title: Notification title
        message: Notification message
        notif_type: Type - "success", "error", "warning", "info"
        
    Example:
        >>> from RedLight import SendNotification
        >>> SendNotification("Done!", "All downloads complete", "success")
    """
    from .notifications import get_notifier
    get_notifier().notify_custom(title, message, notif_type)


# =============================================================================
# VideoDownloader Class
# =============================================================================

class VideoDownloader:
    """
    Main class for programmatic video downloads with full control.
    
    This class provides a clean API for developers who want more control
    over the download process, including progress tracking and quality selection.
    
    Example:
        >>> from RedLight import VideoDownloader
        >>> 
        >>> def progress(downloaded, total):
        ...     percent = (downloaded / total) * 100
        ...     print(f"Progress: {percent:.1f}%")
        >>> 
        >>> downloader = VideoDownloader(output_dir="./videos")
        >>> video_path = downloader.download(
        ...     url="https://pornhub.com/...",
        ...     quality="720",
        ...     on_progress=progress
        ... )
    """
    
    def __init__(
        self,
        output_dir: str = "./downloads",
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        notifications: bool = False
    ):
        """
        Initialize VideoDownloader.
        
        Args:
            output_dir: Default directory for downloads
            proxy: HTTP/HTTPS proxy (e.g., "http://127.0.0.1:8080")
            headers: Custom HTTP headers
            notifications: Enable desktop notifications on completion
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.proxy = proxy
        self.headers = headers
        self.notifications = notifications
        
        if notifications:
            EnableNotifications(enabled=True)
    
    def download(
        self,
        url: str,
        quality: str = "best",
        filename: Optional[str] = None,
        keep_ts: bool = False,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Download a video.
        
        Args:
            url: Video URL
            quality: Quality selection
            filename: Custom filename
            keep_ts: Keep original file
            on_progress: Progress callback
            
        Returns:
            Path to downloaded file
        """
        result = DownloadVideo(
            url=url,
            output_dir=str(self.output_dir),
            quality=quality,
            filename=filename,
            keep_ts=keep_ts,
            proxy=self.proxy,
            on_progress=on_progress
        )
        
        # Send notification if enabled
        if self.notifications:
            from .notifications import get_notifier
            info = GetVideoInfo(url)
            get_notifier().notify_download_complete(
                title=info.get('title', 'Video'),
                filename=Path(result).name,
                path=result,
                quality=quality
            )
        
        return result
    
    def get_info(self, url: str) -> Dict[str, Union[str, List[int]]]:
        """Get video information without downloading."""
        return GetVideoInfo(url)
    
    def list_qualities(self, url: str) -> List[int]:
        """List available quality options."""
        return ListAvailableQualities(url)
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get download history."""
        return GetDownloadHistory(limit=limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get download statistics."""
        return GetStatistics()

