# 📚 RedLight API Documentation

Welcome to the complete API documentation for RedLight! This documentation will help you integrate RedLight into your Python projects.

## 📖 Documentation Structure

### Quick Start
- **[Quick Start Guide](QuickStart.md)** - Get started in 5 minutes
- **[Installation](QuickStart.md#installation)** - Installing RedLight

### Multi-Site Support
- **[Multi-Site Guide](MultiSite.md)** 🌐 - Complete guide for all 4 supported sites
  - PornHub, Eporner, Spankbang, XVideos
  - Simple and advanced examples
  - Multi-site search and batch downloads

### NEW in v1.0.14 ✨
- **[Configuration Guide](Config.md)** ⚙️ - YAML-based config system
- **[Resume/Pause Downloads](Resume.md)** ⏯️ - Pausable downloads with state persistence
- **[Desktop Notifications](Notifications.md)** 🔔 - Cross-platform notifications
- **[Download Statistics](Statistics.md)** 📊 - Comprehensive analytics

### API Reference
- **[API Functions](API.md)** - High-level helper functions
- **[Classes](Classes.md)** - Detailed class documentation
  - `VideoDownloader`, `BatchDownloader`, `PlaylistDownloader`
  - `ResumeManager`, `NotificationManager`, `DownloadStatistics` *(NEW)*
  - `Aria2cDownloader`, `PythonDownloader` *(NEW)*

### Guides & Examples
- **[Examples](Examples.md)** - Practical code examples
- **[Advanced Usage](Advanced.md)** - Advanced topics

## 🚀 Quick Example

```python
from RedLight import DownloadVideo, GetConfig

# Load config defaults
config = GetConfig()

# Download video (uses config defaults)
video_path = DownloadVideo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
print(f"Downloaded: {video_path}")
```

## 🆕 What's New in v1.0.14

| Feature | Description |
|---------|-------------|
| ⏯️ Resume/Pause | Pause downloads and resume later |
| ⚙️ Config File | YAML-based persistent settings |
| 🔔 Notifications | Desktop alerts on completion |
| 📊 Statistics | Comprehensive download analytics |
| ⚡ Aria2c | Multi-connection fast downloads |
| 📈 Speed/ETA | Real-time speed and ETA display |

## 📋 Table of Contents

1. [Quick Start Guide](QuickStart.md)
2. [Multi-Site Guide](MultiSite.md)
3. [Configuration Guide](Config.md) ⚙️ *NEW*
4. [Resume/Pause Downloads](Resume.md) ⏯️ *NEW*
5. [Desktop Notifications](Notifications.md) 🔔 *NEW*
6. [Download Statistics](Statistics.md) 📊 *NEW*
7. [API Functions Reference](API.md)
8. [Classes Documentation](Classes.md)
9. [Code Examples](Examples.md)
10. [Advanced Usage](Advanced.md)

## 🆘 Getting Help

- **GitHub Issues:** [Report bugs or request features](https://github.com/diastom/RedLightDL/issues)
- **Examples:** Check the [examples/](../examples/) directory

## 🔗 External Links

- [GitHub Repository](https://github.com/diastom/RedLightDL)
- [PyPI Package](https://pypi.org/project/ph-shorts/)
- [Changelog](../CHANGELOG.md)
