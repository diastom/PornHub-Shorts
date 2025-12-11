# 🌐 Multi-Site Guide

Complete guide to using RedLight DL with all supported adult content sites.

## Table of Contents

- [Overview](#overview)
- [Supported Sites](#supported-sites)
- [Quick Start](#quick-start)
- [Simple Examples](#simple-examples)
- [Advanced Examples](#advanced-examples)
- [Multi-Site Search](#multi-site-search)
- [Site Comparison](#site-comparison)
- [Best Practices](#best-practices)

---

## Overview

RedLight DL supports **6 major adult content sites** with intelligent auto-detection. Simply paste any supported URL and RedLight will automatically use the correct downloader.

### Key Features

- **Automatic Site Detection** - No need to specify which site you're downloading from
- **Unified API** - Same functions work across all sites
- **Site-Specific Optimization** - Each site uses optimal download method
- **Multi-Site Search** - Search across all sites simultaneously
- **Batch Downloads** - Mix URLs from different sites in one batch

---

## Supported Sites

### 1. PornHub 🎬
- **Technology**: HLS Streaming
- **Qualities**: 240p, 480p, 720p, 1080p
- **Special Features**: 
  - Multi-threaded segment downloading
  - Automatic quality selection
  - Channel/playlist support
  - Advanced search filters

### 2. Eporner 🚀
- **Technology**: Direct MP4 + aria2c
- **Qualities**: Multiple MP4 qualities
- **Special Features**:
  - Ultra-fast aria2c downloads
  - Direct file download (no segments)
  - Built-in download manager
  - Resume support

### 3. Spankbang ⚡
- **Technology**: Hybrid MP4/HLS
- **Qualities**: 240p, 480p, 720p, 1080p, 4K
- **Special Features**:
  - Intelligent format selection
  - 4K support
  - aria2c integration for MP4
  - HLS fallback

### 4. XVideos 📹
- **Technology**: Multi-quality MP4/HLS
- **Qualities**: 360p, 720p, 1080p
- **Special Features**:
  - Multiple quality options
  - Intelligent fallback system
  - Both MP4 and HLS support
  - Fast downloads

### 5. xHamster 🔥
- **Technology**: HLS Streaming
- **Qualities**: 144p, 240p, 480p, 720p, 1080p
- **Special Features**:
  - Multi-quality HLS support
  - Geo-restriction fallback domains
  - Automatic domain switching
  - CustomHLSDownloader integration

### 6. XNXX 📺
- **Technology**: Multi-quality MP4/HLS
- **Qualities**: 360p, 720p, 1080p
- **Special Features**:
  - Same structure as XVideos
  - Multiple quality options
  - HLS adaptive streaming
  - Fast downloads

---

## Quick Start

### Automatic Site Detection

The easiest way to use RedLight - just paste any URL:

```python
from RedLight import DownloadVideo

# Works with ANY supported site!
video_path = DownloadVideo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
video_path = DownloadVideo("https://www.eporner.com/video-xxxxx/title")
video_path = DownloadVideo("https://spankbang.com/xxxxx/video/title")
video_path = DownloadVideo("https://www.xvideos.com/video.xxxxx/title")

# RedLight automatically detects the site and uses the right downloader!
```

---

## Simple Examples

### PornHub - Simple Download

```python
from RedLight import DownloadVideo

# Basic PornHub download
url = "https://www.pornhub.com/view_video.php?viewkey=xxxxx"
video_path = DownloadVideo(url, quality="1080")

print(f"Downloaded: {video_path}")
```

### Eporner - Fast Download

```python
from RedLight import DownloadVideo

# Eporner with ultra-fast aria2c
url = "https://www.eporner.com/video-xxxxx/title"
video_path = DownloadVideo(url)

# Automatically uses aria2c for maximum speed!
print(f"Downloaded: {video_path}")
```

### Spankbang - High Quality

```python
from RedLight import DownloadVideo

# Spankbang supports up to 4K
url = "https://spankbang.com/xxxxx/video/title"
video_path = DownloadVideo(url, quality="best")  # Gets 4K if available

print(f"Downloaded: {video_path}")
```

### XVideos - Multi-Quality

```python
from RedLight import DownloadVideo, GetVideoInfo

# Check available qualities first
url = "https://www.xvideos.com/video.xxxxx/title"
info = GetVideoInfo(url)

print(f"Available: {info['available_qualities']}")

# Download preferred quality
video_path = DownloadVideo(url, quality="720")
print(f"Downloaded: {video_path}")
```

---

## Advanced Examples

### Mixed Site Batch Download

Download videos from multiple sites in one batch:

```python
from RedLight import BatchDownloader

urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.eporner.com/video-xxxxx/title",
    "https://spankbang.com/xxxxx/video/title",
    "https://www.xvideos.com/video.xxxxx/title"
]

# RedLight handles all sites automatically
downloader = BatchDownloader(concurrent=True, max_workers=4)
downloader.AddUrls(urls)

results = downloader.DownloadAll()
print(f"Downloaded {len(results)} videos from multiple sites")
```

### Site-Specific Downloaders

For advanced control, use site-specific classes:

```python
from RedLight import (
    PornHubDownloader,
    EpornerDownloader,
    SpankBangDownloader,
    XVideosDownloader
)

# PornHub with custom settings
ph_downloader = PornHubDownloader(output_dir="./pornhub_videos")
ph_video = ph_downloader.download(
    url="https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    quality="1080"
)

# Eporner with specific configuration
ep_downloader = EpornerDownloader(output_dir="./eporner_videos")
ep_video = ep_downloader.download(
    url="https://www.eporner.com/video-xxxxx/title"
)

# Spankbang 4K download
sb_downloader = SpankBangDownloader(output_dir="./spankbang_videos")
sb_video = sb_downloader.download(
    url="https://spankbang.com/xxxxx/video/title",
    quality="2160"  # 4K
)

# XVideos with fallback
xv_downloader = XVideosDownloader(output_dir="./xvideos_videos")
xv_video = xv_downloader.download(
    url="https://www.xvideos.com/video.xxxxx/title",
    quality="720"
)
```

### Site Registry

Use the site registry for dynamic site handling:

```python
from RedLight import SiteRegistry

registry = SiteRegistry()

# Check which sites are supported
sites = registry.get_all_sites()
for site in sites:
    print(f"- {site['name']}: {site['domains']}")

# Get downloader for specific URL
url = "https://www.pornhub.com/view_video.php?viewkey=xxxxx"
downloader = registry.get_downloader_for_url(url)

if downloader:
    video_path = downloader.download(url)
    print(f"Downloaded: {video_path}")
else:
    print("URL not supported")
```

### Automatic Site Detection with Error Handling

```python
from RedLight import DownloadVideo, SiteRegistry

def smart_download(url):
    """Download with automatic site detection and error handling"""
    
    # Check if URL is supported
    registry = SiteRegistry()
    site_name = registry.detect_site(url)
    
    if not site_name:
        print(f"❌ URL not supported: {url}")
        return None
    
    print(f"✓ Detected site: {site_name}")
    
    try:
        video_path = DownloadVideo(url)
        print(f"✓ Downloaded: {video_path}")
        return video_path
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Use with any URL
smart_download("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
smart_download("https://www.eporner.com/video-xxxxx/title")
```

---

## Multi-Site Search

### Search All Sites Simultaneously

```python
from RedLight import MultiSiteSearch, DownloadVideo

# Create multi-site searcher
searcher = MultiSiteSearch()

# Search across all sites
results = searcher.search_all(
    query="your search term",
    page=1
)

print(f"Found {len(results)} videos across all sites")

# Display results from all sites
for video in results[:10]:
    print(f"[{video['site']}] {video['title']}")
    print(f"  URL: {video['url']}")
    print(f"  Duration: {video.get('duration', 'N/A')}")
    print()

# Download top result from each site
downloaded = {}
for video in results:
    site = video['site']
    if site not in downloaded:
        print(f"Downloading from {site}: {video['title']}")
        path = DownloadVideo(video['url'])
        downloaded[site] = path

print(f"Downloaded {len(downloaded)} videos from {len(downloaded)} sites")
```

### Site-Specific Search

```python
from RedLight import (
    PornHubSearch,
    EpornerSearch,
    SpankBangSearch,
    XVideosSearch,
    DownloadVideo
)

query = "your search term"

# Search PornHub
ph_search = PornHubSearch()
ph_results = ph_search.search(query, sort_by="toprated")
print(f"PornHub: {len(ph_results)} results")

# Search Eporner
ep_search = EpornerSearch()
ep_results = ep_search.search(query)
print(f"Eporner: {len(ep_results)} results")

# Search Spankbang
sb_search = SpankBangSearch()
sb_results = sb_search.search(query)
print(f"Spankbang: {len(sb_results)} results")

# Search XVideos
xv_search = XVideosSearch()
xv_results = xv_search.search(query)
print(f"XVideos: {len(xv_results)} results")

# Download best from each site
for results, site_name in [
    (ph_results, "PornHub"),
    (ep_results, "Eporner"),
    (sb_results, "Spankbang"),
    (xv_results, "XVideos")
]:
    if results:
        print(f"\nDownloading top result from {site_name}...")
        DownloadVideo(results[0]['url'])
```

---

## Site Comparison

### Feature Comparison Table

| Feature | PornHub | Eporner | Spankbang | XVideos |
|---------|---------|---------|-----------|---------|
| **Max Quality** | 1080p | 1080p | 4K | 1080p |
| **Download Method** | HLS | Direct MP4 | Hybrid | MP4/HLS |
| **Speed** | Fast | Ultra Fast | Fast | Fast |
| **aria2c Support** | No | Yes | Yes (MP4) | No |
| **Search** | Advanced | Basic | Basic | Basic |
| **Playlist Support** | Yes | No | No | No |
| **Resume Downloads** | Yes | Yes | Yes | Yes |

### When to Use Each Site

#### Use PornHub when:
- You need advanced search filters
- Downloading from channels/playlists
- Want reliable HLS streaming
- Need consistent quality

#### Use Eporner when:
- Speed is priority #1
- Want direct file downloads
- Need aria2c integration
- Downloading large batches

#### Use Spankbang when:
- Need 4K quality
- Want hybrid download options
- Looking for variety
- Need flexible quality selection

#### Use XVideos when:
- Need reliable MP4 downloads
- Want HLS fallback
- Prefer straightforward downloads
- Need good quality/size balance

---

## Best Practices

### 1. Automatic Detection for Mixed Sources

```python
from RedLight import BatchDownloader

# Mix URLs from any sites - RedLight handles it
urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.eporner.com/video-xxxxx/title",
    "https://spankbang.com/xxxxx/video/title"
]

downloader = BatchDownloader(concurrent=True)
downloader.AddUrls(urls)
results = downloader.DownloadAll()
```

### 2. Site-Specific Quality Selection

```python
from RedLight import DownloadVideo, GetVideoInfo

def download_best_available(url, preferred_quality="1080"):
    """Download with fallback to best available quality"""
    
    # Check what's available
    info = GetVideoInfo(url)
    qualities = info['available_qualities']
    
    # Try preferred quality
    if int(preferred_quality) in qualities:
        quality = preferred_quality
    else:
        # Fallback to best
        quality = "best"
    
    return DownloadVideo(url, quality=quality)

# Works with any site
download_best_available("https://www.pornhub.com/view_video.php?viewkey=xxxxx", "1080")
download_best_available("https://spankbang.com/xxxxx/video/title", "2160")  # 4K
```

### 3. Organized Multi-Site Downloads

```python
from RedLight import SiteRegistry, DownloadVideo
from pathlib import Path

def organized_download(url):
    """Download and organize by site"""
    
    registry = SiteRegistry()
    site_name = registry.detect_site(url)
    
    if not site_name:
        print(f"Unsupported URL: {url}")
        return None
    
    # Create site-specific directory
    output_dir = f"./downloads/{site_name}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Download to site folder
    video_path = DownloadVideo(url, output_dir=output_dir)
    
    print(f"Downloaded from {site_name}: {video_path}")
    return video_path

# Each video goes to its site folder
organized_download("https://www.pornhub.com/view_video.php?viewkey=xxxxx")  # -> ./downloads/pornhub/
organized_download("https://www.eporner.com/video-xxxxx/title")            # -> ./downloads/eporner/
```

### 4. Multi-Site Search and Download

```python
from RedLight import MultiSiteSearch, DownloadVideo

def search_and_download(query, max_per_site=2):
    """Search all sites and download top results"""
    
    searcher = MultiSiteSearch()
    all_results = searcher.search_all(query)
    
    # Group by site
    by_site = {}
    for video in all_results:
        site = video['site']
        if site not in by_site:
            by_site[site] = []
        by_site[site].append(video)
    
    # Download top N from each site
    downloaded = []
    for site, videos in by_site.items():
        print(f"\n{site}: Downloading top {max_per_site}")
        for video in videos[:max_per_site]:
            try:
                path = DownloadVideo(
                    video['url'],
                    output_dir=f"./downloads/{site}"
                )
                downloaded.append(path)
                print(f"  ✓ {video['title']}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    
    return downloaded

# Search and download from all sites
videos = search_and_download("your search", max_per_site=3)
print(f"\nTotal downloaded: {len(videos)}")
```

### 5. Error Handling for Multiple Sites

```python
from Red Light import DownloadVideo, SiteRegistry

def robust_multi_site_download(urls):
    """Download from multiple sites with error handling"""
    
    registry = SiteRegistry()
    results = {"success": [], "failed": []}
    
    for url in urls:
        try:
            # Detect site
            site_name = registry.detect_site(url)
            if not site_name:
                results["failed"].append((url, "Unsupported site"))
                continue
            
            print(f"[{site_name}] Downloading...")
            
            # Download
            video_path = DownloadVideo(url)
            results["success"].append((url, video_path, site_name))
            
            print(f"  ✓ Success: {video_path}")
            
        except Exception as e:
            results["failed"].append((url, str(e)))
            print(f"  ✗ Error: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Success: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed URLs:")
        for url, error in results['failed']:
            print(f"  - {url}")
            print(f"    {error}")
    
    return results

# Use with mixed URLs
urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.eporner.com/video-xxxxx/title",
    "https://spankbang.com/xxxxx/video/title",
    "https://www.xvideos.com/video.xxxxx/title"
]

results = robust_multi_site_download(urls)
```

---

## See Also

- [Quick Start Guide](QuickStart.md) - Get started quickly
- [API Reference](API.md) - Complete API documentation
- [Examples](Examples.md) - More code examples
- [Advanced Usage](Advanced.md) - Advanced techniques
- [Classes](Classes.md) - Class documentation

---

**Made with ❤️ for the community** | RedLight DL - Professional Multi-Site Downloader
