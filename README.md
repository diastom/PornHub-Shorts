# 🎬 PH Shorts Downloader

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Download PornHub Shorts videos with style!** ✨

*A lightweight, specialized downloader with a beautiful CLI*

[Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples)

</div>

---

## ✨ Features

- 🎯 **Specialized** - Built specifically for PornHub Shorts
- 🎨 **Beautiful CLI** - Rich terminal UI with colors and progress bars
- 🚀 **Fast Downloads** - Multi-threaded segment downloading
- 📺 **Quality Selection** - Choose from available qualities (1080p, 720p, 480p, etc.)
- 🌐 **Proxy Support** - Built-in HTTP/HTTPS proxy support
- 🔄 **Auto-conversion** - Automatic conversion to MP4 (requires FFmpeg)
- 💾 **Smart Naming** - Automatically extracts and sanitizes video titles
- 🔁 **Retry Logic** - Auto-retry failed segments
- 🖥️ **Cross-platform** - Works on Windows, Linux, and macOS

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
git clone https://github.com/yourusername/ph-shorts.git
cd ph-shorts

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
╔═══════════════════════════════════════════════════════╗
║  ██████╗ ██╗  ██╗    ███████╗██╗  ██╗ ██████╗ ██████╗ ████████╗███████╗  ║
║  ██╔══██╗██║  ██║    ██╔════╝██║  ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝  ║
║  ██████╔╝███████║    ███████╗███████║██║   ██║██████╔╝   ██║   ███████╗  ║
║  ██╔═══╝ ██╔══██║    ╚════██║██╔══██║██║   ██║██╔══██╗   ██║   ╚════██║  ║
║  ██║     ██║  ██║    ███████║██║  ██║╚██████╔╝██║  ██║   ██║   ███████║  ║
║  ╚═╝     ╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝  ║
╚═══════════════════════════════════════════════════════╝
            Download PornHub Shorts with Style!
    version 1.0.0 • Lightweight & Beautiful CLI
```

### Command Line Mode (For power users)

```bash
ph-shorts "VIDEO_URL" [OPTIONS]
```

## 📝 Examples

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

### Combine options
```bash
ph-shorts "URL" -q 1080 -o "awesome_video.mp4" -p http://proxy:8080
```

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
- Python 3.8 or higher
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
