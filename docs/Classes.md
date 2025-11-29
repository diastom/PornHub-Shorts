# 📦 Classes Documentation

This document provides detailed documentation for all classes in the PHShorts library.

## Table of Contents

- [VideoDownloader](#videodownloader)
- [BatchDownloader](#batchdownloader)
- [PlaylistDownloader](#playlistdownloader)
- [VideoConverter](#videoconverter)
- [MetadataEditor](#metadataeditor)
- [PornHubSearch](#pornhubsearch)
- [AsyncVideoDownloader](#asyncvideodownloader)

---

## VideoDownloader

Main class for programmatic video downloads with full control over the download process.

### Class Signature

```python
class VideoDownloader:
    def __init__(
        self,
        output_dir: str = "./downloads",
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    )
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_dir` | `str` | `"./downloads"` | Default directory for all downloads |
| `proxy` | `str \| None` | `None` | HTTP/HTTPS proxy URL (e.g., `"http://127.0.0.1:8080"`) |
| `headers` | `Dict \| None` | `None` | Custom HTTP headers for requests |

### Methods

#### `download()`

Download a single video.

```python
def download(
    self,
    url: str,
    quality: str = "best",
    filename: Optional[str] = None,
    keep_ts: bool = False,
    on_progress: Optional[Callable[[int, int], None]] = None
) -> str
```

**Parameters:**
- `url` - Video URL
- `quality` - Quality: `"best"`, `"worst"`, or specific height (e.g., `"720"`)
- `filename` - Custom filename (optional)
- `keep_ts` - Keep original .ts file (skip MP4 conversion)
- `on_progress` - Progress callback `(downloaded, total)`

**Returns:** Path to downloaded video

#### `get_info()`

Get video information without downloading.

```python
def get_info(self, url: str) -> Dict[str, Union[str, List[int]]]
```

**Returns:** Dictionary with `title`, `available_qualities`, and `video_id`

#### `list_qualities()`

List available quality options for a video.

```python
def list_qualities(self, url: str) -> List[int]
```

**Returns:** List of quality heights (e.g., `[1080, 720, 480]`)

### Examples

#### Basic Usage

```python
from PHShorts import VideoDownloader

# Initialize downloader
downloader = VideoDownloader(output_dir="./my_videos")

# Download a video
video_path = downloader.download(
    url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    quality="720"
)

print(f"Downloaded: {video_path}")
```

#### With Progress Tracking

```python
from PHShorts import VideoDownloader

def on_progress(downloaded, total):
    percent = (downloaded / total) * 100
    print(f"Progress: {percent:.1f}% ({downloaded}/{total})")

downloader = VideoDownloader()
video_path = downloader.download(
    url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    on_progress=on_progress
)
```

#### With Proxy

```python
from PHShorts import VideoDownloader

# Use proxy for downloads
downloader = VideoDownloader(
    output_dir="./videos",
    proxy="http://127.0.0.1:8080"
)

video_path = downloader.download("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
```

#### Check Info Before Download

```python
from PHShorts import VideoDownloader

downloader = VideoDownloader()

# Get video info first
info = downloader.get_info("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
print(f"Title: {info['title']}")
print(f"Available qualities: {info['available_qualities']}")

# Download in best available quality
video_path = downloader.download(url, quality="best")
```

---

## BatchDownloader

Download multiple videos efficiently with concurrent or sequential processing.

### Class Signature

```python
class BatchDownloader:
    def __init__(
        self,
        output_dir: str = "./downloads",
        concurrent: bool = False,
        max_workers: int = 3,
        quality: str = "best",
        keep_ts: bool = False
    )
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_dir` | `str` | `"./downloads"` | Directory to save downloaded videos |
| `concurrent` | `bool` | `False` | If `True`, downloads simultaneously; if `False`, one-by-one |
| `max_workers` | `int` | `3` | Maximum concurrent downloads (only if `concurrent=True`) |
| `quality` | `str` | `"best"` | Default quality for all downloads |
| `keep_ts` | `bool` | `False` | Keep original .ts files |

### Methods

#### `AddUrl()`

Add a single URL to the download queue.

```python
def AddUrl(self, url: str) -> None
```

#### `AddUrls()`

Add multiple URLs to the download queue.

```python
def AddUrls(self, urls: List[str]) -> None
```

#### `ClearQueue()`

Clear all URLs from the download queue.

```python
def ClearQueue(self) -> None
```

#### `DownloadAll()`

Download all queued videos.

```python
def DownloadAll(
    self,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    on_complete: Optional[Callable[[str, str], None]] = None,
    on_error: Optional[Callable[[str, Exception], None]] = None
) -> Dict[str, str]
```

**Parameters:**
- `on_progress` - Callback `(completed, total, current_url)` called after each video
- `on_complete` - Callback `(url, path)` called when a video downloads successfully
- `on_error` - Callback `(url, exception)` called when a download fails

**Returns:** Dictionary mapping successful URLs to their file paths

### Properties

#### `QueueSize`

Get the number of URLs in the queue.

```python
@property
def QueueSize(self) -> int
```

### Examples

#### Sequential Download

```python
from PHShorts import BatchDownloader

urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.pornhub.com/view_video.php?viewkey=yyyyy",
    "https://www.pornhub.com/view_video.php?viewkey=zzzzz"
]

# Sequential (one-by-one) download
downloader = BatchDownloader(concurrent=False)
downloader.AddUrls(urls)

results = downloader.DownloadAll()
print(f"Downloaded {len(results)} videos")
```

#### Concurrent Download

```python
from PHShorts import BatchDownloader

urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.pornhub.com/view_video.php?viewkey=yyyyy",
    "https://www.pornhub.com/view_video.php?viewkey=zzzzz"
]

# Concurrent download (3 videos at once)
downloader = BatchDownloader(
    concurrent=True,
    max_workers=3,
    quality="720"
)

downloader.AddUrls(urls)
results = downloader.DownloadAll()
```

#### With Callbacks

```python
from PHShorts import BatchDownloader

def on_progress(completed, total, current_url):
    print(f"[{completed}/{total}] Downloading: {current_url}")

def on_complete(url, path):
    print(f"✓ Completed: {path}")

def on_error(url, error):
    print(f"✗ Failed: {url} - {error}")

downloader = BatchDownloader(concurrent=True, max_workers=3)
downloader.AddUrls(urls)

results = downloader.DownloadAll(
    on_progress=on_progress,
    on_complete=on_complete,
    on_error=on_error
)

print(f"\nTotal downloads: {len(results)}/{len(urls)}")
```

#### Progress Bar Example

```python
from PHShorts import BatchDownloader
from tqdm import tqdm

urls = ["url1", "url2", "url3"]  # Your URLs here

downloader = BatchDownloader(concurrent=True)
downloader.AddUrls(urls)

with tqdm(total=len(urls), desc="Downloading") as pbar:
    def on_complete(url, path):
        pbar.update(1)
    
    def on_error(url, error):
        pbar.update(1)
    
    results = downloader.DownloadAll(
        on_complete=on_complete,
        on_error=on_error
    )
```

---

## PlaylistDownloader

Download videos from a channel, user profile, or playlist.

### Class Signature

```python
class PlaylistDownloader:
    def __init__(self)
```

### Methods

#### `GetChannelVideos()`

Get video URLs from a channel or user.

```python
def GetChannelVideos(
    self,
    target: str,
    limit: int = 10
) -> List[str]
```

**Parameters:**
- `target` - Username, channel name, or full URL
- `limit` - Maximum number of videos to retrieve

**Returns:** List of video URLs

### Examples

#### Download from Channel

```python
from PHShorts import PlaylistDownloader, BatchDownloader

# Get videos from channel
playlist = PlaylistDownloader()
urls = playlist.GetChannelVideos("pornhub_user", limit=10)

print(f"Found {len(urls)} videos")

# Download them using BatchDownloader
downloader = BatchDownloader(concurrent=True)
downloader.AddUrls(urls)
results = downloader.DownloadAll()
```

#### With URL

```python
from PHShorts import PlaylistDownloader

playlist = PlaylistDownloader()

# Can also use full URL
urls = playlist.GetChannelVideos(
    "https://www.pornhub.com/model/username",
    limit=5
)
```

---

## VideoConverter

Convert videos to different formats and compress them using FFmpeg.

### Class Signature

```python
class VideoConverter:
    def __init__(self)
```

### Static Methods

#### `IsFFmpegAvailable()`

Check if FFmpeg is installed and available.

```python
@staticmethod
def IsFFmpegAvailable() -> bool
```

**Returns:** `True` if FFmpeg is available, `False` otherwise

### Methods

#### `Convert()`

Convert a video to a different format.

```python
def Convert(
    self,
    input_file: str,
    output_format: str = "mp4",
    compress_quality: Optional[int] = None,
    audio_only: bool = False
) -> str
```

**Parameters:**
- `input_file` - Path to input video
- `output_format` - Output format: `"mp4"`, `"webm"`, `"mkv"`
- `compress_quality` - Compression quality (0-100, higher=better)
- `audio_only` - If `True`, extracts audio as MP3

**Returns:** Path to converted file

#### `Compress()`

Compress a video to reduce file size.

```python
def Compress(
    self,
    input_file: str,
    quality: int = 70,
    output_file: Optional[str] = None
) -> str
```

**Parameters:**
- `input_file` - Path to input video
- `quality` - Compression quality (0-100, higher=better)
- `output_file` - Optional output path

**Returns:** Path to compressed file

### Examples

#### Convert Format

```python
from PHShorts import VideoConverter

converter = VideoConverter()

# Check if FFmpeg is available
if not converter.IsFFmpegAvailable():
    print("FFmpeg not installed!")
    exit(1)

# Convert to WebM
output = converter.Convert(
    input_file="video.mp4",
    output_format="webm"
)
print(f"Converted: {output}")
```

#### Compress Video

```python
from PHShorts import VideoConverter

converter = VideoConverter()

# Compress video (70% quality)
compressed = converter.Compress(
    input_file="video.mp4",
    quality=70
)
print(f"Compressed: {compressed}")
```

#### Extract Audio

```python
from PHShorts import VideoConverter

converter = VideoConverter()

# Extract audio as MP3
audio = converter.Convert(
    input_file="video.mp4",
    audio_only=True
)
print(f"Audio extracted: {audio}")
```

#### Combined Operations

```python
from PHShorts import DownloadVideo, VideoConverter

# Download video
video_path = DownloadVideo(url, keep_ts=True)

# Convert to MKV and compress
converter = VideoConverter()
output = converter.Convert(
    input_file=video_path,
    output_format="mkv",
    compress_quality=80
)

print(f"Final output: {output}")
```

---

## MetadataEditor

Edit video metadata and thumbnails using FFmpeg.

### Class Signature

```python
class MetadataEditor:
    def __init__(self)
```

### Methods

#### `SetMetadata()`

Set video metadata tags.

```python
def SetMetadata(
    self,
    video_path: str,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    description: Optional[str] = None,
    genre: Optional[str] = None,
    date: Optional[str] = None,
    output_path: Optional[str] = None
) -> str
```

**Parameters:**
- `video_path` - Path to input video
- `title` - Video title
- `artist` - Artist/Author
- `album` - Album/Collection
- `description` - Video description/comment
- `genre` - Genre
- `date` - Creation date (YYYY)
- `output_path` - Optional output path (default: overwrite input)

**Returns:** Path to modified video

#### `SetThumbnail()`

Embed a custom thumbnail into the video.

```python
def SetThumbnail(
    self,
    video_path: str,
    thumbnail_path: str,
    output_path: Optional[str] = None
) -> str
```

**Parameters:**
- `video_path` - Path to input video
- `thumbnail_path` - Path to image file
- `output_path` - Optional output path

**Returns:** Path to modified video

### Examples

#### Set Metadata

```python
from PHShorts import MetadataEditor

editor = MetadataEditor()

# Set video metadata
output = editor.SetMetadata(
    video_path="video.mp4",
    title="My Awesome Video",
    artist="Me",
    description="This is my video",
    genre="Entertainment",
    date="2024"
)

print(f"Metadata updated: {output}")
```

#### Set Thumbnail

```python
from PHShorts import MetadataEditor

editor = MetadataEditor()

# Add custom thumbnail
output = editor.SetThumbnail(
    video_path="video.mp4",
    thumbnail_path="thumbnail.jpg"
)

print(f"Thumbnail added: {output}")
```

#### Combined Metadata Operations

```python
from PHShorts import DownloadVideo, MetadataEditor

# Download video
video_path = DownloadVideo(url)

# Edit metadata
editor = MetadataEditor()

# Set metadata
video_path = editor.SetMetadata(
    video_path=video_path,
    title="Custom Title",
    artist="My Name"
)

# Add thumbnail
video_path = editor.SetThumbnail(
    video_path=video_path,
    thumbnail_path="cover.jpg"
)

print(f"Final video: {video_path}")
```

---

## PornHubSearch

Search for videos with filtering and sorting options.

### Class Signature

```python
class PornHubSearch:
    def __init__(self)
```

### Methods

#### `search()`

Search PornHub and return list of video results.

```python
def search(
    self,
    query: str,
    page: int = 1,
    sort_by: str = "mostviewed",
    duration: Optional[str] = None
) -> List[Dict[str, str]]
```

**Parameters:**
- `query` - Search term
- `page` - Page number
- `sort_by` - Sort order: `"mostviewed"`, `"toprated"`, `"newest"`
- `duration` - Duration filter: `"short"` (<10m), `"medium"` (10-20m), `"long"` (>20m)

**Returns:** List of video dictionaries with `title`, `url`, `duration`, `views`

### Examples

#### Basic Search

```python
from PHShorts import PornHubSearch

searcher = PornHubSearch()

results = searcher.search("query")

for video in results:
    print(f"Title: {video['title']}")
    print(f"URL: {video['url']}")
    print(f"Duration: {video['duration']}")
    print(f"Views: {video['views']}")
    print("-" * 50)
```

#### Filtered Search

```python
from PHShorts import PornHubSearch

searcher = PornHubSearch()

# Search for short videos, sorted by rating
results = searcher.search(
    query="query",
    sort_by="toprated",
    duration="short"
)

print(f"Found {len(results)} short videos")
```

#### Search and Download

```python
from PHShorts import PornHubSearch, DownloadVideo

searcher = PornHubSearch()

# Search
results = searcher.search("query", sort_by="mostviewed")

# Download top 3 results
for video in results[:3]:
    print(f"Downloading: {video['title']}")
    path = DownloadVideo(video['url'])
    print(f"Saved: {path}")
```

---

## AsyncVideoDownloader

Async version of VideoDownloader for use in async applications (bots, web servers).

### Class Signature

```python
class AsyncVideoDownloader:
    def __init__(
        self,
        output_dir: str = "./downloads",
        proxy: Optional[str] = None
    )
```

### Async Methods

#### `download()`

Async download method.

```python
async def download(
    self,
    url: str,
    quality: str = "best"
) -> str
```

#### `get_info()`

Async info retrieval.

```python
async def get_info(self, url: str) -> Dict[str, Union[str, List[int]]]
```

### Examples

#### Basic Async Usage

```python
import asyncio
from PHShorts import AsyncVideoDownloader

async def main():
    async with AsyncVideoDownloader() as downloader:
        # Get video info
        info = await downloader.get_info("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
        print(f"Title: {info['title']}")
        
        # Download video
        video_path = await downloader.download(
            "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
            quality="720"
        )
        print(f"Downloaded: {video_path}")

# Run
asyncio.run(main())
```

#### Multiple Async Downloads

```python
import asyncio
from PHShorts import AsyncVideoDownloader

async def download_video(downloader, url):
    try:
        path = await downloader.download(url)
        print(f"✓ Downloaded: {path}")
        return path
    except Exception as e:
        print(f"✗ Failed: {url} - {e}")
        return None

async def main():
    urls = ["url1", "url2", "url3"]
    
    async with AsyncVideoDownloader() as downloader:
        # Download all concurrently
        tasks = [download_video(downloader, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        successful = [r for r in results if r]
        print(f"Downloaded {len(successful)}/{len(urls)} videos")

asyncio.run(main())
```

---

## See Also

- [API Functions](API.md) - High-level helper functions
- [Examples](Examples.md) - More practical examples
- [Advanced Usage](Advanced.md) - Advanced topics and best practices
