# 📚 PHShorts API Documentation

Welcome to the complete API documentation for PHShorts! This documentation will help you integrate PHShorts into your Python projects.

## 📖 Documentation Structure

### Quick Start
- **[Quick Start Guide](QuickStart.md)** - Get started in 5 minutes
- **[Installation](QuickStart.md#installation)** - Installing PHShorts

### API Reference
- **[API Functions](API.md)** - High-level helper functions (`DownloadVideo`, `GetVideoInfo`, etc.)
- **[Classes](Classes.md)** - Detailed class documentation
  - `VideoDownloader`
  - `BatchDownloader`
  - `PlaylistDownloader`
  - `VideoConverter`
  - `MetadataEditor`
  - `PornHubSearch`
  - `AsyncVideoDownloader`

### Guides & Examples
- **[Examples](Examples.md)** - Practical code examples for common use cases
- **[Advanced Usage](Advanced.md)** - Advanced topics and best practices

## 🚀 Quick Example

```python
from PHShorts import DownloadVideo

# Simple one-liner
video_path = DownloadVideo("https://www.pornhub.com/view_video.php?viewkey=xxxxx")
print(f"Downloaded: {video_path}")
```

## 📋 Table of Contents

1. [Quick Start Guide](QuickStart.md)
2. [API Functions Reference](API.md)
3. [Classes Documentation](Classes.md)
4. [Code Examples](Examples.md)
5. [Advanced Usage](Advanced.md)

## 🆘 Getting Help

- **GitHub Issues:** [Report bugs or request features](https://github.com/diastom/PornHub-Shorts/issues)
- **Examples:** Check the [examples/](../examples/) directory for working code

## 🔗 External Links

- [GitHub Repository](https://github.com/diastom/PornHub-Shorts)
- [PyPI Package](https://pypi.org/project/ph-shorts/)
- [Changelog](../CHANGELOG.md)
