# ⚡ Advanced Usage

Advanced topics, best practices, and optimization techniques for PHShorts.

## Table of Contents

- [Performance Optimization](#performance-optimization)
- [Custom Downloaders](#custom-downloaders)
- [Advanced Error Handling](#advanced-error-handling)
- [Memory Management](#memory-management)
- [Network Configuration](#network-configuration)
- [Custom Workflows](#custom-workflows)
- [Integration Patterns](#integration-patterns)
- [Best Practices](#best-practices)

---

## Performance Optimization

### Concurrent Downloads

```python
from PHShorts import BatchDownloader

# Optimal concurrent settings
downloader = BatchDownloader(
    concurrent=True,
    max_workers=3,  # Sweet spot for most systems
    quality="best"
)

# Too many workers can actually slow things down due to:
# - Network bandwidth limits
# - System resource contention
# - Server rate limiting
```

### Keep TS for Conversion

When planning to convert videos, skip the initial MP4 conversion:

```python
from PHShorts import DownloadVideo, VideoConverter

# Download as .ts (faster, no conversion)
video_path = DownloadVideo(url, keep_ts=True)

# Then convert to your desired format
converter = VideoConverter()
final_path = converter.Convert(
    input_file=video_path,
    output_format="webm",
    compress_quality=80
)

# Clean up .ts file
import os
os.remove(video_path)
```

### Batch Processing Best Practices

```python
from PHShorts import BatchDownloader
from pathlib import Path

def process_in_chunks(urls, chunk_size=10):
    """Process large URL lists in chunks to manage resources"""
    
    results = []
    
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        print(f"Processing chunk {i//chunk_size + 1}/{len(urls)//chunk_size + 1}")
        
        downloader = BatchDownloader(concurrent=True, max_workers=3)
        downloader.AddUrls(chunk)
        
        chunk_results = downloader.DownloadAll()
        results.extend(chunk_results.values())
        
        # Cleanup between chunks
        downloader.ClearQueue()
    
    return results
```

---

## Custom Downloaders

### Custom Progress Tracking

```python
from PHShorts import VideoDownloader
import sys

class ProgressTracker:
    def __init__(self):
        self.downloads = {}
    
    def start_download(self, url):
        """Called when download starts"""
        self.downloads[url] = {'completed': 0, 'total': 0}
    
    def on_progress(self, downloaded, total):
        """Progress callback"""
        percent = (downloaded / total) * 100
        bar_length = 50
        filled = int(bar_length * downloaded / total)
        bar = '█' * filled + '-' * (bar_length - filled)
        
        sys.stdout.write(f'\r[{bar}] {percent:.1f}% ({downloaded}/{total})')
        sys.stdout.flush()
    
    def complete_download(self, url, path):
        """Called when download completes"""
        sys.stdout.write('\n')
        print(f"✓ Complete: {path}")

# Usage
tracker = ProgressTracker()
downloader = VideoDownloader()

url = "https://www.pornhub.com/view_video.php?viewkey=xxxxx"
tracker.start_download(url)

video_path = downloader.download(
    url=url,
    on_progress=tracker.on_progress
)

tracker.complete_download(url, video_path)
```

### Custom Headers and Authentication

```python
from PHShorts import VideoDownloader

# Custom headers for advanced use cases
custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Custom Agent)',
    'Referer': 'https://www.pornhub.com/',
    'Accept-Language': 'en-US,en;q=0.9'
}

downloader = VideoDownloader(
    headers=custom_headers,
    proxy="http://proxy.example.com:8080"
)

video_path = downloader.download(url)
```

---

## Advanced Error Handling

### Comprehensive Error Recovery

```python
from PHShorts import DownloadVideo
import logging
import time
from pathlib import Path

class DownloadManager:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = logging.getLogger(__name__)
    
    def download_with_recovery(self, url, **kwargs):
        """Download with automatic error recovery"""
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{self.max_retries} for {url}")
                
                video_path = DownloadVideo(url, **kwargs)
                
                # Verify file exists and has content
                if not Path(video_path).exists():
                    raise FileNotFoundError(f"Download claimed success but file not found")
                
                file_size = Path(video_path).stat().st_size
                if file_size < 1024:  # Less than 1KB is suspicious
                    raise ValueError(f"Downloaded file too small: {file_size} bytes")
                
                self.logger.info(f"Success: {video_path} ({file_size / 1024 / 1024:.2f}MB)")
                return video_path
                
            except ConnectionError as e:
                self.logger.warning(f"Network error: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    self.logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.logger.error("Max retries reached for network error")
                    raise
            
            except ValueError as e:
                self.logger.error(f"Validation error: {e}")
                raise  # Don't retry validation errors
            
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_factor ** attempt)
                else:
                    raise
        
        raise RuntimeError(f"Failed to download after {self.max_retries} attempts")

# Usage
manager = DownloadManager(max_retries=5, backoff_factor=3)
video_path = manager.download_with_recovery(url, quality="720")
```

### Batch Error Recovery

```python
from PHShorts import BatchDownloader
import json
from pathlib import Path

class ResilientBatchDownloader:
    def __init__(self, state_file="download_state.json"):
        self.state_file = Path(state_file)
        self.state = self.load_state()
    
    def load_state(self):
        """Load previous state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {'completed': [], 'failed': [], 'pending': []}
    
    def save_state(self):
        """Save current state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def download_all(self, urls):
        """Download with state persistence"""
        
        # Filter out already completed
        pending = [u for u in urls if u not in self.state['completed']]
        
        if not pending:
            print("All downloads already completed")
            return
        
        print(f"Remaining: {len(pending)} downloads")
        
        downloader = BatchDownloader(concurrent=True, max_workers=3)
        downloader.AddUrls(pending)
        
        def on_complete(url, path):
            self.state['completed'].append(url)
            if url in self.state['failed']:
                self.state['failed'].remove(url)
            self.save_state()
            print(f"✓ {path}")
        
        def on_error(url, error):
            if url not in self.state['failed']:
                self.state['failed'].append(url)
                self.save_state()
            print(f"✗ {url} - {error}")
        
        downloader.DownloadAll(
            on_complete=on_complete,
            on_error=on_error
        )
        
        print(f"\nResults:")
        print(f"  Completed: {len(self.state['completed'])}")
        print(f"  Failed: {len(self.state['failed'])}")

# Usage
urls = [...]  # Your URLs
batch = ResilientBatchDownloader()
batch.download_all(urls)

# If interrupted, run again and it will resume
```

---

## Memory Management

### Streaming for Large Batches

```python
from PHShorts import BatchDownloader
import gc

def download_large_batch(urls, batch_size=10):
    """Download large batches without memory issues"""
    
    total = len(urls)
    completed = 0
    
    for i in range(0, total, batch_size):
        batch = urls[i:i + batch_size]
        
        print(f"Batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
        
        downloader = BatchDownloader(concurrent=True, max_workers=3)
        downloader.AddUrls(batch)
        
        results = downloader.DownloadAll()
        completed += len(results)
        
        # Cleanup
        del downloader
        gc.collect()
        
        print(f"Progress: {completed}/{total}")
    
    return completed
```

---

## Network Configuration

### Advanced Proxy Configuration

```python
from PHShorts import VideoDownloader
import os

# Use system proxy
http_proxy = os.getenv('HTTP_PROXY')
https_proxy = os.getenv('HTTPS_PROXY')

# Rotating proxies
proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080"
]

current_proxy = 0

def download_with_rotating_proxy(urls):
    """Download using rotating proxies"""
    global current_proxy
    
    results = []
    
    for url in urls:
        proxy = proxies[current_proxy % len(proxies)]
        
        print(f"Using proxy: {proxy}")
        
        downloader = VideoDownloader(proxy=proxy)
        
        try:
            path = downloader.download(url)
            results.append(path)
        except Exception as e:
            print(f"Error with {proxy}: {e}")
            current_proxy += 1  # Try next proxy
            # Retry with new proxy
            proxy = proxies[current_proxy % len(proxies)]
            downloader = VideoDownloader(proxy=proxy)
            path = downloader.download(url)
            results.append(path)
        
        current_proxy += 1
    
    return results
```

### Rate Limiting

```python
import time
from PHShorts import BatchDownloader

class RateLimitedDownloader:
    def __init__(self, requests_per_minute=10):
        self.delay = 60 / requests_per_minute
        self.last_request = 0
    
    def download(self, url):
        """Download with rate limiting"""
        # Wait if needed
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        
        # Download
        from PHShorts import DownloadVideo
        result = DownloadVideo(url)
        
        self.last_request = time.time()
        return result

# Usage
downloader = RateLimitedDownloader(requests_per_minute=5)

for url in urls:
    path = downloader.download(url)
    print(f"Downloaded: {path}")
```

---

## Custom Workflows

### Download, Convert, and Upload Pipeline

```python
from PHShorts import DownloadVideo, VideoConverter
import boto3  # AWS S3
from pathlib import Path

def process_and_upload(url, bucket_name):
    """Complete pipeline: Download -> Convert -> Upload -> Cleanup"""
    
    # 1. Download
    print("Downloading...")
    video_path = DownloadVideo(url, keep_ts=True)
    
    # 2. Convert
    print("Converting...")
    converter = VideoConverter()
    webm_path = converter.Convert(
        input_file=video_path,
        output_format="webm",
        compress_quality=75
    )
    
    # 3. Upload to S3
    print("Uploading...")
    s3 = boto3.client('s3')
    s3.upload_file(
        webm_path,
        bucket_name,
        Path(webm_path).name
    )
    
    # 4. Cleanup
    print("Cleaning up...")
    Path(video_path).unlink()
    Path(webm_path).unlink()
    
    print(f"Complete: {Path(webm_path).name} uploaded to {bucket_name}")

# Usage
process_and_upload(url, "my-videos-bucket")
```

### Automated Channel Monitoring

```python
from PHShorts import PlaylistDownloader, BatchDownloader
import schedule
import time
from pathlib import Path
import json

class ChannelMonitor:
    def __init__(self, channel, check_file="seen_videos.json"):
        self.channel = channel
        self.check_file = Path(check_file)
        self.seen_videos = self.load_seen()
    
    def load_seen(self):
        """Load already seen video IDs"""
        if self.check_file.exists():
            with open(self.check_file) as f:
                return set(json.load(f))
        return set()
    
    def save_seen(self):
        """Save seen video IDs"""
        with open(self.check_file, 'w') as f:
            json.dump(list(self.seen_videos), f)
    
    def check_new_videos(self):
        """Check for new videos and download them"""
        
        print(f"Checking {self.channel}...")
        
        # Get latest videos
        playlist = PlaylistDownloader()
        urls = playlist.GetChannelVideos(self.channel, limit=20)
        
        # Filter new videos
        new_urls = [url for url in urls if url not in self.seen_videos]
        
        if not new_urls:
            print("No new videos")
            return
        
        print(f"Found {len(new_urls)} new videos")
        
        # Download
        downloader = BatchDownloader(concurrent=True)
        downloader.AddUrls(new_urls)
        
        results = downloader.DownloadAll()
        
        # Mark as seen
        self.seen_videos.update(new_urls)
        self.save_seen()
        
        print(f"Downloaded {len(results)} new videos")
    
    def start_monitoring(self, interval_minutes=60):
        """Start continuous monitoring"""
        
        # Initial check
        self.check_new_videos()
        
        # Schedule periodic checks
        schedule.every(interval_minutes).minutes.do(self.check_new_videos)
        
        print(f"Monitoring started (checking every {interval_minutes} minutes)")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

# Usage
monitor = ChannelMonitor("channel_name")
monitor.start_monitoring(interval_minutes=30)
```

---

## Integration Patterns

### Database Integration

```python
from PHShorts import DownloadVideo, GetVideoInfo
import sqlite3
from datetime import datetime

class VideoDatabase:
    def __init__(self, db_path="videos.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database schema"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                file_path TEXT,
                quality TEXT,
                file_size INTEGER,
                download_date TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()
    
    def add_video(self, url, title=None):
        """Add video to database"""
        try:
            # Get info
            if not title:
                info = GetVideoInfo(url)
                title = info['title']
            
            self.conn.execute(
                "INSERT INTO videos (url, title, status) VALUES (?, ?, ?)",
                (url, title, 'pending')
            )
            self.conn.commit()
            print(f"Added: {title}")
            
        except sqlite3.IntegrityError:
            print(f"Already in database: {url}")
    
    def download_pending(self):
        """Download all pending videos"""
        
        cursor = self.conn.execute(
            "SELECT id, url FROM videos WHERE status = 'pending'"
        )
        
        for video_id, url in cursor:
            try:
                print(f"Downloading: {url}")
                
                # Download
                video_path = DownloadVideo(url)
                
                # Update database
                file_size = Path(video_path).stat().st_size
                self.conn.execute('''
                    UPDATE videos 
                    SET file_path = ?, 
                        file_size = ?,
                        download_date = ?,
                        status = 'completed'
                    WHERE id = ?
                ''', (video_path, file_size, datetime.now().isoformat(), video_id))
                
                self.conn.commit()
                print(f"✓ Complete")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                self.conn.execute(
                    "UPDATE videos SET status = 'failed' WHERE id = ?",
                    (video_id,)
                )
                self.conn.commit()

# Usage
db = VideoDatabase()

# Add videos
db.add_video("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
db.add_video("https://www.pornhub.com/view_video.php?viewkey=yyyyy")

# Download all pending
db.download_pending()
```

---

## Best Practices

### 1. Always Use Context Managers for Async

```python
# Good ✓
async with AsyncVideoDownloader() as downloader:
    await downloader.download(url)

# Bad ✗
downloader = AsyncVideoDownloader()
await downloader.download(url)
# (no cleanup)
```

### 2. Validate URLs Before Bulk Operations

```python
from PHShorts import GetVideoInfo

def validate_urls(urls):
    """Validate URLs before batch download"""
    valid = []
    invalid = []
    
    for url in urls:
        try:
            info = GetVideoInfo(url)
            valid.append(url)
        except:
            invalid.append(url)
    
    return valid, invalid

urls = [...]  # Your URLs
valid, invalid = validate_urls(urls)

print(f"Valid: {len(valid)}, Invalid: {len(invalid)}")

# Only download valid URLs
# ... proceed with valid
```

### 3. Monitor Disk Space

```python
import shutil
from PHShorts import BatchDownloader

def download_with_space_check(urls, min_free_gb=10):
    """Check disk space before downloading"""
    
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    
    if free_gb < min_free_gb:
        raise RuntimeError(f"Insufficient disk space: {free_gb}GB free")
    
    print(f"Disk space: {free_gb}GB free")
    
    # Proceed with download
    downloader = BatchDownloader(concurrent=True)
    downloader.AddUrls(urls)
    return downloader.DownloadAll()
```

### 4. Use Logging

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phshorts.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PHShorts')

# Use throughout your code
logger.info("Starting download...")
logger.error(f"Download failed: {e}")
```

---

## See Also

- [Quick Start](QuickStart.md) - Getting started
- [API Reference](API.md) - API functions
- [Classes](Classes.md) - Class documentation
- [Examples](Examples.md) - Practical examples
