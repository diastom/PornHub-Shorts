# Release Notes - RedLight DL

## Version 1.0.15 (2025-12-11)

### 🎉 New Site Support

#### xHamster.com ⭐
- **Full Integration**: Download videos from xHamster with multi-quality selection
- **HLS Streaming**: Uses CustomHLSDownloader for reliable downloads
- **Geo-Fallback**: Automatic domain fallback (xhamster2.com, xhamster.desi) for geo-restricted regions
- **Quality Options**: 144p, 240p, 480p, 720p, 1080p
- **Search Support**: Full search with pagination

#### XNXX.com ⭐
- **Full Integration**: Download videos from XNXX with quality selection
- **Same Structure as XVideos**: Uses html5player API pattern
- **Quality Options**: Low, High, HLS Adaptive
- **Search Support**: Full search with pagination

### 📦 New Modules
- `sites/xhamster.py` - xHamster downloader and search
- `sites/xnxx.py` - XNXX downloader and search

### 🔧 Changes
- Site count increased from 4 to 6
- Updated README.md with new sites
- Updated docs/QuickStart.md and docs/MultiSite.md
- Updated examples with new site references
- All existing code continues to work (backward compatible)

### 📝 Supported Sites (6 Total)
- **PornHub** - HLS streaming downloads
- **Eporner** - Direct MP4 with aria2c
- **Spankbang** - Hybrid MP4/HLS with 4K support
- **XVideos** - Multi-quality MP4/HLS
- **xHamster** - HLS with geo-fallback (NEW)
- **XNXX** - Multi-quality MP4/HLS (NEW)

---

## Version 1.0.14 (2025-12-07)

### 🎉 Major New Features

#### ⏯️ Resume/Pause Downloads
- **Pausable Downloads**: Pause active downloads and resume them later
- **Resume Manager**: New `ResumeManager` class with persistent state in SQLite
- **API Functions**:
  - `StartResumableDownload()` - Start a download and get a download ID
  - `PauseDownload()` - Pause an active download
  - `ResumeDownload()` - Resume a paused download
  - `CancelDownload()` - Cancel and remove download state
  - `GetActiveDownloads()` - List currently downloading items
  - `GetPausedDownloads()` - List paused downloads

#### 📜 Enhanced Download History
- **Extended Metadata**: Now tracks site, file size, duration, and status
- **Filter by Site**: View history filtered by specific site
- **Export Support**: Export history to JSON or CSV
- **Clear History**: Clear all or old entries
- **API Functions**:
  - `GetDownloadHistory()` - Get history with optional filters
  - `ClearDownloadHistory()` - Clear history entries
  - `ExportHistory()` - Export to JSON/CSV

#### 🔔 Desktop Notifications
- **Cross-Platform**: Supports Windows, macOS, and Linux
- **Sound Alerts**: Optional notification sounds
- **Customizable**: Enable/disable notifications and sounds
- **API Functions**:
  - `EnableNotifications()` - Toggle notifications on/off
  - `SetNotificationSound()` - Custom notification sound
  - `SendNotification()` - Send custom notifications

#### 📊 Advanced Statistics
- **Statistics Dashboard**: Comprehensive view of all download stats
- **Per-Site Breakdown**: Downloads, size, and quality per site
- **Quality Distribution**: Visual breakdown of quality choices
- **Download Timeline**: Daily download counts chart
- **Search Statistics**: Most searched queries
- **API Functions**:
  - `GetStatistics()` - Get summary statistics
  - `GetStatsBySite()` - Stats grouped by site
  - `GetStatsByQuality()` - Stats grouped by quality
  - `GetStatsByDate()` - Daily download counts

#### ⚙️ Configuration File (NEW)
- **YAML-Based Config**: `~/.RedLight/config.yaml` for persistent settings
- **Default Quality**: Set default quality (best, 1080, 720, etc.)
- **Download Directory**: Configure default output path
- **Proxy Settings**: HTTP/HTTPS proxy configuration
- **Aria2c Settings**: Enable/disable, connection count
- **API Functions**:
  - `get_config()` / `save_config()` - Load/save configuration
  - `reset_config()` - Reset to defaults
  - `create_default_config()` - Create config file

#### ⚡ Speed Improvements (NEW)
- **Aria2c Integration**: Multi-connection downloads for all sites
- **Smart Retry**: Exponential backoff with jitter for reliability
- **Faster Downloads**: Up to 16 parallel connections with aria2c
- **Python Fallback**: Multi-threaded Python downloader when aria2c unavailable
- **API Classes**:
  - `Aria2cDownloader` - High-speed aria2c-based downloads
  - `PythonDownloader` - Multi-threaded Python fallback
  - `smart_retry()` decorator - Exponential backoff retry

### 🖥️ CLI Enhancements

#### Progress Bar Improvements (NEW)
- **Download Speed**: Real-time transfer speed display (KB/s, MB/s)
- **ETA Display**: Estimated time remaining
- **File Size**: Total and downloaded size in progress bar
- **Completion Stats**: Total time and average speed on success

#### New Main Menu (9 Options)
```
1. Download Video
2. Search Videos
3. Batch Download Multiple Videos
4. Download Channel/Playlist
5. View History        ← Enhanced with export/clear
6. View Statistics     ← Enhanced with dashboard
7. Active Downloads    ← NEW (Resume/Pause)
8. Settings            ← NEW (Full config management)
9. Exit
```

#### Enhanced Settings Menu
1. Set Default Quality
2. Set Download Directory
3. Configure Proxy
4. Toggle Aria2c (Fast Downloads)
5. Toggle Notifications
6. Toggle Notification Sounds
7. Test Notification
8. Open Config File Location
9. Reset to Defaults
10. View App Info

### 📦 New Modules
- `resume_manager.py` - Pausable/resumable download management
- `notifications.py` - Cross-platform desktop notifications
- `statistics.py` - Advanced download analytics
- `config.py` - YAML configuration management
- `retry.py` - Smart retry with exponential backoff
- `aria2_downloader.py` - Aria2c/multi-threaded downloads
- `progress_bar.py` - Enhanced progress with speed/ETA

### 🔧 Changes
- Enhanced `database.py` with new columns (site, file_size, duration, status)
- Extended `api.py` with 25+ new API functions
- Updated `__init__.py` with all new exports
- CLI interactive mode expanded from 7 to 9 menu options
- CLI download shows speed, ETA, file size, and completion stats
- Settings menu expanded from 5 to 11 options
- Version bumped to 1.0.14

### 📝 Migration Notes
No breaking changes! All existing code continues to work.
New features are additive and opt-in.


---

## Version 1.0.10 (2025-01-30) - Hotfix

### 🐛 Bug Fixes
- **CLI Download Fix**: Fixed CLI `download_video()` to use multi-site API instead of direct HLS downloader
- Eporner downloads now work correctly in CLI interactive mode
- Auto-detection properly applied to all CLI download flows

### 📝 Notes
This is a critical hotfix for v1.0.9. Users on 1.0.9 should upgrade immediately.

---

## Version 1.0.9 (2025-01-30)

### 🎉 Multi-Site Support

#### New Architecture
- **Site Registry System**: Scalable architecture for supporting multiple adult content sites
- **Automatic Site Detection**: URLs automatically detected and routed to appropriate downloader
- **Base Classes**: `BaseSiteDownloader` and `BaseSiteSearch` for easy integration of new sites

#### Eporner.com Support ⭐
- **Full Integration**: Download videos from eporner.com with quality selection
- **MP4 Downloads**: Direct MP4 downloads using aria2c or multi-threaded Python downloader
- **Search Support**: Web scraping-based search with sorting (views, rating, date)
- **Quality Detection**: Automatic detection of 240p to 2160p including AV1 variants

#### Enhanced Search
- **Multi-Site Search Menu**: New site selection in interactive CLI
  - Search PornHub
  - Search Eporner
  - Search in All Sites (concurrent search across all supported sites)
- **Search History Database**: Track searches with site, query, and result count
- **Database Schema**: New `search_history` table

#### API Enhancements
- **Multi-Site API**: All API functions support multiple sites via auto-detection
  - `DownloadVideo()` - Works with any supported site URL
  - `GetVideoInfo()` - Returns site field
  - `ListAvailableQualities()` - Works across all sites
- **MultiSiteSearch**: New class for concurrent multi-site searching
- **Async Support**: Full multi-site support in `AsyncVideoDownloader`
- **Batch Downloads**: Mixed URLs from different sites in one batch

#### Supported Sites
- **PornHub**: HLS streaming downloads
- **Eporner**: Direct MP4 downloads

### 🔧 Changes
- PornHub wrapped in new `PornHubDownloader` class
- Full backward compatibility maintained
- Version bumped to 1.0.9

### 📝 Migration Notes
No breaking changes! All existing code continues to work.

---

## Version 1.0.8 (2025-11-29)

### 🎨 Project Rebranding

#### Complete Package Rename
- **Package name changed:** `PHShorts` → `RedLight`
- **Project renamed:** "PH Shorts Downloader" → "RedLight DL"
- **Repository URL:** `PornHub-Shorts` → `RedLightDL`
- **Reason:** Expanding to support multiple adult content platforms

#### Updated Branding
- ✨ New "REDLIGHT" ASCII banner in CLI
- 📝 Updated all documentation and examples
- 🔗 All GitHub links point to new repository
- 📦 Package metadata updated to "RedLight Team"

#### Import Changes
**Before (v1.0.7):**
```python
from PHShorts import DownloadVideo
```

**After (v1.0.8):**
```python
from RedLight import DownloadVideo
```

#### What Stayed the Same
- ✅ CLI command: `ph-shorts` (unchanged)
- ✅ PyPI package name: `ph-shorts` (unchanged)
- ✅ All functionality works identically
- ✅ No breaking changes to API structure

### 📚 Documentation Updates
- Updated README with rebranding notice
- Updated all documentation files (6 files in `docs/`)
- Updated all code examples
- Added migration note for existing users

---

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
RedLight can now be used as a Python library! Build custom scripts, bots, and automation tools.

**New Modules:**
- `api.py` - High-level helper functions (PascalCase naming)
- `async_downloader.py` - Async support for bots

**Available Functions:**
```python
from RedLight import (
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
