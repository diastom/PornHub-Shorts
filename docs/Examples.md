# 💡 Code Examples

Practical, real-world examples for using PHShorts in your projects.

## Table of Contents

- [Basic Downloads](#basic-downloads)
- [Batch Processing](#batch-processing)
- [Channel Management](#channel-management)
- [Search and Filter](#search-and-filter)
- [Format Conversion](#format-conversion)
- [Automation Scripts](#automation-scripts)
- [Bot Integration](#bot-integration)
- [Error Handling](#error-handling)

---

## Basic Downloads

### Simple Download

```python
from PHShorts import DownloadVideo

url = "https://www.pornhub.com/view_video.php?viewkey=xxxxx"
video_path = DownloadVideo(url)

print(f"Downloaded: {video_path}")
```

### Download with Custom Settings

```python
from PHShorts import DownloadVideo

video_path = DownloadVideo(
    url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    output_dir="./videos",
    quality="1080",
    filename="awesome_video.mp4"
)
```

### Progress Bar with Rich

```python
from PHShorts import VideoDownloader
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

downloader = VideoDownloader()

with Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeRemainingColumn(),
) as progress:
    
    task_id = None
    
    def on_progress(downloaded, total):
        nonlocal task_id
        if task_id is None:
            task_id = progress.add_task("Downloading...", total=total)
        progress.update(task_id, completed=downloaded)
    
    video_path = downloader.download(
        url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",
        on_progress=on_progress
    )

print(f"Downloaded: {video_path}")
```

---

## Batch Processing

### Simple Batch Download

```python
from PHShorts import BatchDownloader

urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.pornhub.com/view_video.php?viewkey=yyyyy",
    "https://www.pornhub.com/view_video.php?viewkey=zzzzz"
]

downloader = BatchDownloader(
    concurrent=True,
    max_workers=3,
    quality="720"
)

downloader.AddUrls(urls)
results = downloader.DownloadAll()

print(f"Successfully downloaded {len(results)} videos")
```

### Batch Download with Progress and Error Handling

```python
from PHShorts import BatchDownloader
from pathlib import Path

urls = [...]  # Your URLs

downloader = BatchDownloader(concurrent=True, max_workers=3)
downloader.AddUrls(urls)

successful = []
failed = []

def on_complete(url, path):
    successful.append(path)
    print(f"✓ {Path(path).name}")

def on_error(url, error):
    failed.append((url, str(error)))
    print(f"✗ {url[:50]}... - {error}")

results = downloader.DownloadAll(
    on_complete=on_complete,
    on_error=on_error
)

print(f"\nResults:")
print(f"  Successful: {len(successful)}")
print(f"  Failed: {len(failed)}")

if failed:
    print("\nFailed URLs:")
    for url, error in failed:
        print(f"  - {url}")
        print(f"    Error: {error}")
```

### Download URLs from a Text File

```python
from PHShorts import BatchDownloader
from pathlib import Path

# Read URLs from file
urls_file = Path("urls.txt")
urls = [line.strip() for line in urls_file.read_text().splitlines() if line.strip()]

print(f"Found {len(urls)} URLs")

# Download
downloader = BatchDownloader(concurrent=True, max_workers=5)
downloader.AddUrls(urls)

results = downloader.DownloadAll()
print(f"Downloaded {len(results)}/{len(urls)} videos")
```

---

## Channel Management

### Download Latest Videos from Channel

```python
from PHShorts import PlaylistDownloader, BatchDownloader

# Get latest 10 videos from channel
playlist = PlaylistDownloader()
urls = playlist.GetChannelVideos("pornhub_user", limit=10)

if not urls:
    print("No videos found or channel doesn't exist")
    exit()

print(f"Found {len(urls)} videos")

# Download them
downloader = BatchDownloader(concurrent=True, max_workers=3)
downloader.AddUrls(urls)

results = downloader.DownloadAll()
print(f"Downloaded {len(results)} videos")
```

### Download and Convert Channel Videos

```python
from PHShorts import PlaylistDownloader, BatchDownloader, VideoConverter
from pathlib import Path

# Get videos
playlist = PlaylistDownloader()
urls = playlist.GetChannelVideos("channel_name", limit=5)

# Download (keep .ts for conversion)
downloader = BatchDownloader(concurrent=True, keep_ts=True)
downloader.AddUrls(urls)

video_paths = []

def on_complete(url, path):
    video_paths.append(path)
    print(f"Downloaded: {Path(path).name}")

downloader.DownloadAll(on_complete=on_complete)

# Convert to WebM and compress
converter = VideoConverter()

for video_path in video_paths:
    print(f"Converting: {Path(video_path).name}")
    
    webm_path = converter.Convert(
       input_file=video_path,
        output_format="webm",
        compress_quality=80
    )
    
    print(f"Converted: {Path(webm_path).name}")
    
    # Delete original .ts file
    Path(video_path).unlink()
```

---

## Search and Filter

### Search and Download Top Results

```python
from PHShorts import PornHubSearch, DownloadVideo

# Search for videos
searcher = PornHubSearch()
results = searcher.search(
    query="query",
    sort_by="toprated",
    duration="medium"
)

print(f"Found {len(results)} videos")

# Download top 5
for i, video in enumerate(results[:5], 1):
    print(f"\n[{i}/5] {video['title']}")
    print(f"  Duration: {video['duration']}")
    print(f"  Views: {video['views']}")
    
    try:
        path = DownloadVideo(video['url'], quality="720")
        print(f"  ✓ Downloaded: {path}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
```

### Interactive Search and Download

```python
from PHShorts import PornHubSearch, DownloadVideo

searcher = PornHubSearch()

while True:
    query = input("\nEnter search query (or 'quit'): ")
    if query.lower() == 'quit':
        break
    
    results = searcher.search(query, sort_by="mostviewed")
    
    if not results:
        print("No results found")
        continue
    
    print("\nResults:")
    for i, video in enumerate(results[:10], 1):
        print(f"{i}. {video['title']} ({video['duration']})")
    
    choice = input("\nEnter number to download (or 'skip'): ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(results):
        video = results[int(choice) - 1]
        print(f"\nDownloading: {video['title']}")
        
        try:
            path = DownloadVideo(video['url'])
            print(f"✓ Saved to: {path}")
        except Exception as e:
            print(f"✗ Error: {e}")
```

---

## Format Conversion

### Download and Convert to MP3

```python
from PHShorts import DownloadVideo, VideoConverter

# Download video
print("Downloading...")
video_path = DownloadVideo(url, keep_ts=True)

# Extract audio
print("Extracting audio...")
converter = VideoConverter()
audio_path = converter.Convert(
    input_file=video_path,
    audio_only=True
)

print(f"Audio saved: {audio_path}")

# Delete video file
from pathlib import Path
Path(video_path).unlink()
```

### Batch Convert Videos

```python
from PHShorts import VideoConverter
from pathlib import Path

converter = VideoConverter()

# Get all MP4 files in directory
video_dir = Path("./downloads")
mp4_files = list(video_dir.glob("*.mp4"))

print(f"Found {len(mp4_files)} MP4 files")

# Convert all to WebM with compression
for video_file in mp4_files:
    print(f"Converting: {video_file.name}")
    
    webm_path = converter.Convert(
        input_file=str(video_file),
        output_format="webm",
        compress_quality=75
    )
    
    print(f"  ✓ {Path(webm_path).name}")
```

### Smart Compression

```python
from PHShorts import VideoConverter
from pathlib import Path

def compress_if_large(video_path, max_size_mb=100):
    """Compress video if larger than max_size_mb"""
    
    file_size = Path(video_path).stat().st_size / (1024 * 1024)  # MB
    
    if file_size > max_size_mb:
        print(f"File size: {file_size:.1f}MB (compressing...)")
        
        converter = VideoConverter()
        compressed = converter.Compress(
            input_file=video_path,
            quality=70
        )
        
        new_size = Path(compressed).stat().st_size / (1024 * 1024)
        saved = file_size - new_size
        
        print(f"Compressed: {new_size:.1f}MB (saved {saved:.1f}MB)")
        return compressed
    else:
        print(f"File size: {file_size:.1f}MB (no compression needed)")
        return video_path

# Usage
from PHShorts import DownloadVideo

video_path = DownloadVideo(url)
final_path = compress_if_large(video_path, max_size_mb=50)
```

---

## Automation Scripts

### Daily Channel Scraper

```python
import schedule
import time
from PHShorts import PlaylistDownloader, BatchDownloader
from datetime import datetime

def download_daily():
    """Download latest videos from channel daily"""
    
    print(f"\n[{datetime.now()}] Starting daily download...")
    
    # Get latest 5 videos
    playlist = PlaylistDownloader()
    urls = playlist.GetChannelVideos("channel_name", limit=5)
    
    if not urls:
        print("No new videos found")
        return
    
    print(f"Found {len(urls)} videos")
    
    # Download
    downloader = BatchDownloader(
        output_dir=f"./downloads/{datetime.now().strftime('%Y-%m-%d')}",
        concurrent=True
    )
    downloader.AddUrls(urls)
    
    results = downloader.DownloadAll()
    print(f"Downloaded {len(results)} videos")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(download_daily)

print("Daily scraper started. Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Bulk Channel Downloader

```python
from PHShorts import PlaylistDownloader, BatchDownloader

channels = [
    "channel1",
    "channel2",
    "channel3"
]

playlist = PlaylistDownloader()
all_urls = []

# Collect URLs from all channels
for channel in channels:
    print(f"Scanning: {channel}")
    urls = playlist.GetChannelVideos(channel, limit=10)
    all_urls.extend(urls)
    print(f"  Found: {len(urls)} videos")

print(f"\nTotal videos: {len(all_urls)}")

# Download all
downloader = BatchDownloader(concurrent=True, max_workers=5)
downloader.AddUrls(all_urls)

results = downloader.DownloadAll()
print(f"\nDownloaded {len(results)}/{len(all_urls)} videos")
```

---

## Bot Integration

### Telegram Bot Example

```python
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PHShorts import AsyncVideoDownloader

async def download_video(update: Update, context):
    """Handle /download command"""
    
    url = context.args[0] if context.args else None
    
    if not url:
        await update.message.reply_text("Usage: /download <URL>")
        return
    
    await update.message.reply_text("Downloading video...")
    
    try:
        async with AsyncVideoDownloader() as downloader:
            # Get info
            info = await downloader.get_info(url)
            await update.message.reply_text(f"Title: {info['title']}")
            
            # Download
            video_path = await downloader.download(url, quality="720")
            
            # Send video
            with open(video_path, 'rb') as video:
                await update.message.reply_video(video)
            
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Create bot
app = Application.builder().token("YOUR_BOT_TOKEN").build()

# Add handlers
app.add_handler(CommandHandler("download", download_video))

# Start bot
app.run_polling()
```

### Discord Bot Example

```python
import discord
from discord.ext import commands
from PHShorts import AsyncVideoDownloader
import asyncio

bot = commands.Bot(command_prefix='!')

@bot.command()
async def download(ctx, url: str):
    """Download PornHub video"""
    
    await ctx.send("Downloading...")
    
    try:
        async with AsyncVideoDownloader() as downloader:
            # Get info
            info = await downloader.get_info(url)
            await ctx.send(f"**Title:** {info['title']}")
            
            # Download
            video_path = await downloader.download(url)
            
            # Send file
            if os.path.getsize(video_path) < 8 * 1024 * 1024:  # 8MB limit
                await ctx.send(file=discord.File(video_path))
            else:
                await ctx.send("Video too large to send on Discord")
                
    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run("YOUR_BOT_TOKEN")
```

---

## Error Handling

### Robust Download with Retry

```python
from PHShorts import DownloadVideo
import time

def download_with_retry(url, max_retries=3):
    """Download with automatic retry on failure"""
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            video_path = DownloadVideo(url)
            print(f"Success: {video_path}")
            return video_path
            
        except ConnectionError as e:
            print(f"Network error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print("Max retries reached")
                raise
                
        except ValueError as e:
            print(f"Invalid URL: {e}")
            raise  # Don't retry on invalid URL
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

# Usage
url = "https://www.pornhub.com/view_video.php?viewkey=xxxxx"
video_path = download_with_retry(url)
```

### Batch Download with Detailed Logging

```python
from PHShorts import BatchDownloader
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename=f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

urls = [...]  # Your URLs

downloader = BatchDownloader(concurrent=True)
downloader.AddUrls(urls)

def on_complete(url, path):
    logging.info(f"SUCCESS: {url} -> {path}")

def on_error(url, error):
    logging.error(f"FAILED: {url} - {error}")

results = downloader.DownloadAll(
    on_complete=on_complete,
    on_error=on_error
)

logging.info(f"Batch complete: {len(results)}/{len(urls)} successful")
```

---

## See Also

- [Quick Start](QuickStart.md) - Get started quickly
- [API Reference](API.md) - API function documentation
- [Classes](Classes.md) - Class documentation
- [Advanced Usage](Advanced.md) - Advanced topics
