import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass
class ProxyConfig:
    enabled: bool = False
    http: str = ""
    https: str = ""
    
    def get_proxies(self) -> Optional[Dict[str, str]]:
        if not self.enabled:
            return None
        proxies = {}
        if self.http:
            proxies["http"] = self.http
        if self.https:
            proxies["https"] = self.https
        elif self.http:
            proxies["https"] = self.http
        return proxies if proxies else None


@dataclass
class DownloadConfig:
    default_quality: str = "best"
    output_directory: str = "./downloads"
    keep_original: bool = False
    max_concurrent: int = 3
    speed_limit: str = ""
    use_aria2c: bool = True
    aria2c_connections: int = 16
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass 
class NotificationConfig:
    enabled: bool = True
    sound_enabled: bool = True
    on_complete: bool = True
    on_error: bool = True
    on_batch_complete: bool = True


@dataclass
class UIConfig:
    show_speed: bool = True
    show_eta: bool = True
    show_progress_bar: bool = True
    color_output: bool = True


@dataclass
class Config:
    download: DownloadConfig = field(default_factory=DownloadConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "download": asdict(self.download),
            "proxy": asdict(self.proxy),
            "notifications": asdict(self.notifications),
            "ui": asdict(self.ui)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        config = cls()
        for section in ["download", "proxy", "notifications", "ui"]:
            if section in data:
                section_obj = getattr(config, section)
                for key, value in data[section].items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
        return config


class ConfigManager:
    DEFAULT_CONFIG_PATH = Path.home() / ".RedLight" / "config.yaml"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        self._config: Optional[Config] = None
    
    def get(self) -> Config:
        if self._config is None:
            self._config = self.load()
        return self._config
    
    def load(self) -> Config:
        if not self.config_path.exists():
            return Config()
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return Config.from_dict(data)
        except Exception:
            return Config()
    
    def save(self, config: Optional[Config] = None) -> bool:
        if config is None:
            config = self._config or Config()
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config.to_dict(), f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            self._config = config
            return True
        except Exception:
            return False
    
    def reset(self) -> Config:
        self._config = Config()
        self.save(self._config)
        return self._config
    
    def get_default_quality(self) -> str:
        return self.get().download.default_quality
    
    def get_output_directory(self) -> str:
        return self.get().download.output_directory
    
    def get_proxies(self) -> Optional[Dict[str, str]]:
        return self.get().proxy.get_proxies()
    
    def is_aria2c_enabled(self) -> bool:
        return self.get().download.use_aria2c
    
    def get_aria2c_connections(self) -> int:
        return self.get().download.aria2c_connections
    
    def get_retry_config(self) -> tuple:
        cfg = self.get().download
        return (cfg.retry_attempts, cfg.retry_delay)


_default_manager: Optional[ConfigManager] = None


def GetConfigManager() -> ConfigManager:
    global _default_manager
    if _default_manager is None:
        _default_manager = ConfigManager()
    return _default_manager


def GetConfig() -> Config:
    return GetConfigManager().get()


def SaveConfig(config: Optional[Config] = None) -> bool:
    return GetConfigManager().save(config)


def ResetConfig() -> Config:
    return GetConfigManager().reset()


DEFAULT_CONFIG_YAML = """# RedLight DL Configuration
download:
  default_quality: best
  output_directory: ./downloads
  keep_original: false
  max_concurrent: 3
  speed_limit: ""
  use_aria2c: true
  aria2c_connections: 16
  retry_attempts: 3
  retry_delay: 1.0

proxy:
  enabled: false
  http: ""
  https: ""

notifications:
  enabled: true
  sound_enabled: true
  on_complete: true
  on_error: true
  on_batch_complete: true

ui:
  show_speed: true
  show_eta: true
  show_progress_bar: true
  color_output: true
"""


def CreateDefaultConfig() -> str:
    config_path = ConfigManager.DEFAULT_CONFIG_PATH
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(DEFAULT_CONFIG_YAML, encoding='utf-8')
    return str(config_path)
