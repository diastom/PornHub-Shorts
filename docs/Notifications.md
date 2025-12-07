# 🔔 Desktop Notifications

RedLight v1.0.14 includes cross-platform desktop notifications.

## Platform Support

| Platform | Method |
|----------|--------|
| Windows | win10toast / winsound |
| macOS | terminal-notifier / afplay |
| Linux | notify-send |

## Quick Start

```python
from RedLight import GetNotifier

notifier = GetNotifier()

# Send notification
notifier.notify_download_complete(
    title="Video Downloaded!",
    filename="video.mp4",
    path="./downloads/video.mp4",
    quality="1080"
)

# Send failure notification
notifier.notify_download_failed(
    title="Download Error",
    url="https://example.com",
    error="Network timeout"
)
```

## NotificationManager

### Configuration

```python
from RedLight import GetNotifier

notifier = GetNotifier()

# Enable/disable notifications
notifier.config.enabled = True

# Enable/disable sound
notifier.config.sound_enabled = True

# Configure events
notifier.config.on_complete = True
notifier.config.on_error = True
notifier.config.on_pause = False
```

### Methods

| Method | Description |
|--------|-------------|
| `notify_download_complete(...)` | Video downloaded successfully |
| `notify_download_failed(...)` | Download error |
| `notify_download_paused(...)` | Download paused |
| `notify_batch_complete(...)` | Batch download finished |
| `send_notification(title, message)` | Custom notification |

### Example: Custom Notification

```python
from RedLight import GetNotifier

notifier = GetNotifier()
notifier.send_notification(
    title="RedLight DL",
    message="Your video is ready!"
)
```

## CLI Settings

Access via interactive mode → `8. Settings`:

```
5. Toggle Notifications   [ON/OFF]
6. Toggle Notification Sounds  [ON/OFF]
7. Test Notification
```

## Config File

Notification settings in `~/.RedLight/config.yaml`:

```yaml
notifications:
  enabled: true
  sound_enabled: true
  on_complete: true
  on_error: true
  on_pause: false
```

## See Also

- [Configuration Guide](Config.md)
- [API Functions](API.md)
