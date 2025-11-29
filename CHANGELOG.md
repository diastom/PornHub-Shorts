# Release Notes - PH Shorts Downloader

## Version 1.0.7 (2025-11-29)

### 🎉 Major New Features

#### 📦 Batch Download System
- Download multiple videos concurrently or sequentially
- **CLI:** `ph-shorts --batch "url1, url2" --concurrent`
- **Interactive Menu:** Option 3 (Batch Download)
- Smart progress tracking for multiple files

#### 📺 Playlist & Channel Support
- Download entire channels, user uploads, or playlists
- **CLI:** `ph-shorts --channel "username" --limit 10`
- **Interactive Menu:** Option 4 (Download Channel/Playlist)
- Integrated with batch system for optimized performance

#### 🔍 Advanced Search & Filter
- Enhanced search with sorting and filtering
- **CLI:** `ph-shorts --search "query" --sort mostviewed --duration short`
- **Interactive Menu:** Option 2 (Search Videos)
- Sort by: Most Viewed, Top Rated, Newest
- Filter by: Short (<10m), Medium (10-20m), Long (>20m)

#### 🔄 Format Conversion & Compression
- Convert videos to MP4, WebM, MKV
- Video compression support (0-100 quality)
- Audio extraction (MP3)
- **CLI:** `ph-shorts "url" --format webm --compress 70 --audio-only`
- Optimized flow: Prevents double conversion (TS -> MP4 -> Target)

#### 🛠️ Enhanced Python API
- New `MetadataEditor` class for editing tags and thumbnails
- `PornHubSearch` class for programmatic searching
- Updated `DownloadVideo` to support `keep_ts` argument
- Full type hinting and documentation

### 🐛 Bug Fixes
- Fixed `TypeError` in `DownloadVideo` API (added `keep_ts` support)
- Fixed progress bar tracking in batch mode
- Fixed indentation issues in CLI module
- Resolved double-conversion inefficiency

### 📚 Documentation
- Updated README with comprehensive guides for all new features
- Added `examples/batch_advanced.py`


---

## Version 1.0.6 (2025-11-28)

### 🎉 Major New Features

#### Programmable API Support
PHShorts can now be used as a Python library! Build custom scripts, bots, and automation tools.

**New Modules:**
- `api.py` - High-level helper functions (PascalCase naming)
- `async_downloader.py` - Async support for bots

**Available Functions:**
```python
from PHShorts import (
    DownloadVideo,           # Simple one-liner downloads
    GetVideoInfo,            # Get metadata without downloading
    ListAvailableQualities,  # List available quality options
    VideoDownloader,         # Main downloader class
    AsyncVideoDownloader     # Async version for bots
)
```

**Use Cases:**
- Build Telegram/Discord bots
- Create batch download scripts
- Integrate into existing applications
- Progress tracking and custom workflows

### 📚 Documentation & Examples

- Added comprehensive API usage section in README
- Created 4 working example files:
  - `examples/basic_usage.py` - Simple download example
  - `examples/progress_tracking.py` - Progress bar implementation
  - `examples/telegram_bot.py` - Telegram bot integration
  - `examples/batch_download.py` - Batch downloads with error handling

### 🔄 Changes
- Updated `__init__.py` to export new API functions
- Version bumped to 1.0.6 throughout project
- **Naming Convention**: Functions use PascalCase (e.g., `DownloadVideo`)
- CLI functionality remains unchanged (full backward compatibility)

### 🐛 Bug Fixes
- None in this release (new features only)

---

## Version 1.0.5 (Previous)

See previous release notes for older versions.
