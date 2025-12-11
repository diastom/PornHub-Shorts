import sys
import subprocess
import shutil
import threading
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class NotificationConfig:
    enabled: bool = True
    sound_enabled: bool = True
    custom_sound_path: Optional[str] = None


class NotificationManager:
    
    def __init__(self, enabled=True, sound_enabled=True):
        self.config = NotificationConfig(enabled=enabled, sound_enabled=sound_enabled)
        self._platform = sys.platform
        self._notifier = self._detect_notifier()
    
    def _detect_notifier(self) -> str:
        if self._platform == "win32":
            try:
                from win10toast import ToastNotifier
                return "win10toast"
            except ImportError:
                pass
            try:
                from plyer import notification
                return "plyer"
            except ImportError:
                pass
            return "powershell"
        
        elif self._platform == "darwin":
            if shutil.which("terminal-notifier"):
                return "terminal-notifier"
            return "osascript"
        
        else:
            if shutil.which("notify-send"):
                return "notify-send"
            try:
                from plyer import notification
                return "plyer"
            except ImportError:
                pass
            return "none"
    
    @staticmethod
    def is_supported() -> bool:
        platform = sys.platform
        if platform == "win32":
            return True
        elif platform == "darwin":
            return True
        return shutil.which("notify-send") is not None
    
    def enable(self):
        self.config.enabled = True
    
    def disable(self):
        self.config.enabled = False
    
    def enable_sound(self):
        self.config.sound_enabled = True
    
    def disable_sound(self):
        self.config.sound_enabled = False
    
    def set_sound_file(self, path: Optional[str]):
        self.config.custom_sound_path = path
    
    def notify_download_complete(self, title: str, filename: str, path: str, quality: str = ""):
        if not self.config.enabled:
            return
        header = "✅ Download Complete!"
        msg = f"{title}\n{quality}p • {filename}" if quality else f"{title}\n{filename}"
        self._send_notification(header, msg, "success")
    
    def notify_download_failed(self, title: str, error: str, **kwargs):
        if not self.config.enabled:
            return
        self._send_notification("❌ Download Failed", f"{title}\n{error[:100]}", "error")
    
    def notify_download_paused(self, title: str, progress: float = 0):
        if not self.config.enabled:
            return
        self._send_notification("⏸️ Download Paused", f"{title}\nProgress: {progress:.1f}%", "info")
    
    def notify_batch_complete(self, total_count: int, success_count: int, failed_count: int = 0):
        if not self.config.enabled:
            return
        if failed_count > 0:
            header = "📦 Batch Download Complete"
            msg = f"Downloaded: {success_count}/{total_count}\nFailed: {failed_count}"
            notif_type = "warning"
        else:
            header = "✅ Batch Download Complete!"
            msg = f"Successfully downloaded {success_count} videos"
            notif_type = "success"
        self._send_notification(header, msg, notif_type)
    
    def notify_custom(self, title: str, message: str, notif_type: str = "info"):
        if not self.config.enabled:
            return
        self._send_notification(title, message, notif_type)
    
    def _send_notification(self, title: str, message: str, notif_type: str = "info"):
        thread = threading.Thread(
            target=self._send_notification_sync,
            args=(title, message, notif_type),
            daemon=True
        )
        thread.start()
    
    def _send_notification_sync(self, title: str, message: str, notif_type: str):
        try:
            if self._notifier == "win10toast":
                self._notify_win10toast(title, message)
            elif self._notifier == "plyer":
                self._notify_plyer(title, message)
            elif self._notifier == "powershell":
                self._notify_powershell(title, message)
            elif self._notifier == "terminal-notifier":
                self._notify_terminal_notifier(title, message)
            elif self._notifier == "osascript":
                self._notify_osascript(title, message)
            elif self._notifier == "notify-send":
                self._notify_linux(title, message)
            
            if self.config.sound_enabled:
                self._play_sound(notif_type)
        except Exception:
            pass
    
    def _notify_win10toast(self, title: str, message: str):
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5, threaded=True)
        except Exception:
            self._notify_powershell(title, message)
    
    def _notify_plyer(self, title: str, message: str):
        from plyer import notification
        notification.notify(title=title, message=message, app_name="RedLight DL", timeout=5)
    
    def _notify_powershell(self, title: str, message: str):
        title = title.replace("'", "''").replace('"', '`"')
        message = message.replace("'", "''").replace('"', '`"').replace("\n", "`n")
        
        script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        
        $template = @"
        <toast>
            <visual>
                <binding template="ToastText02">
                    <text id="1">{title}</text>
                    <text id="2">{message}</text>
                </binding>
            </visual>
        </toast>
"@
        
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("RedLight DL").Show($toast)
        '''
        
        try:
            subprocess.run(["powershell", "-Command", script], capture_output=True, timeout=5)
        except Exception:
            pass
    
    def _notify_terminal_notifier(self, title: str, message: str):
        subprocess.run([
            "terminal-notifier", "-title", title, "-message", message, "-appIcon", "📥"
        ], capture_output=True)
    
    def _notify_osascript(self, title: str, message: str):
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], capture_output=True)
    
    def _notify_linux(self, title: str, message: str):
        subprocess.run(["notify-send", "-a", "RedLight DL", title, message], capture_output=True)
    
    def _play_sound(self, notif_type: str):
        if self.config.custom_sound_path:
            self._play_custom_sound(self.config.custom_sound_path)
            return
        
        if self._platform == "win32":
            self._play_windows_sound(notif_type)
        elif self._platform == "darwin":
            self._play_macos_sound(notif_type)
    
    def _play_windows_sound(self, notif_type: str):
        try:
            import winsound
            sounds = {
                "success": winsound.MB_OK,
                "error": winsound.MB_ICONHAND,
                "warning": winsound.MB_ICONEXCLAMATION,
                "info": winsound.MB_ICONASTERISK
            }
            winsound.MessageBeep(sounds.get(notif_type, winsound.MB_OK))
        except Exception:
            pass
    
    def _play_macos_sound(self, notif_type: str):
        sounds = {"success": "Glass", "error": "Basso", "warning": "Sosumi", "info": "Pop"}
        sound = sounds.get(notif_type, "Pop")
        try:
            subprocess.run([
                "afplay", f"/System/Library/Sounds/{sound}.aiff"
            ], capture_output=True, timeout=2)
        except Exception:
            pass
    
    def _play_custom_sound(self, sound_path: str):
        if not Path(sound_path).exists():
            return
        try:
            if self._platform == "win32":
                import winsound
                winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            elif self._platform == "darwin":
                subprocess.run(["afplay", sound_path], capture_output=True, timeout=5)
            else:
                for player in ["paplay", "aplay", "mpv"]:
                    if shutil.which(player):
                        subprocess.run([player, sound_path], capture_output=True, timeout=5)
                        break
        except Exception:
            pass


_default_notifier: Optional[NotificationManager] = None


def GetNotifier() -> NotificationManager:
    global _default_notifier
    if _default_notifier is None:
        _default_notifier = NotificationManager()
    return _default_notifier
