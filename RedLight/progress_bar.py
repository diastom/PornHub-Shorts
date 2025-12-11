import time
from typing import Optional, Callable

from rich.progress import (
    Progress, ProgressColumn, Task,
    BarColumn, TextColumn, TimeRemainingColumn,
    DownloadColumn, TransferSpeedColumn, SpinnerColumn
)
from rich.text import Text
from rich.console import Console


class SpeedColumn(ProgressColumn):
    
    def render(self, task: Task) -> Text:
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("--.-  B/s", style="cyan")
        return Text(format_speed(speed), style="cyan")


class ETAColumn(ProgressColumn):
    
    def render(self, task: Task) -> Text:
        remaining = task.time_remaining
        if remaining is None:
            return Text("--:--", style="yellow")
        return Text(format_eta(remaining), style="yellow")


class ProgressCallback:
    
    def __init__(self, on_progress: Optional[Callable[[int, int], None]] = None):
        self.on_progress = on_progress
        self.total = 0
        self.current = 0
        self._start_time = time.time()
        self._last_update = 0
        self._last_time = self._start_time
        self._speed = 0.0
    
    def update(self, current: int, total: int):
        self.current = current
        self.total = total
        
        now = time.time()
        elapsed = now - self._last_time
        
        if elapsed >= 0.5:
            delta = current - self._last_update
            self._speed = delta / elapsed if elapsed > 0 else 0
            self._last_update = current
            self._last_time = now
        
        if self.on_progress:
            self.on_progress(current, total)
    
    @property
    def speed(self) -> float:
        return self._speed
    
    @property
    def eta(self) -> Optional[float]:
        if self._speed <= 0 or self.total <= 0:
            return None
        remaining = self.total - self.current
        return remaining / self._speed
    
    @property
    def progress_percent(self) -> float:
        if self.total <= 0:
            return 0.0
        return (self.current / self.total) * 100


class EnhancedProgress:
    
    def __init__(self, console: Optional[Console] = None, show_speed: bool = True, show_eta: bool = True):
        self.console = console or Console()
        self.show_speed = show_speed
        self.show_eta = show_eta
        self._progress = None
        self._tasks = {}
    
    def __enter__(self):
        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ]
        
        if self.show_speed:
            columns.append(TransferSpeedColumn())
        if self.show_eta:
            columns.append(TimeRemainingColumn())
        columns.append(DownloadColumn())
        
        self._progress = Progress(*columns, console=self.console)
        self._progress.start()
        return self
    
    def __exit__(self, *args):
        if self._progress:
            self._progress.stop()
    
    def add_task(self, description: str, total: int = 100) -> int:
        task_id = self._progress.add_task(description, total=total)
        self._tasks[task_id] = {"start_time": time.time(), "last_update": 0}
        return task_id
    
    def update(self, task_id: int, completed: int = None, total: int = None, description: str = None):
        kwargs = {}
        if completed is not None:
            kwargs["completed"] = completed
        if total is not None:
            kwargs["total"] = total
        if description is not None:
            kwargs["description"] = description
        self._progress.update(task_id, **kwargs)
    
    def complete_task(self, task_id: int):
        task = self._progress.tasks[task_id]
        self._progress.update(task_id, completed=task.total)


def create_download_progress(console: Optional[Console] = None, show_speed: bool = True, show_eta: bool = True) -> Progress:
    columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="cyan", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ]
    
    if show_speed:
        columns.append(TransferSpeedColumn())
    if show_eta:
        columns.append(TimeRemainingColumn())
    columns.append(DownloadColumn())
    
    return Progress(*columns, console=console or Console())


def format_speed(bytes_per_sec: float) -> str:
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.1f} {unit}"
        bytes_per_sec /= 1024
    return f"{bytes_per_sec:.1f} TB/s"


def format_eta(seconds: float) -> str:
    if seconds < 0:
        return "--:--"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
