# 🚀 Quick Start Guide

Get started with RedLight in less than 5 minutes!

## Installation

### From PyPI (Recommended)

```bash
pip install ph-shorts
```

### From Source

```bash
git clone https://github.com/diastom/RedLightDL.git
cd RedLightDL
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

## 🌐 Multi-Site Support

RedLight supports **6 major adult content sites** with automatic detection:

| Site | Technology | Max Quality | Special Features |
|------|------------|-------------|------------------|
| **PornHub** | HLS Streaming | 1080p | Playlists, Advanced Search |
| **Eporner** | Direct MP4 + aria2c | 1080p | Ultra-fast downloads |
| **Spankbang** | Hybrid MP4/HLS | 4K | Intelligent format selection |
| **XVideos** | Multi-quality MP4/HLS | 1080p | Intelligent fallback |
| **xHamster** | HLS Streaming | 1080p | Multi-quality, Geo-fallback |
| **XNXX** | Multi-quality MP4/HLS | 1080p | Same as XVideos |

**Best Part**: You don't need to do anything special! Just paste any supported URL and RedLight automatically uses the correct downloader.

---

## Your First Download

### Option 1: Simple One-Liner (Works with ANY Site!)

```python
from RedLight import DownloadVideo

# Works with PornHub
video_path = DownloadVideo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")

# Works with Eporner (ultra-fast with aria2c)
video_path = DownloadVideo("https://www.eporner.com/video-xxxxx/title")

# Works with Spankbang (supports 4K!)
video_path = DownloadVideo("https://spankbang.com/xxxxx/video/title")

# Works with XVideos
video_path = DownloadVideo("https://www.xvideos.com/video.xxxxx/title")

# Works with xHamster
video_path = DownloadVideo("https://xhamster.com/videos/video-title-xxxxx")

# Works with XNXX
video_path = DownloadVideo("https://www.xnxx.com/video-xxxxx/title")

print(f"Downloaded: {video_path}")
```

That's it! RedLight automatically detects the site and uses the optimal downloader.

### Option 2: With Custom Options (All Sites)

```python
from RedLight import DownloadVideo

# Same API works for all sites!
video_path = DownloadVideo(
    url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",  # Or any other site
    output_dir="./my_videos",    # Custom directory
    quality="720",                # Specific quality
    filename="my_video.mp4"       # Custom filename
)

print(f"Video saved to: {video_path}")
```

### Option 3: Multi-Site Batch Download

```python
from RedLight import BatchDownloader

# Mix URLs from different sites - RedLight handles it!
urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.eporner.com/video-xxxxx/title",
    "https://spankbang.com/xxxxx/video/title",
    "https://www.xvideos.com/video.xxxxx/title"
]

downloader = BatchDownloader(concurrent=True, max_workers=4)
downloader.AddUrls(urls)
results = downloader.DownloadAll()

print(f"Downloaded {len(results)} videos from multiple sites!")
```

---

## Common Use Cases

### 1. Download with Progress Tracking

```python
from RedLight import DownloadVideo

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
from RedLight import GetVideoInfo, DownloadVideo

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
from RedLight import BatchDownloader

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
from RedLight import PlaylistDownloader, BatchDownloader

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

#### Search Single Site (PornHub)
```python
from RedLight import PornHubSearch, DownloadVideo

# Search for videos
searcher = PornHubSearch()
results = searcher.search("query", sort_by="toprated")

# Download top 3
for video in results[:3]:
    print(f"Downloading: {video['title']}")
    DownloadVideo(video['url'])
```

#### Search All Sites
```python
from RedLight import MultiSiteSearch, DownloadVideo

# Search across all 4 sites simultaneously!
searcher = MultiSiteSearch()
results = searcher.search_all("query")

print(f"Found {len(results)} videos across all sites")

# Download top result from each site
downloaded = {}
for video in results:
    site = video['site']
    if site not in downloaded:
        print(f"Downloading from {site}: {video['title']}")
        DownloadVideo(video['url'])
        downloaded[site] = video
```

### 6. Convert Format

```python
from RedLight import DownloadVideo, VideoConverter

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
from RedLight import DownloadVideo, VideoConverter

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
from RedLight import DownloadVideo, VideoConverter

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

RedLight also provides a beautiful command-line interface!

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
from RedLight import DownloadVideo

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
from RedLight import VideoDownloader

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
from RedLight import AsyncVideoDownloader

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
- **Issues:** [GitHub Issues](https://github.com/diastom/RedLightDL/issues)

Happy downloading! 🎉
