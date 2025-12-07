# ⏯️ Resume/Pause Downloads

RedLight v1.0.14 introduces pausable/resumable downloads with persistent state.

## Quick Start

```python
from RedLight import GetResumeManager

manager = GetResumeManager()

# Start a resumable download
download_id = manager.create_download(
    url="https://example.com/video",
    output_path="./downloads/video.mp4",
    quality="1080"
)

# Pause download
manager.pause_download(download_id)

# Resume later
manager.resume_download(download_id)

# Check status
state = manager.get_download_state(download_id)
print(f"Progress: {state.progress_percent:.1f}%")
```

## ResumeManager Class

### Methods

| Method | Description |
|--------|-------------|
| `create_download(url, output_path, ...)` | Create new download, returns ID |
| `update_progress(id, downloaded, total)` | Update download progress |
| `pause_download(id)` | Pause active download |
| `resume_download(id)` | Resume paused download |
| `cancel_download(id)` | Cancel download |
| `complete_download(id, path)` | Mark as completed |
| `fail_download(id, error)` | Mark as failed |
| `get_download_state(id)` | Get download state |
| `list_active_downloads()` | List downloading items |
| `list_paused_downloads()` | List paused items |
| `list_failed_downloads()` | List failed items |
| `should_continue(id)` | Check if should continue |

### DownloadState Properties

```python
state = manager.get_download_state(download_id)

state.download_id      # Unique ID
state.url              # Video URL
state.output_path      # Output file path
state.total_size       # Total bytes
state.downloaded_size  # Downloaded bytes
state.status           # pending/downloading/paused/completed/failed
state.progress_percent # 0-100 percentage
state.is_resumable     # Can be resumed?
```

## CLI Active Downloads Menu

Access via interactive mode → `7. Active Downloads`:

```
⏯️ Active Downloads Manager

Currently downloading:
  1. [abc123] Video Title - 45.2% (downloading)
  
Paused:
  2. [def456] Another Video - 23.1% (paused)

1. Resume Download
2. Pause Download
3. Cancel Download
4. Refresh List
5. Back
```

## Storage

Download states are persisted in SQLite:
```
~/.RedLight/downloads.db
```

States survive app restarts and can be resumed later.

## See Also

- [API Functions](API.md)
- [Classes Documentation](Classes.md)
