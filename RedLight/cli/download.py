import sys
import shutil
import time
from pathlib import Path
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn, 
    TimeRemainingColumn, DownloadColumn, TransferSpeedColumn
)
from rich.panel import Panel
from rich import box
import traceback
from .ui import console, db
from ..sites import SiteRegistry
from ..api import GetVideoInfo, DownloadVideo
from ..converter import VideoConverter
from ..config import GetConfig
from ..notifications import GetNotifier


def process_video_conversion(video_path, format=None, compress=None, audio_only=False, keep_ts=False, console=None):
    if not (format or compress is not None or audio_only):
        return video_path
        
    if not console:
        from .ui import console as default_console
        console = default_console

    try:
        if not VideoConverter.IsFFmpegAvailable():
            console.print("[red]❌ FFmpeg not found! Conversion features require FFmpeg.[/]")
            console.print("[yellow]Install FFmpeg to use --format, --compress, or --audio-only[/]")
            return video_path
        
        converter = VideoConverter()
        console.print(f"  [dim]Processing: {Path(video_path).name}...[/]")
        
        converted_path = converter.Convert(
            input_file=video_path,
            output_format=format if format else "mp4",
            compress_quality=compress,
            audio_only=audio_only
        )
        
        console.print(f"  [green]✓[/] Converted: {Path(converted_path).name}")
        
        if not keep_ts and Path(video_path) != Path(converted_path):
            try:
                Path(video_path).unlink()
            except Exception:
                pass
                
        return converted_path
        
    except Exception as e:
        console.print(f"  [red]Conversion failed: {e}[/]")
        return video_path


def download_video(url, output=None, quality=None, proxy=None, keep_ts=False, subs=False, speed_limit=None):
    
    try:
        config = GetConfig()
        
        if quality is None:
            quality = config.download.default_quality
        
        if proxy is None:
            proxies = config.proxy.get_proxies()
            if proxies:
                proxy = proxies.get('http') or proxies.get('https')
        
        if speed_limit is None and config.download.speed_limit:
            speed_limit = config.download.speed_limit
        
        output_dir = config.download.output_directory
        show_speed = config.ui.show_speed
        show_eta = config.ui.show_eta
        
        with console.status("[bold cyan]🔍 Detecting site and fetching video information...", spinner="dots"):
            registry = SiteRegistry()
            site_name = registry.detect_site(url)
            
            if not site_name:
                raise ValueError("Unsupported URL. Please use a PornHub, Eporner, SpankBang, or XVideos link.")
            
            info = GetVideoInfo(url)
        
        console.print(f"[green]✓[/] Site: [bold]{site_name.title()}[/]")
        console.print(f"[green]✓[/] Video: [bold]{info['title']}[/]")
        console.print(f"[green]✓[/] Available Qualities: [bold]{', '.join([f'{q}p' for q in info['available_qualities']])}[/]")
        
        if quality == 'best':
            selected_q = max(info['available_qualities'])
        elif quality == 'worst':
            selected_q = min(info['available_qualities'])
        else:
            try:
                req_q = int(quality)
                selected_q = min(info['available_qualities'], key=lambda x: abs(x - req_q))
            except:
                selected_q = max(info['available_qualities'])
        
        console.print(f"[green]✓[/] Selected Quality: [bold]{selected_q}p[/]")
        
        if proxy:
            console.print(f"[green]✓[/] Proxy: [bold]{proxy}[/]")
        
        if speed_limit:
            console.print(f"[green]✓[/] Speed Limit: [bold]{speed_limit}[/]")
        
        console.print("\n[bold cyan]📥 Starting download...[/]")
        
        if site_name == "eporner":
            original_which = shutil.which
            def mock_which(cmd):
                if cmd == "aria2c":
                    return None
                return original_which(cmd)
            
            shutil.which = mock_which
        
        start_time = time.time()
        last_update = [0]
        last_time = [start_time]
        current_speed = [0.0]
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="cyan", finished_style="green"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("[cyan]{task.completed}/{task.total} segments[/]"),
                console=console
            ) as progress:
                
                task_id = None
                
                def on_progress(current, total):
                    nonlocal task_id
                    if task_id is None:
                        task_id = progress.add_task(f"[cyan]Downloading {selected_q}p", total=total)
                    progress.update(task_id, completed=current)
                
                result_path = DownloadVideo(
                    url=url,
                    output_dir=output_dir,
                    quality=quality,
                    filename=output,
                    keep_ts=keep_ts,
                    proxy=proxy,
                    on_progress=on_progress
                )
        finally:
            if site_name == "eporner":
                shutil.which = original_which
        
        total_time = time.time() - start_time
        file_size = Path(result_path).stat().st_size if Path(result_path).exists() else 0
        avg_speed = file_size / total_time if total_time > 0 else 0
        
        def format_speed(bps):
            for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
                if bps < 1024:
                    return f"{bps:.1f} {unit}"
                bps /= 1024
            return f"{bps:.1f} TB/s"
        
        def format_size(size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        
        console.print()
        success_panel = Panel(
            f"[bold green]✓ Download Successful![/]\n\n"
            f"[cyan]Site:[/] [bold white]{site_name.title()}[/]\n"
            f"[cyan]Title:[/] [bold white]{info['title']}[/]\n"
            f"[cyan]Quality:[/] [bold white]{selected_q}p[/]\n"
            f"[cyan]Size:[/] [bold white]{format_size(file_size)}[/]\n"
            f"[cyan]Time:[/] [bold white]{total_time:.1f}s[/]\n"
            f"[cyan]Speed:[/] [bold white]{format_speed(avg_speed)}[/]\n"
            f"[cyan]File:[/] [bold white]{Path(result_path).name}[/]\n"
            f"[cyan]Location:[/] [dim]{Path(result_path).absolute()}[/]",
            title="[bold green]Success[/]",
            border_style="green",
            box=box.DOUBLE
        )
        console.print(success_panel)
        
        db.add_entry(
            url=url,
            title=info['title'],
            filename=result_path,
            quality=selected_q,
            site=site_name,
            file_size=file_size
        )
        
        if config.notifications.enabled and config.notifications.on_complete:
            try:
                GetNotifier().notify_download_complete(
                    title=info['title'],
                    filename=Path(result_path).name,
                    path=str(result_path),
                    quality=str(selected_q)
                )
            except Exception:
                pass
        
        return result_path
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Download cancelled by user[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/] {str(e)}")
        
        try:
            config = GetConfig()
            if config.notifications.enabled and config.notifications.on_error:
                GetNotifier().notify_download_failed(
                    title="Download Failed",
                    url=url,
                    error=str(e)
                )
        except Exception:
            pass
        
        console.print(f"[dim]{traceback.format_exc()}[/]")
        sys.exit(1)
