# 🚀 Quick Start Guide

Get started with PHShorts in less than 5 minutes!

## Installation

### From PyPI (Recommended)

```bash
pip install ph-shorts
```

### From Source

```bash
git clone https://github.com/diastom/PornHub-Shorts.git
cd PornHub-Shorts
pip install -e .
```

### Requirements

- **Python:** 3.10 or higher
- **FFmpeg:** Optional, but recommended for format conversion

**Install FFmpeg:**
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)

---

## Your First Download

### Option 1: Simple One-Liner

```python
from PHShorts import DownloadVideo

# Download a video (simplest way)
video_path = DownloadVideo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
print(f"Downloaded: {video_path}")
```

That's it! The video will be saved to `./downloads/` with auto-detected title.

### Option 2: With Custom Options

```python
from PHShorts import DownloadVideo

video_path = DownloadVideo(
    url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    output_dir="./my_videos",    # Custom directory
    quality="720",                # Specific quality
    filename="my_video.mp4"       # Custom filename
)

print(f"Video saved to: {video_path}")
```

---

## Common Use Cases

### 1. Download with Progress Tracking

```python
from PHShorts import DownloadVideo

def show_progress(downloaded, total):
    percent = (downloaded / total) * 100
    print(f"\rProgress: {percent:.1f}%", end="")

video_path = DownloadVideo(
    url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    on_progress=show_progress
)
print(f"\nDone! Saved to: {video_path}")
```

### 2. Check Video Info First

```python
from PHShorts import GetVideoInfo, DownloadVideo

# Get video information
info = GetVideoInfo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")

print(f"Title: {info['title']}")
print(f"Available qualities: {info['available_qualities']}")

# Download if 1080p is available
if 1080 in info['available_qualities']:
    DownloadVideo(url, quality="1080")
else:
    print("1080p not available")
```

### 3. Download Multiple Videos (Batch)

```python
from PHShorts import BatchDownloader

urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.pornhub.com/view_video.php?viewkey=yyyyy",
    "https://www.pornhub.com/view_video.php?viewkey=zzzzz"
]

# Create batch downloader
downloader = BatchDownloader(
    concurrent=True,  # Download simultaneously
    max_workers=3     # Up to 3 at once
)

# Add URLs and download
downloader.AddUrls(urls)
results = downloader.DownloadAll()

print(f"Downloaded {len(results)} videos")
```

### 4. Download from a Channel

```python
from PHShorts import PlaylistDownloader, BatchDownloader

# Get videos from a channel
playlist = PlaylistDownloader()
urls = playlist.GetChannelVideos("pornhub_user", limit=5)

print(f"Found {len(urls)} videos")

# Download them
downloader = BatchDownloader(concurrent=True)
downloader.AddUrls(urls)
results = downloader.DownloadAll()
```

### 5. Search and Download

```python
from PHShorts import PornHubSearch, DownloadVideo

# Search for videos
searcher = PornHubSearch()
results = searcher.search("query", sort_by="toprated")

# Download top 3
for video in results[:3]:
    print(f"Downloading: {video['title']}")
    DownloadVideo(video['url'])
```

### 6. Convert Format

```python
from PHShorts import DownloadVideo, VideoConverter

# Download video (keep original .ts)
video_path = DownloadVideo(url, keep_ts=True)

# Convert to WebM
converter = VideoConverter()
webm_path = converter.Convert(
    input_file=video_path,
    output_format="webm"
)

print(f"Converted: {webm_path}")
```

### 7. Compress Video

```python
from PHShorts import DownloadVideo, VideoConverter

# Download video
video_path = DownloadVideo(url)

# Compress to 70% quality
converter = VideoConverter()
compressed = converter.Compress(
    input_file=video_path,
    quality=70
)

print(f"Compressed: {compressed}")
```

### 8. Extract Audio Only

```python
from PHShorts import DownloadVideo, VideoConverter

# Download video
video_path = DownloadVideo(url)

# Extract audio as MP3
converter = VideoConverter()
audio_path = converter.Convert(
    input_file=video_path,
    audio_only=True
)

print(f"Audio: {audio_path}")
```

---

## CLI Usage

PHShorts also provides a beautiful command-line interface!

### Interactive Mode

```bash
# Launch interactive menu
ph-shorts
```

You'll see a menu with options:
1. Download Video
2. Search Videos
3. Batch Download
4. Download Channel/Playlist
5. View History
6. View Statistics
7. Exit

### Direct Commands

```bash
# Download a video
ph-shorts "VIDEO_URL"

# Download with options
ph-shorts "URL" -q 720 -o my_video.mp4

# Batch download
ph-shorts --batch "url1, url2, url3" --concurrent

# Download channel
ph-shorts --channel "username" --limit 10

# Search
ph-shorts --search "query" --sort toprated

# Convert and compress
ph-shorts "URL" --format webm --compress 70

# Extract audio
ph-shorts "URL" --audio-only
```

---

## Error Handling

Always wrap your code in try-except for production use:

```python
from PHShorts import DownloadVideo

try:
    video_path = DownloadVideo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
    print(f"Success: {video_path}")
    
except ValueError as e:
    print(f"Invalid URL: {e}")
    
except ConnectionError as e:
    print(f"Network error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Using with Proxy

If you need to use a proxy:

```python
from PHShorts import VideoDownloader

# Create downloader with proxy
downloader = VideoDownloader(
    proxy="http://127.0.0.1:8080"
)

# Download through proxy
video_path = downloader.download("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
```

---

## Async Usage (for Bots)

For async applications like Telegram/Discord bots:

```python
import asyncio
from PHShorts import AsyncVideoDownloader

async def main():
    async with AsyncVideoDownloader() as downloader:
        video_path = await downloader.download(
            "https://www.pornhub.com/view_video.php?viewkey=xxxxx"
        )
        print(f"Downloaded: {video_path}")

# Run
asyncio.run(main())
```

---

## Next Steps

Now that you know the basics, explore:

- **[API Reference](API.md)** - Detailed API function documentation
- **[Classes](Classes.md)** - Complete class documentation
- **[Examples](Examples.md)** - More practical examples
- **[Advanced Usage](Advanced.md)** - Advanced features and best practices

---

## Getting Help

- **Documentation:** You're reading it!
- **Examples:** Check [examples/](../examples/) directory
- **Issues:** [GitHub Issues](https://github.com/diastom/PornHub-Shorts/issues)

Happy downloading! 🎉
