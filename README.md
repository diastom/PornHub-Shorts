# 🎬 RedLight DL

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.13-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/ph-shorts?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/ph-shorts)

**Professional Adult Content Downloader with Style!** ✨

*A powerful, feature-rich downloader with a beautiful CLI and comprehensive Python API*


[Installation](#-installation) • [Features](#-features) • [Usage](#-usage) • [Examples](#-examples)

</div>

> **ℹ️ Note:** Formerly known as **PornHub-Shorts** → Renamed to **RedLight DL** to support multiple adult content platforms.

---

## 📦 Installation

### From PyPI ✅ (Recommended)

```bash
pip install ph-shorts
```

### Quick Install (Linux/macOS)

```bash
chmod +x install.sh
./install.sh
```

### Quick Install (Windows)

```batch
install.bat
```

### Manual Install from Source

```bash
# Clone the repository
git clone https://github.com/diastom/RedLightDL.git
cd RedLightDL

# Install
pip install .
```

---

## 🌐 Supported Sites

- **PornHub** - HLS streaming downloads with full quality selection
- **Eporner** - Direct MP4 downloads with aria2c support
- **Spankbang** - Hybrid Delivery MP4/HLS with aria2c support (4K!)
- **XVideos** - Multi-quality MP4/HLS downloads with intelligent fallback

---

## ✨ Features

- **Multi-Site Support** - Download from 4 adult content sites
- **Automatic Site Detection** - Just paste any supported URL
- **Beautiful CLI** - Rich terminal UI with colors and progress bars
- **Fast Downloads** - Multi-threaded segment downloading
- **Quality Selection** - Choose from available qualities (up to 4K!)
- **Batch Downloads** - Download multiple videos concurrently
- **Playlist/Channel Support** - Download entire channels
- **Advanced Search** - Search across all sites or specific ones
- **Format Conversion** - Convert to MP4/WebM/MKV, compress videos
- **Proxy Support** - Built-in HTTP/HTTPS proxy support
- **Python API** - Use as a library for automation
- **Async Support** - Perfect for bot integration

---

## 🚀 Usage

### Interactive Mode (Recommended for beginners)

Simply run without arguments:

```bash
ph-shorts
```

You'll get a beautiful interactive menu:

```
╔══════════════════════════════════════════════════════════════════╗
║  ██████╗ ███████╗██████╗ ██╗     ██╗ ██████╗ ██╗  ██╗████████╗  ║
║  ██╔══██╗██╔════╝██╔══██╗██║     ██║██╔════╝ ██║  ██║╚══██╔══╝  ║
║  ██████╔╝█████╗  ██║  ██║██║     ██║██║  ███╗███████║   ██║     ║
║  ██╔══██╗██╔══╝  ██║  ██║██║     ██║██║   ██║██╔══██║   ██║     ║
║  ██║  ██║███████╗██████╔╝███████╗██║╚██████╔╝██║  ██║   ██║     ║
║  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝     ║
║          Professional Adult Content Downloader                  ║
╚══════════════════════════════════════════════════════════════════╝
                    version 1.0.13 • RedLight DL
```


### Command Line Mode

```bash
# Download from any supported site
ph-shorts "VIDEO_URL"

# Specify quality
ph-shorts "URL" -q 720

# Custom output
ph-shorts "URL" -o my_video.mp4

# Use proxy
ph-shorts "URL" -p http://127.0.0.1:1080
```

---

## 📝 Examples

### Basic Download (Works with ANY Site!)

```python
from RedLight import DownloadVideo

# PornHub
DownloadVideo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")

# Eporner (ultra-fast with aria2c!)
DownloadVideo("https://www.eporner.com/video-xxxxx/title")

# Spankbang (4K support!)
DownloadVideo("https://spankbang.com/xxxxx/video/title")

# XVideos
DownloadVideo("https://www.xvideos.com/video.xxxxx/title")
```

### Batch Download from Multiple Sites

```python
from RedLight import BatchDownloader

urls = [
    "https://www.pornhub.com/view_video.php?viewkey=xxxxx",
    "https://www.eporner.com/video-xxxxx/title",
    "https://spankbang.com/xxxxx/video/title"
]

downloader = BatchDownloader(concurrent=True, max_workers=3)
downloader.AddUrls(urls)
results = downloader.DownloadAll()
```

### Multi-Site Search

```python
from RedLight import MultiSiteSearch, DownloadVideo

# Search across all sites
searcher = MultiSiteSearch()
results = searcher.search_all("your search term")

print(f"Found {len(results)} videos across all sites")

# Download top result from each site
for video in results[:4]:
    DownloadVideo(video['url'])
```

### More Examples

Check the [`examples/`](examples/) directory for complete working examples:
- [`basic_usage.py`](examples/basic_usage.py) - Multi-site basics
- [`multi_site_search.py`](examples/multi_site_search.py) - Search all sites
- [`multi_site_download.py`](examples/multi_site_download.py) - Batch downloads
- [`site_specific_features.py`](examples/site_specific_features.py) - Site features

---

## 📚 Documentation

Complete documentation available in [`docs/`](docs/):

- **[Quick Start Guide](docs/QuickStart.md)** - Get started in 5 minutes
- **[Multi-Site Guide](docs/MultiSite.md)** - Complete multi-site guide
- **[API Reference](docs/API.md)** - Function documentation
- **[Examples](docs/Examples.md)** - Code examples
- **[Advanced Usage](docs/Advanced.md)** - Advanced topics

---

## 🔧 Requirements

### Required
- Python 3.10 or higher
- Internet connection

### Optional (Recommended)
- **FFmpeg** - For automatic MP4 conversion
  - **Ubuntu/Debian**: `sudo apt install ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚖️ Disclaimer

This tool is for educational purposes only. Please respect copyright laws and the terms of service of the websites you download from. The developers are not responsible for any misuse of this software.

---

<div align="center">

**Made with ❤️ by AI (Google Antigravity)**

If this tool helped you, consider giving it a ⭐ on GitHub!

[GitHub](https://github.com/diastom/RedLightDL) • [PyPI](https://pypi.org/project/ph-shorts/) • [Documentation](docs/)

</div>
