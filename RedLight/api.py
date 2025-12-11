from pathlib import Path
from typing import Optional, Callable, Dict, List, Union, Any
from .downloader import CustomHLSDownloader
from .sites import SiteRegistry
from .resume_manager import GetResumeManager
from .database import DatabaseManager
from .statistics import GetStatistics
from .notifications import GetNotifier


def DownloadVideo(
    url: str,
    output_dir: str = "./downloads",
    quality: str = "best",
    filename: Optional[str] = None,
    keep_ts: bool = False,
    proxy: Optional[str] = None,
    on_progress: Optional[Callable[[int, int], None]] = None
) -> str:
    registry = SiteRegistry()
    downloader = registry.get_downloader_for_url(url)
    
    if not downloader:
        raise ValueError(f"Unsupported URL. Supported sites: {', '.join([s['name'] for s in registry.get_all_sites()])}")
    
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
    registry = SiteRegistry()
    downloader = registry.get_downloader_for_url(url)
    
    if not downloader:
        raise ValueError(f"Unsupported URL. Supported sites: {', '.join([s['name'] for s in registry.get_all_sites()])}")
    
    return downloader.get_info(url)


def ListAvailableQualities(url: str) -> List[int]:
    info = GetVideoInfo(url)
    return info["available_qualities"]


def StartResumableDownload(
    url: str,
    output_dir: str = "./downloads",
    quality: str = "best",
    filename: Optional[str] = None,
    proxy: Optional[str] = None
) -> str:
    from .resume_manager import get_resume_manager
    
    manager = get_resume_manager()
    
    info = GetVideoInfo(url)
    registry = SiteRegistry()
    site_name = registry.detect_site(url)
    
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
    from .resume_manager import get_resume_manager
    return get_resume_manager().pause_download(download_id)


def ResumeDownload(download_id: str) -> Optional[Dict[str, Any]]:
    from .resume_manager import get_resume_manager
    state = get_resume_manager().resume_download(download_id)
    return state.to_dict() if state else None


def CancelDownload(download_id: str) -> bool:
    from .resume_manager import get_resume_manager
    return get_resume_manager().cancel_download(download_id)


def GetActiveDownloads() -> List[Dict[str, Any]]:
    from .resume_manager import get_resume_manager
    downloads = get_resume_manager().list_active_downloads()
    return [d.to_dict() for d in downloads]


def GetPausedDownloads() -> List[Dict[str, Any]]:
    from .resume_manager import get_resume_manager
    downloads = get_resume_manager().list_paused_downloads()
    return [d.to_dict() for d in downloads]


def GetDownloadHistory(
    limit: int = 50,
    site: Optional[str] = None
) -> List[Dict[str, Any]]:
    from .database import DatabaseManager
    db = DatabaseManager()
    return db.get_history(limit=limit, site=site)


def ClearDownloadHistory(older_than_days: Optional[int] = None) -> int:
    from .database import DatabaseManager
    db = DatabaseManager()
    return db.clear_history(older_than_days=older_than_days)


def ExportHistory(
    format: str = "json",
    filepath: Optional[str] = None
) -> str:
    from .database import DatabaseManager
    db = DatabaseManager()
    return db.export_history(format=format, filepath=filepath)


def GetStatistics() -> Dict[str, Any]:
    from .statistics import GetStatistics
    return GetStatistics().get_summary()


def GetStatsBySite() -> Dict[str, Dict[str, Any]]:
    from .statistics import GetStatistics
    return GetStatistics().get_by_site()


def GetStatsByQuality() -> Dict[str, int]:
    from .statistics import GetStatistics
    return GetStatistics().get_by_quality()


def GetStatsByDate(days: int = 30) -> List[Dict[str, Any]]:
    from .statistics import GetStatistics
    return GetStatistics().get_by_date(days=days)


def EnableNotifications(enabled: bool = True, sound: bool = True):
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
    from .notifications import get_notifier
    get_notifier().set_sound_file(path)


def SendNotification(title: str, message: str, notif_type: str = "info"):
    from .notifications import get_notifier
    get_notifier().notify_custom(title, message, notif_type)


class VideoDownloader:
    
    def __init__(
        self,
        output_dir: str = "./downloads",
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        notifications: bool = False
    ):
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
        result = DownloadVideo(
            url=url,
            output_dir=str(self.output_dir),
            quality=quality,
            filename=filename,
            keep_ts=keep_ts,
            proxy=self.proxy,
            on_progress=on_progress
        )
        
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
        return GetVideoInfo(url)
    
    def list_qualities(self, url: str) -> List[int]:
        return ListAvailableQualities(url)
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return GetDownloadHistory(limit=limit)
    
    def get_stats(self) -> Dict[str, Any]:
        return GetStatistics()
