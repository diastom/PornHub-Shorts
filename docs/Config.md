# ⚙️ Configuration Guide

RedLight v1.0.14 introduces a YAML-based configuration system for persistent settings.

## Config File Location

```
~/.RedLight/config.yaml
```
- **Windows**: `C:\Users\<username>\.RedLight\config.yaml`
- **Linux/macOS**: `~/.RedLight/config.yaml`

## Quick Start

```python
from RedLight import GetConfig, SaveConfig, ResetConfig

# Get current config
config = GetConfig()
print(f"Default quality: {config.download.default_quality}")

# Modify and save
config.download.default_quality = "1080"
SaveConfig(config)
```

## Config Structure

```yaml
download:
  default_quality: "best"      # best, 1080, 720, 480, worst
  output_dir: "./downloads"
  use_aria2c: true             # Use aria2c for faster downloads
  aria2c_connections: 16       # Number of connections

retry:
  max_retries: 3
  base_delay: 1.0              # Seconds
  max_delay: 30.0

proxy:
  enabled: false
  http: ""
  https: ""

notifications:
  enabled: true
  sound_enabled: true
  on_complete: true
  on_error: true

ui:
  show_progress: true
  show_speed: true
  show_eta: true
```

## API Functions

### GetConfig()
Get current configuration (creates default if not exists).

```python
from RedLight import GetConfig

config = GetConfig()
print(config.download.default_quality)
print(config.notifications.enabled)
```

### SaveConfig(config)
Save configuration to file.

```python
from RedLight import GetConfig, SaveConfig

config = GetConfig()
config.download.use_aria2c = True
config.notifications.sound_enabled = False
SaveConfig(config)
```

### ResetConfig()
Reset configuration to defaults.

```python
from RedLight import ResetConfig

ResetConfig()
print("Config reset to defaults!")
```

### CreateDefaultConfig()
Create default config file (overwrites existing).

```python
from RedLight import CreateDefaultConfig

CreateDefaultConfig()
```

## CLI Settings Menu

Access via interactive mode → `8. Settings`:

```
⚙️ Settings
1. Set Default Quality
2. Set Download Directory
3. Configure Proxy
4. Toggle Aria2c (Fast Downloads)
5. Toggle Notifications
6. Toggle Notification Sounds
7. Test Notification
8. Open Config File Location
9. Reset to Defaults
```

## Aria2c Integration

For faster downloads, install aria2c:

```bash
# Windows (Chocolatey)
choco install aria2

# macOS
brew install aria2

# Linux
sudo apt install aria2
```

When aria2c is available and enabled:
- Downloads use up to 16 parallel connections
- Significantly faster for large files
- Automatic fallback to Python downloader if unavailable

## See Also

- [API Functions](API.md)
- [Advanced Usage](Advanced.md)
