# 🎬 RedLight DL

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.11-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Professional Adult Content Downloader with Style!** ✨

*A powerful, feature-rich downloader with a beautiful CLI and comprehensive Python API*


[Installation](#-installation) • [Features](#-features) • [Usage](#-usage) • [Examples](#-examples)

</div>

> **ℹ️ Note:** Formerly known as **PornHub-Shorts** → Renamed to **RedLight DL** to support multiple adult content platforms.

---

this tool is made by AI in google **antigravity**

## 🌐 Supported Sites

- **PornHub** - HLS streaming downloads with full quality selection
- **Eporner** - Direct MP4 downloads with aria2c support

More sites coming soon! The architecture is designed for easy integration of new platforms.

---

## ✨ Features

### 🎯 Core Features
- **Multi-Site Support** - Download from multiple adult content sites
- **Automatic Site Detection** - Just paste any supported URL
- **Beautiful CLI** - Rich terminal UI with colors and progress bars
- **Fast Downloads** - Multi-threaded segment downloading
- **Quality Selection** - Choose from available qualities (1080p, 720p, 480p, etc.)
- **Proxy Support** - Built-in HTTP/HTTPS proxy support
- **Smart Naming** - Automatically extracts and sanitizes video titles
- **Cross-platform** - Works on Windows, Linux, and macOS

### 🆕 New in v1.0.9
- 🌐 **Multi-Site Architecture** - Support for multiple adult content sites
- 🔍 **Multi-Site Search** - Search across all sites or pick specific ones
- 📊 **Search History** - Track your searches in database
- ⚡ **Eporner Support** - Direct MP4 downloads with aria2c integration
- 🔄 **Site Registry** - Easily extensible for adding new sites

### 🎉 Features from v1.0.7
- 📦 **Batch Downloads** - Download multiple videos concurrently or sequentially
- 📺 **Playlist/Channel Support** - Download entire channels with one command
- 🔍 **Advanced Search** - Search with filters (duration, sort by views/rating/date)
- 🔄 **Format Conversion** - Convert to MP4/WebM/MKV, compress videos, extract audio
- 📝 **Metadata Editor** - Edit video tags and thumbnails (API)
- 🛠️ **Enhanced API** - Comprehensive Python library for automation

### 🔧 Developer Features
- **Programmable API** - Use as a Python library to build custom scripts and bots
- **Async Support** - Perfect for Telegram/Discord bot integration
- **Type Hints** - Full type hinting for better IDE support
- **Progress Callbacks** - Track download progress in your applications


## 📦 Installation

### Method 1: From PyPI ✅ (Recommended)

```bash
pip install ph-shorts
```

### Method 2: Quick Install (Linux/macOS)

```bash
chmod +x install.sh
./install.sh
```

### Method 3: Quick Install (Windows)

```batch
install.bat
```

### Method 4: Manual Install with pip

```bash
# Clone or download the repository
git clone https://github.com/diastom/RedLightDL.git
cd RedLightDL

# Install using pip
pip install .

# Or install in development mode
pip install -e .
```

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
                    version 1.0.8 • RedLight DL
```


### Command Line Mode (For power users)

```bash
ph-shorts "VIDEO_URL" [OPTIONS]
```

## 📝 Examples

### v1.0.7 New Features

#### Batch Download
```bash
# Download multiple videos concurrently
ph-shorts --batch "url1, url2, url3" --concurrent

# Download sequentially (more stable)
ph-shorts --batch "url1, url2, url3"
```

#### Channel/Playlist Download
```bash
# Download entire channel (limit 10 videos)
ph-shorts --channel "pornhub_user" --limit 10

# Download with concurrent mode
ph-shorts --channel "https://www.pornhub.com/model/username" --limit 5 --concurrent
```

#### Advanced Search
```bash
# Search and filter
ph-shorts --search "query" --sort mostviewed --duration short

# Sort options: mostviewed, toprated, newest
# Duration: short (<10m), medium (10-20m), long (>20m)
```

#### Format Conversion
```bash
# Convert to WebM
ph-shorts "URL" --format webm

# Compress video (quality 0-100)
ph-shorts "URL" --compress 70

# Extract audio only (MP3)
ph-shorts "URL" --audio-only

# Combine options
ph-shorts "URL" --format mkv --compress 80
```

### Basic Examples

### Basic download (best quality)
```bash
ph-shorts "https://www.pornhub.com/view_video.php?viewkey=..."
```

### Specify quality
```bash
ph-shorts "URL" -q 720
```

### Custom output filename
```bash
ph-shorts "URL" -o my_video.mp4
```

### Use a proxy
```bash
ph-shorts "URL" -p http://127.0.0.1:1080
```

### Keep original .ts file
```bash
ph-shorts "URL" --keep-ts
```
```

### Async Support (for Bots)

Perfect for Telegram bots, Discord bots, and other async applications:

```python
from RedLight import AsyncVideoDownloader

async def download_for_bot(url: str):
    async with AsyncVideoDownloader() as downloader:
        # Get info first
        info = await downloader.get_info(url)
        print(f"Downloading: {info['title']}")
        
        # Download video
        video_path = await downloader.download(url)
        return video_path
```

### More Examples

Check the [`examples/`](examples/) directory for complete working examples:
- [`basic_usage.py`](examples/basic_usage.py) - Simple download
- [`progress_tracking.py`](examples/progress_tracking.py) - Progress bar
- [`telegram_bot.py`](examples/telegram_bot.py) - Telegram bot integration
- [`batch_download.py`](examples/batch_download.py) - Batch downloads

## ⚙️ Options

```
Usage: ph-shorts [URL] [OPTIONS]

Arguments:
  URL                   Video URL (optional - will prompt if not provided)

Options:
  -o, --output TEXT     Custom output filename
  -q, --quality TEXT    Quality: best, worst, 1080, 720, 480 (default: best)
  -p, --proxy TEXT      HTTP/HTTPS proxy URL
  --keep-ts             Keep original .ts file (don't convert to mp4)
  --help                Show this message and exit
```

### Quality Options

- `best` - Highest available quality (default)
- `worst` - Lowest available quality (saves bandwidth)
- `1080` - 1080p (if available)
- `720` - 720p (if available)
- `480` - 480p (if available)

## 🔧 Requirements

### Required
- Python 3.10 or higher
- Internet connection

### Optional (Recommended)
- **FFmpeg** - For automatic MP4 conversion
  - Without FFmpeg, videos are saved as `.ts` files
  - Install:
    - **Ubuntu/Debian**: `sudo apt install ffmpeg`
    - **macOS**: `brew install ffmpeg`
    - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## 🐛 Troubleshooting

### Issue: "403 Forbidden" error
**Solution**: The site might be blocking requests. Try using a different User-Agent or proxy.

### Issue: Videos saved as .ts instead of .mp4
**Solution**: Install FFmpeg for automatic conversion.

### Issue: Slow download speed
**Solution**: 
- Check your internet connection
- Try using a proxy closer to the server location
- The quality you selected might be from a slower CDN

### Issue: "No compatible HLS stream found"
**Solution**: The video URL might be invalid or the video format is not supported.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

This tool is for educational purposes only. Please respect copyright laws and the terms of service of the websites you download from. The developers are not responsible for any misuse of this software.

## 🙏 Credits

Built with:
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [Click](https://github.com/pallets/click) - CLI framework
- [Requests](https://github.com/psf/requests) - HTTP library

## 📧 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions

---

<div align="center">

**Made with ❤️ for the community**

If this tool helped you, consider giving it a ⭐ on GitHub!

</div>
