import sys
import click
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from .ui import show_banner, show_version, show_history, show_stats, console, db
from .interactive import interactive_mode, batch_download_interactive, channel_download_interactive, search_cli_mode
from .download import download_video, process_video_conversion
from ..search import PornHubSearch
from ..playlist import PlaylistDownloader
from ..batch import BatchDownloader
from ..converter import VideoConverter


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('url', required=False)
@click.option('-o', '--output', 
              help='Custom output filename', 
              default=None,
              metavar='FILE')
@click.option('-q', '--quality', 
              default='best', 
              help='Video quality: best, worst, 1080, 720, 480',
              metavar='QUALITY')
@click.option('-p', '--proxy', 
              help='HTTP/HTTPS proxy URL (e.g., http://127.0.0.1:1080)', 
              default=None,
              metavar='URL')
@click.option('--keep-ts', 
              is_flag=True, 
              help='Keep the original .ts file after conversion')
@click.option('--subs', 
              is_flag=True, 
              help='Download subtitles if available')
@click.option('--speed-limit',
              default=None,
              metavar='RATE',
              help='Limit download speed (e.g., 1M, 500K)')
@click.option('--format',
              default=None,
              metavar='FORMAT',
              help='Convert to format: mp4, webm, mkv (requires FFmpeg)')
@click.option('--compress',
              default=None,
              type=int,
              metavar='QUALITY',
              help='Compress video quality 0-100 (higher=better, requires FFmpeg)')
@click.option('--audio-only',
              is_flag=True,
              help='Extract audio as MP3 (requires FFmpeg)')
@click.option('--search',
              default=None,
              metavar='QUERY',
              help='Search videos and download')
@click.option('--sort',
              default='mostviewed',
              type=click.Choice(['mostviewed', 'toprated', 'newest'], case_sensitive=False),
              help='Sort search results')
@click.option('--duration',
              default=None,
              type=click.Choice(['short', 'medium', 'long'], case_sensitive=False),
              help='Filter search results by duration')
@click.option('--channel',
              default=None,
              metavar='TARGET',
              help='Download from channel/user (URL or name)')
@click.option('--limit',
              default=10,
              type=int,
              help='Max videos to download from channel (default: 10)')
@click.option('--batch',
              default=None,
              metavar='URLS',
              help='Batch download multiple videos (comma-separated URLs)')
@click.option('--concurrent',
              is_flag=True,
              help='Enable concurrent downloads for batch mode')
@click.option('--history',
              is_flag=True,
              callback=show_history,
              expose_value=False,
              help='Show download history and exit')
@click.option('--stats',
              is_flag=True,
              callback=show_stats,
              expose_value=False,
              help='Show download statistics and exit')
@click.option('-v', '--version',
              is_flag=True,
              callback=show_version,
              expose_value=False,
              is_eager=True,
              help='Show version information and exit')
def main(url, output, quality, proxy, keep_ts, subs, speed_limit, format, compress, audio_only, search, sort, duration, channel, limit, batch, concurrent):
    
    if search:
        search_cli_mode(search, sort_by=sort, duration=duration)
        return
    
    if channel:

        
        show_banner()
        console.print(f"\n[cyan]🔍 Scanning channel: {channel}...[/]")
        
        playlist = PlaylistDownloader()
        urls = playlist.GetChannelVideos(channel, limit=limit)
        
        if not urls:
            console.print("[red]❌ No videos found or channel does not exist[/]")
            return
            
        console.print(f"[green]✓ Found {len(urls)} videos[/]")
        
        console.print(f"\n[cyan]📦 Batch downloading {len(urls)} video(s)...[/]")
        console.print(f"[cyan]Mode:[/] {'Concurrent' if concurrent else 'Sequential'}\n")
        
        doing_conversion = format is not None or compress is not None or audio_only
        effective_keep_ts = keep_ts or doing_conversion
        
        downloader = BatchDownloader(
            concurrent=concurrent,
            max_workers=3 if concurrent else 1,
            quality=quality,
            keep_ts=effective_keep_ts
        )
        
        downloader.AddUrls(urls)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task(
                f"[cyan]Downloading {len(urls)} videos...",
                total=len(urls)
            )
            
            completed_count = 0
            
            def on_progress(completed, total, current_url):
                pass
            
            def on_complete(url, path):
                nonlocal completed_count
                completed_count += 1
                progress.update(task, completed=completed_count)
                progress.console.print(f"[green]✓[/] Downloaded: {Path(path).name}")
                
                if format or compress is not None or audio_only:
                    process_video_conversion(
                        video_path=path,
                        format=format,
                        compress=compress,
                        audio_only=audio_only,
                        keep_ts=keep_ts,
                        console=progress.console
                    )
            
            def on_error(url, error):
                nonlocal completed_count
                completed_count += 1
                progress.update(task, completed=completed_count)
                progress.console.print(f"[red]✗[/] Failed: {url[:50]}... - {str(error)[:80]}")
            
            results = downloader.DownloadAll(
                on_progress=on_progress,
                on_complete=on_complete,
                on_error=on_error
            )
        
        console.print(f"\n[bold green]✅ Channel Download Complete![/]")
        console.print(f"[cyan]Successfully downloaded:[/] {len(results)}/{len(urls)}")
        return

    if batch:
        urls = [url.strip() for url in batch.split(',') if url.strip()]
        
        if not urls:
            console.print("[red]❌ No valid URLs provided[/]")
            return
        
        show_banner()
        console.print(f"\n[cyan]📦 Batch downloading {len(urls)} video(s)...[/]")
        console.print(f"[cyan]Mode:[/] {'Concurrent' if concurrent else 'Sequential'}\n")

        
        doing_conversion = format is not None or compress is not None or audio_only
        effective_keep_ts = keep_ts or doing_conversion
        
        downloader = BatchDownloader(
            concurrent=concurrent,
            max_workers=3 if concurrent else 1,
            quality=quality,
            keep_ts=effective_keep_ts
        )
        
        downloader.AddUrls(urls)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task(
                f"[cyan]Downloading {len(urls)} videos...",
                total=len(urls)
            )
            
            completed_count = 0
            
            def on_progress(completed, total, current_url):
                pass
            
            def on_complete(url, path):
                nonlocal completed_count
                completed_count += 1
                progress.update(task, completed=completed_count)
                progress.console.print(f"[green]✓[/] Downloaded: {Path(path).name}")
                
                if doing_conversion:
                    process_video_conversion(
                        video_path=path,
                        format=format,
                        compress=compress,
                        audio_only=audio_only,
                        keep_ts=keep_ts,
                        console=progress.console
                    )
            
            def on_error(url, error):
                nonlocal completed_count
                completed_count += 1
                progress.update(task, completed=completed_count)
                progress.console.print(f"[red]✗[/] Failed: {url[:50]}... - {str(error)[:80]}")
            
            results = downloader.DownloadAll(
                on_progress=on_progress,
                on_complete=on_complete,
                on_error=on_error
            )
        
        console.print(f"\n[bold green]✅ Batch Download Complete![/]")
        console.print(f"[cyan]Successfully downloaded:[/] {len(results)}/{len(urls)}")
        return
    
    if not url:
        interactive_mode()
    else:
        show_banner()
        
        doing_conversion = format is not None or compress is not None or audio_only
        effective_keep_ts = keep_ts or doing_conversion
        
        video_path = download_video(url, output=output, quality=quality, proxy=proxy, keep_ts=effective_keep_ts, subs=subs, speed_limit=speed_limit)
        
        if doing_conversion:
            process_video_conversion(
                video_path=video_path,
                format=format,
                compress=compress,
                audio_only=audio_only,
                keep_ts=keep_ts,
                console=console
            )
