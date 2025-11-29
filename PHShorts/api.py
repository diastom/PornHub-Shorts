"""
PHShorts API - Simple helper functions for quick usage.

This module provides high-level functions for downloading videos
and extracting metadata without dealing with classes directly.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, List, Union
from .downloader import CustomHLSDownloader


def DownloadVideo(
    url: str,
    output_dir: str = "./downloads",
    quality: str = "best",
    filename: Optional[str] = None,
    keep_ts: bool = False,
    on_progress: Optional[Callable[[int, int], None]] = None
) -> str:
    """
    Download a video from PornHub Shorts.
    
    Args:
        url: Video URL (e.g., https://pornhub.com/view_video.php?viewkey=xxxxx)
        output_dir: Directory to save the video (default: "./downloads")
        quality: Video quality - "best", "worst", or specific height like "720" (default: "best")
        quality: Video quality - "best", "worst", or specific height like "720" (default: "best")
        filename: Custom filename (optional, auto-detected from video title if not provided)
        keep_ts: If True, keep original .ts file (skips MP4 conversion)
        on_progress: Callback function (downloaded_segments, total_segments) for progress tracking
    
    Returns:
        Path to the downloaded video file
        
    Example:
        >>> from PHShorts import DownloadVideo
        >>> video_path = DownloadVideo("https://pornhub.com/...")
        >>> print(f"Downloaded to: {video_path}")
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare output filename
    output_file = None
    if filename:
        output_file = output_path / filename
    
    # Initialize downloader
    downloader = CustomHLSDownloader(
        output_name=str(output_file) if output_file else None,
        keep_ts=keep_ts,
        progress_callback=on_progress
    )
    
    # Extract video info and get m3u8 streams
    streams = downloader.extract_video_info(url)
    
    # If no custom filename, the downloader auto-detected it
    # Update output path to include the detected filename
    if not output_file and downloader.output_name:
        final_output = output_path / downloader.output_name.name
        downloader.output_name = final_output
    
    # Select the best quality stream
    if isinstance(streams, dict):
        # Get the highest quality stream URL
        quality_keys = sorted([k for k in streams.keys() if isinstance(k, int)], reverse=True)
        if quality_keys:
            m3u8_url = streams[quality_keys[0]]
        else:
            m3u8_url = list(streams.values())[0]
    else:
        m3u8_url = streams
    
    # Download and convert
    result_path = downloader.download_stream(m3u8_url, preferred_quality=quality)
    
    return result_path


def GetVideoInfo(url: str) -> Dict[str, Union[str, List[int]]]:
    """
    Get video metadata without downloading.
    
    Args:
        url: Video URL
    
    Returns:
        Dictionary containing:
            - title: Video title
            - available_qualities: List of available quality heights (e.g., [720, 1080])
            - video_id: Extracted video ID
            
    Example:
        >>> from PHShorts import GetVideoInfo
        >>> info = GetVideoInfo("https://pornhub.com/...")
        >>> print(f"Title: {info['title']}")
        >>> print(f"Qualities: {info['available_qualities']}")
    """
    downloader = CustomHLSDownloader()
    
    # Extract streams and title
    streams = downloader.extract_video_info(url)
    
    # Get video ID
    video_id = downloader.extract_video_id(url)
    
    # Extract title from the auto-detected filename
    title = downloader.output_name.stem if downloader.output_name else "Unknown"
    
    # Get available qualities
    available_qualities = []
    if isinstance(streams, dict):
        available_qualities = sorted([k for k in streams.keys() if isinstance(k, int)], reverse=True)
    
    return {
        "title": title,
        "available_qualities": available_qualities,
        "video_id": video_id
    }


def ListAvailableQualities(url: str) -> List[int]:
    """
    List all available quality options for a video.
    
    Args:
        url: Video URL
    
    Returns:
        List of available quality heights (e.g., [1080, 720, 480])
        
    Example:
        >>> from PHShorts import ListAvailableQualities
        >>> qualities = ListAvailableQualities("https://pornhub.com/...")
        >>> print(f"Available: {qualities}")
    """
    info = GetVideoInfo(url)
    return info["available_qualities"]


class VideoDownloader:
    """
    Main class for programmatic video downloads with full control.
    
    This class provides a clean API for developers who want more control
    over the download process, including progress tracking and quality selection.
    
    Example:
        >>> from PHShorts import VideoDownloader
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
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize VideoDownloader.
        
        Args:
            output_dir: Default directory for downloads
            proxy: HTTP/HTTPS proxy (e.g., "http://127.0.0.1:8080")
            headers: Custom HTTP headers
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.proxy = proxy
        self.headers = headers
    
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
            quality: "best", "worst", or specific height (e.g., "720")
            filename: Custom filename (optional)
            on_progress: Progress callback function(downloaded, total)
        
        Returns:
            Path to downloaded video
        """
        return DownloadVideo(
            url=url,
            output_dir=str(self.output_dir),
            quality=quality,
            filename=filename,
            keep_ts=keep_ts,
            on_progress=on_progress
        )
    
    def get_info(self, url: str) -> Dict[str, Union[str, List[int]]]:
        """
        Get video information without downloading.
        
        Args:
            url: Video URL
        
        Returns:
            Dictionary with title, available_qualities, and video_id
        """
        return GetVideoInfo(url)
    
    def list_qualities(self, url: str) -> List[int]:
        """
        List available quality options.
        
        Args:
            url: Video URL
        
        Returns:
            List of quality heights
        """
        return ListAvailableQualities(url)
