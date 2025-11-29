
"""
CLI interface for PH Shorts Downloader using Rich and Click
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from rich.text import Text
from rich.markdown import Markdown
from pathlib import Path

from .downloader import CustomHLSDownloader
from .database import DatabaseManager
from . import __version__, __description__, __author__

console = Console()
db = DatabaseManager()

BANNER = """
[bold cyan]╔════════════════════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold magenta]██████╗ ██╗  ██╗    ███████╗██╗  ██╗ ██████╗ ██████╗ ████████╗███████╗[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔══██╗██║  ██║    ██╔════╝██║  ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██████╔╝███████║    ███████╗███████║██║   ██║██████╔╝   ██║   ███████╗[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔═══╝ ██╔══██║    ╚════██║██╔══██║██║   ██║██╔══██╗   ██║   ╚════██║[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██║     ██║  ██║    ███████║██║  ██║╚██████╔╝██║  ██║   ██║   ███████║[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]╚═╝     ╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝[/]  [bold cyan]║[/]
[bold cyan]╚════════════════════════════════════════════════════════════════════════════╝[/]
            [bold yellow]Download PornHub Shorts with Style![/]
    [dim]version 1.0.6 • Simple & Light[/]
"""


def show_banner():
    """Display the awesome banner"""
    console.print(BANNER)


def show_version(ctx, param, value):
    """Display version information"""
    if not value or ctx.resilient_parsing:
        return
    
    version_info = Panel(
        f"[bold cyan]PH Shorts Downloader[/]\n\n"
        f"[yellow]Version:[/] [bold white]{__version__}[/]\n"
        f"[yellow]Author:[/] [bold white]{__author__}[/]\n"
        f"[yellow]Description:[/] [dim]{__description__}[/]\n\n"
        f"[dim]For more information, visit:[/]\n"
        f"[link=https://github.com/diastom/PornHub-Shorts]https://github.com/diastom/PornHub-Shorts[/]",
        title="[bold magenta]📦 Package Info[/]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(version_info)
    ctx.exit()


def show_history(ctx, param, value):
    """Display download history"""
    if not value or ctx.resilient_parsing:
        return
    db.show_history(console)
    ctx.exit()


def show_stats(ctx, param, value):
    """Display download statistics"""
    if not value or ctx.resilient_parsing:
        return
    db.show_stats(console)
    ctx.exit()



def interactive_mode():
    """Interactive mode with beautiful prompts"""
    show_banner()
    
    while True:
        console.print("\n[bold cyan]📌 Main Menu:[/]")
        console.print("1. [bold green]Download Video[/]")
        console.print("2. [bold blue]Search Videos[/]")
        console.print("3. [bold orange1]Batch Download Multiple Videos[/]")
        console.print("4. [bold yellow]Download Channel/Playlist[/]")
        console.print("5. [bold magenta]View History[/]")
        console.print("6. [bold white]View Statistics[/]")
        console.print("7. [bold red]Exit[/]")
        
        choice = Prompt.ask("\n   Select an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")
        
        if choice == "1":
            # Get URL
            url = Prompt.ask("\n[bold green]🔗 Enter Video URL[/]")
            if not url:
                continue
            
            # Quality Selection
            console.print("\n[bold yellow]📺 Select Quality:[/]")
            quality_table = Table(show_header=False, box=box.SIMPLE)
            quality_table.add_column("Option", style="cyan", width=12)
            quality_table.add_column("Description", style="white")
            
            quality_table.add_row("1", "🏆 Best Available (Recommended)")
            quality_table.add_row("2", "📺 1080p")
            quality_table.add_row("3", "📱 720p")
            quality_table.add_row("4", "💾 480p")
            quality_table.add_row("5", "📉 Lowest Available (Data Saver)")
            
            console.print(quality_table)
            
            q_choice = Prompt.ask("   Your choice", choices=["1", "2", "3", "4", "5"], default="1")
            quality_map = {'1': 'best', '2': '1080', '3': '720', '4': '480', '5': 'worst'}
            quality = quality_map[q_choice]
            
            # Proxy
            proxy = None
            if Confirm.ask("\n[bold yellow]🌐 Use Proxy?[/]", default=False):
                proxy = Prompt.ask("   [cyan]Enter Proxy URL (e.g., http://127.0.0.1:2080)[/]")
                if not proxy.startswith("http"):
                    proxy = f"http://{proxy}"
                    
            # Custom Output
            output = None
            if Confirm.ask("\n[bold yellow]💾 Custom Output Filename?[/]", default=False):
                output = Prompt.ask("   [cyan]Enter filename (e.g., video.mp4)[/]")

            # Keep TS
            keep_ts = Confirm.ask("\n[bold yellow]📦 Keep original .ts file?[/]", default=False)

            # Subtitles
            subs = Confirm.ask("\n[bold yellow]📝 Download Subtitles?[/]", default=False)
            
            # Speed Limit
            speed_limit = None
            if Confirm.ask("\n[bold yellow]⚡ Limit download speed?[/]", default=False):
                speed_limit = Prompt.ask("   [cyan]Enter speed limit (e.g., 1M, 500K)[/]")
            
            # Start download
            download_video(url, output=output, quality=quality, proxy=proxy, keep_ts=keep_ts, subs=subs, speed_limit=speed_limit)
            
            if not Confirm.ask("\n[bold cyan]Do you want to continue?[/]", default=True):
                console.print("[bold green]Goodbye! 👋[/]")
                break
                
        elif choice == "2":
            from .search import PornHubSearch
            searcher = PornHubSearch()
            searcher.interactive_search()
            
        elif choice == "3":
            # Batch Download
            batch_download_interactive()
            
        elif choice == "4":
            # Playlist/Channel Download
            channel_download_interactive()
            
        elif choice == "5":
            db.show_history(console)
            Prompt.ask("\n[dim]Press Enter to return to menu...[/]")
            
        elif choice == "6":
            db.show_stats(console)
            Prompt.ask("\n[dim]Press Enter to return to menu...[/]")
            
        elif choice == "7":
            console.print("[bold green]Goodbye! 👋[/]")
            break


def batch_download_interactive():
    """Interactive batch download with progress tracking"""
    console.print("\n[bold cyan]📦 Batch Download Multiple Videos[/]")
    
    # Get URLs
    urls_input = Prompt.ask("\n[bold green]🔗 Enter Video URLs (separated by commas)[/]")
    if not urls_input:
        return
    
    # Parse URLs
    urls = [url.strip() for url in urls_input.split(',') if url.strip()]
    
    if not urls:
        console.print("[red]❌ No valid URLs provided[/]")
        return
    
    console.print(f"\n[cyan]Found {len(urls)} URL(s)[/]")
    
    # Download mode selection
    console.print("\n[bold yellow]📥 Download Mode:[/]")
    console.print("1. Sequential (one-by-one) - Slower but more stable")
    console.print("2. Concurrent (simultaneous) - Faster but uses more resources")
    
    mode_choice = Prompt.ask("   Select mode", choices=["1", "2"], default="1")
    concurrent = mode_choice == "2"
    
    if concurrent:
        max_workers = int(Prompt.ask(
            "   [cyan]Max concurrent downloads[/]",
            default="3"
        ))
    else:
        max_workers = 1
    
    # Quality selection
    console.print("\n[bold yellow]📺 Select Quality:[/]")
    q_choice = Prompt.ask(
        "   Quality (best/1080/720/480/worst)",
        default="best"
    )
    
    # Start batch download
    from .batch import BatchDownloader
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    
    console.print(f"\n[bold cyan]🚀 Starting {'concurrent' if concurrent else 'sequential'} download...[/]\n")
    
    downloader = BatchDownloader(
        concurrent=concurrent,
        max_workers=max_workers if concurrent else 1,
        quality=q_choice
    )
    
    downloader.AddUrls(urls)
    
    results = {}
    errors = {}
    
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
        
        def on_progress_callback(completed, total, current_url):
            # This gets called during download
            pass  # We'll update in on_complete instead
        
        def on_complete_callback(url, path):
            nonlocal completed_count
            results[url] = path
            completed_count += 1
            progress.update(task, completed=completed_count)
            progress.console.print(f"[green]✓[/] Downloaded: {Path(path).name}")
        
        def on_error_callback(url, error):
            nonlocal completed_count
            errors[url] = error
            completed_count += 1
            progress.update(task, completed=completed_count)
            progress.console.print(f"[red]✗[/] Failed: {url[:50]}... - {str(error)[:100]}")
        
        downloaded = downloader.DownloadAll(
            on_progress=on_progress_callback,
            on_complete=on_complete_callback,
            on_error=on_error_callback
        )
    
    # Summary
    console.print(f"\n[bold green]✅ Batch Download Complete![/]")
    console.print(f"[cyan]Successfully downloaded:[/] {len(results)}/{len(urls)}")
    if errors:
        console.print(f"[red]Failed:[/] {len(errors)}/{len(urls)}")
    
    Prompt.ask("\n[dim]Press Enter to return to menu...[/]")


def download_video(url, output=None, quality='best', proxy=None, keep_ts=False, subs=False, speed_limit=None):
    """Download a video with fancy progress bars"""
    
    headers = {'Origin': 'https://www.pornhub.com'}
    
    try:
        # Phase 1: Extracting video info
        with console.status("[bold cyan]🔍 Fetching video information...", spinner="dots"):
            downloader = CustomHLSDownloader(
                output_name=output,
                headers=headers,
                keep_ts=keep_ts,
                proxy=proxy,
                speed_limit=speed_limit
            )
            streams = downloader.extract_video_info(url)
            
            # Extract Video ID for unique temp dir
            video_id = downloader.extract_video_id(url)
        
        console.print(f"[green]✓[/] Video: [bold]{downloader.output_name.stem}[/]")
        if proxy:
            console.print(f"[green]✓[/] Proxy: [bold]{proxy}[/]")
            
        # Select stream from available qualities
        sorted_keys = sorted([k for k in streams.keys() if isinstance(k, int)], reverse=True)
        
        if quality == 'best':
            selected_res = sorted_keys[0] if sorted_keys else list(streams.keys())[0]
        elif quality == 'worst':
            selected_res = sorted_keys[-1] if sorted_keys else list(streams.keys())[-1]
        else:
            try:
                req_q = int(quality)
                if req_q in streams:
                    selected_res = req_q
                elif sorted_keys:
                    selected_res = min(sorted_keys, key=lambda x:abs(x-req_q))
                else:
                    selected_res = list(streams.keys())[0]
            except ValueError:
                selected_res = sorted_keys[0] if sorted_keys else list(streams.keys())[0]
        
        m3u8_url = streams[selected_res]
        console.print(f"[green]✓[/] Quality: [bold]{selected_res}p[/]")
        
        # Phase 2: Analyzing playlist
        with console.status("[bold cyan]📊 Analyzing stream quality...", spinner="dots"):
            response = downloader.session.get(m3u8_url, timeout=10)
            response.raise_for_status()
            playlist_content = response.text
            
            # Check for multiple qualities (Master Playlist)
            if "#EXT-X-STREAM-INF" in playlist_content:
                console.print("[dim]Detected Master Playlist, fetching media playlist...[/]")
                
                # Parse available qualities from master playlist
                qualities = downloader._get_qualities(playlist_content, m3u8_url)
                
                if qualities:
                    # Select the first quality from parsed master playlist
                    # (user already selected quality when choosing stream URL earlier)
                    sorted_keys = sorted([k for k in qualities.keys() if isinstance(k, int)], reverse=True)
                    if sorted_keys:
                        # Pick first available quality
                        selected_q = sorted_keys[0]
                        media_playlist_url = qualities[selected_q]
                        
                        console.print(f"[dim]Fetching media playlist for {selected_q}p...[/]")
                        
                        # Fetch the actual media playlist
                        response = downloader.session.get(media_playlist_url, timeout=10)
                        response.raise_for_status()
                        playlist_content = response.text
                        m3u8_url = media_playlist_url
                else:
                    # Fallback: just parse the master playlist as-is
                    console.print("[yellow]⚠ Could not parse qualities from master playlist[/]")
            
            # Parse segments from media playlist
            segments = downloader._parse_media_playlist(playlist_content, m3u8_url)
            total_segments = len(segments)
            
            console.print(f"[green]✓[/] Segments: [bold]{total_segments}[/]")
            
            # Download Subtitles
            if subs:
                console.print("[cyan]📝 Checking for subtitles...[/]")
                # We need the original page content for this, but we didn't save it.
                # Let's re-fetch or assume we can't get it easily without refactoring extract_video_info to return it.
                # Actually, extract_video_info is where we had the HTML.
                # For now, let's fetch the page again quickly or just skip if too complex.
                # Better approach: pass the HTML content out of extract_video_info? 
                # Or just fetch again, it's cheap.
                try:
                    page_resp = downloader.session.get(url)
                    if downloader.download_subtitles(page_resp.text, downloader.output_name):
                        console.print("[green]✓[/] Subtitles downloaded")
                    else:
                        console.print("[yellow]⚠ No subtitles found[/]")
                except:
                    pass

        # Phase 3: Download with progress
        console.print("\n[bold cyan]📥 Downloading...[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="cyan", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("[cyan]Downloading segments...", total=total_segments)
            
            def progress_callback(completed, total):
                progress.update(task, completed=completed)
            
            # Update downloader with callback
            downloader.progress_callback = progress_callback
            
            # Start download
            from pathlib import Path
            import shutil
            import concurrent.futures
            
            # Unique temp directory for Resume capability
            temp_dir = Path(f"temp_{video_id}")
            temp_dir.mkdir(exist_ok=True)
            
            downloaded_files = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_to_segment = {
                    executor.submit(downloader._download_segment, seg_url, idx, temp_dir): idx 
                    for idx, seg_url in enumerate(segments)
                }
                
                completed = 0
                failed_segments = []
                for future in concurrent.futures.as_completed(future_to_segment):
                    idx = future_to_segment[future]
                    try:
                        file_path = future.result()
                        downloaded_files.append((idx, file_path))
                        completed += 1
                        progress_callback(completed, total_segments)
                    except Exception as e:
                        failed_segments.append(idx)
                        console.print(f"\n[red]Failed to download segment {idx}: {e}[/]")
            
            # Check if all segments downloaded successfully
            if failed_segments:
                raise RuntimeError(f"Failed to download {len(failed_segments)} segment(s). Download incomplete.")
            
            # Merge segments
            progress.update(task, description="[yellow]Merging segments...")
            downloaded_files.sort(key=lambda x: x[0])
            
            with open(downloader.output_name, 'wb') as outfile:
                for _, segment_file in downloaded_files:
                    with open(segment_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            shutil.rmtree(temp_dir)
            
            # Convert to MP4
            if not keep_ts:
                progress.update(task, description="[yellow]Converting to MP4...")
            final_file = downloader.convert_to_mp4()
            progress.update(task, completed=total_segments, description="[green]✓ Complete!")
            
            # Save to History
            db.add_entry(url, downloader.output_name.stem, final_file, selected_res)
        
        # Success message
        console.print()
        success_panel = Panel(
            f"[bold green]✓ Download Successful![/]\n\n"
            f"[cyan]File:[/] [bold white]{final_file}[/]\n"
            f"[cyan]Location:[/] [dim]{Path(final_file).absolute()}[/]",
            title="[bold green]Success[/]",
            border_style="green",
            box=box.DOUBLE
        )
        console.print(success_panel)
        
        return final_file
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Download cancelled by user[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/] {str(e)}")
        sys.exit(1)


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
    """
    \b
    ╔═══════════════════════════════════════════════════════╗
    ║                  PH SHORTS DOWNLOADER                 ║
    ╚═══════════════════════════════════════════════════════╝
    
    Download PornHub Shorts videos with a beautiful interface!
    
    \b
    📖 USAGE:
      ph-shorts [URL] [OPTIONS]
      ph-shorts                    # Interactive mode
      ph-shorts --version          # Show version
      ph-shorts --history          # Show history
      ph-shorts --stats            # Show statistics
      ph-shorts --help             # Show this help
    
    \b
    ✨ EXAMPLES:
      # Interactive mode with prompts
      ph-shorts
      
      # Download with URL (best quality)
      ph-shorts "https://www.pornhub.com/view_video.php?viewkey=..."
      
      # Specify quality
      ph-shorts "URL" -q 720
      ph-shorts "URL" --quality 1080
      
      # Custom output filename
      ph-shorts "URL" -o my_video.mp4
      
      # Use HTTP/HTTPS proxy
      ph-shorts "URL" -p http://127.0.0.1:1080
      ph-shorts "URL" --proxy http://proxy.example.com:8080
      
      # Keep original .ts file
      ph-shorts "URL" --keep-ts
      
      # Download with subtitles
      ph-shorts "URL" --subs
      
      # View past downloads
      ph-shorts --history
      
      # Combine options
      ph-shorts "URL" -q 1080 -o "video.mp4" -p http://proxy:8080
    
    \b
    📺 QUALITY OPTIONS:
      best   - Highest available quality (default)
      1080   - 1080p resolution
      720    - 720p resolution  
      480    - 480p resolution
      worst  - Lowest available quality (save bandwidth)
    
    \b
    🔧 REQUIREMENTS:
      • Python 3.10+
      • FFmpeg (optional, for MP4 conversion)
      • Internet connection
    
    \b
    💡 TIPS:
      • Use interactive mode if you're new (just run: ph-shorts)
      • FFmpeg is needed for MP4 conversion, otherwise .ts files are saved
      • Set a proxy if you have connection issues
      • Use 'best' quality for automatic quality selection
    
    \b
    📚 MORE INFO:
      GitHub: https://github.com/diastom/PornHub-Shorts
      Issues: https://github.com/diastom/PornHub-Shorts/issues
    """
    
    # Handle search mode
    if search:
        from .search import PornHubSearch
        searcher = PornHubSearch()
        searcher.cli_search(search, sort_by=sort, duration=duration)
        return
    
    # Handle channel mode
    if channel:
        from .playlist import PlaylistDownloader
        from .batch import BatchDownloader
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
        
        show_banner()
        console.print(f"\n[cyan]🔍 Scanning channel: {channel}...[/]")
        
        playlist = PlaylistDownloader()
        urls = playlist.GetChannelVideos(channel, limit=limit)
        
        if not urls:
            console.print("[red]❌ No videos found or channel does not exist[/]")
            return
            
        console.print(f"[green]✓ Found {len(urls)} videos[/]")
        
        # Reuse batch logic
        # We set batch variable to comma-separated URLs to reuse the block below?
        # No, better to just call the logic directly or structure it better.
        # Let's just run the batch logic here to be clean.
        
        console.print(f"\n[cyan]📦 Batch downloading {len(urls)} video(s)...[/]")
        console.print(f"[cyan]Mode:[/] {'Concurrent' if concurrent else 'Sequential'}\n")
        
        # Optimization: If converting later, keep TS to avoid double conversion
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
                
                # Handle conversion if requested
                if format or compress is not None or audio_only:
                    try:
                        from .converter import VideoConverter
                        if VideoConverter.IsFFmpegAvailable():
                            converter = VideoConverter()
                            progress.console.print(f"  [dim]Converting...[/]")
                            converted = converter.Convert(
                                input_file=path,
                                output_format=format if format else "mp4",
                                compress_quality=compress,
                                audio_only=audio_only
                            )
                            progress.console.print(f"  [green]✓[/] Converted: {Path(converted).name}")
                            
                            # Cleanup
                            if not keep_ts and Path(path).suffix == '.ts' and Path(path) != Path(converted):
                                try:
                                    Path(path).unlink()
                                except: pass
                    except Exception as e:
                        progress.console.print(f"  [red]Conversion failed: {e}[/]")
            
            def on_error(url, error):
                nonlocal completed_count
                completed_count += 1
                progress.update(task, completed=completed_count)
                progress.console.print(f"[red]✗[/] Failed: {url[:50]}... - {str(error)[:80]}")
            
            # Note: For batch channel download, we should probably force keep_ts=True 
            # if we plan to convert, to avoid double conversion.
            # But BatchDownloader calls DownloadVideo which calls VideoDownloader.download.
            # We can't easily pass keep_ts override to BatchDownloader without modifying it.
            # BatchDownloader uses self.quality but doesn't seem to expose keep_ts in AddUrl or DownloadAll.
            # Let's check BatchDownloader implementation.
            # If BatchDownloader doesn't support keep_ts, we might get MP4s.
            # That's acceptable for now, or we can update BatchDownloader.
            
            results = downloader.DownloadAll(
                on_progress=on_progress,
                on_complete=on_complete,
                on_error=on_error
            )
        
        console.print(f"\n[bold green]✅ Channel Download Complete![/]")
        console.print(f"[cyan]Successfully downloaded:[/] {len(results)}/{len(urls)}")
        return

    # Handle batch mode
    if batch:
        urls = [url.strip() for url in batch.split(',') if url.strip()]
        
        if not urls:
            console.print("[red]❌ No valid URLs provided[/]")
            return
        
        show_banner()
        console.print(f"\n[cyan]📦 Batch downloading {len(urls)} video(s)...[/]")
        console.print(f"[cyan]Mode:[/] {'Concurrent' if concurrent else 'Sequential'}\n")
        
        from .batch import BatchDownloader
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
        
        # Optimization: If converting later, keep TS to avoid double conversion
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
                # This gets called during download
                pass  # We'll update in on_complete instead
            
            def on_complete(url, path):
                nonlocal completed_count
                completed_count += 1
                progress.update(task, completed=completed_count)
                progress.console.print(f"[green]✓[/] Downloaded: {Path(path).name}")
                
                # Handle conversion if requested
                if doing_conversion:
                    try:
                        from .converter import VideoConverter
                        if VideoConverter.IsFFmpegAvailable():
                            converter = VideoConverter()
                            progress.console.print(f"  [dim]Converting...[/]")
                            converted = converter.Convert(
                                input_file=path,
                                output_format=format if format else "mp4",
                                compress_quality=compress,
                                audio_only=audio_only
                            )
                            progress.console.print(f"  [green]✓[/] Converted: {Path(converted).name}")
                            
                            # Cleanup
                            if not keep_ts and Path(path).suffix == '.ts' and Path(path) != Path(converted):
                                try:
                                    Path(path).unlink()
                                except: pass
                    except Exception as e:
                        progress.console.print(f"  [red]Conversion failed: {e}[/]")
            
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
        # Interactive mode
        interactive_mode()
    else:
        # CLI mode
        show_banner()
        
        # Optimization: If we are going to convert/compress later, 
        # don't waste time converting to MP4 first. Keep the raw TS file.
        doing_conversion = format is not None or compress is not None or audio_only
        effective_keep_ts = keep_ts or doing_conversion
        
        video_path = download_video(url, output=output, quality=quality, proxy=proxy, keep_ts=effective_keep_ts, subs=subs, speed_limit=speed_limit)
        
        # Post-download conversion if requested
        if doing_conversion:
            try:
                from .converter import VideoConverter
                
                if not VideoConverter.IsFFmpegAvailable():
                    console.print("[red]❌ FFmpeg not found! Conversion features require FFmpeg.[/]")
                    console.print("[yellow]Install FFmpeg to use --format, --compress, or --audio-only[/]")
                    return
                
                converter = VideoConverter()
                console.print("\n[bold cyan]🔄 Converting video...[/]")
                
                converted_path = converter.Convert(
                    input_file=video_path,
                    output_format=format if format else "mp4",
                    compress_quality=compress,
                    audio_only=audio_only
                )
                
                console.print(f"[green]✓[/] Converted: {Path(converted_path).name}")
                
                # Cleanup: If user didn't explicitly ask to keep TS, delete it
                if not keep_ts and Path(video_path).suffix == '.ts' and Path(video_path) != Path(converted_path):
                    try:
                        Path(video_path).unlink()
                    except Exception:
                        pass
                
            except Exception as e:
                console.print(f"[red]✗ Conversion failed:[/] {str(e)}")



def channel_download_interactive():
    """Interactive channel/playlist download"""
    console.print("\n[bold cyan]📺 Download Channel or Playlist[/]")
    
    # Get Target
    target = Prompt.ask("\n[bold green]🔗 Enter Channel/User URL or Name[/]")
    if not target:
        return
        
    # Get Limit
    limit = int(Prompt.ask("   [cyan]Max videos to download[/]", default="10"))
    
    # Scan
    from .playlist import PlaylistDownloader
    playlist = PlaylistDownloader()
    
    with console.status("[bold cyan]🔍 Scanning channel...", spinner="dots"):
        urls = playlist.GetChannelVideos(target, limit=limit)
        
    if not urls:
        console.print("[red]❌ No videos found[/]")
        return
        
    console.print(f"[green]✓ Found {len(urls)} videos[/]")
    
    # Confirm
    if not Confirm.ask(f"\n[bold yellow]📥 Download {len(urls)} videos?[/]", default=True):
        return
        
    # Download Mode
    console.print("\n[bold yellow]📥 Download Mode:[/]")
    console.print("1. Sequential (one-by-one)")
    console.print("2. Concurrent (simultaneous)")
    
    mode_choice = Prompt.ask("   Select mode", choices=["1", "2"], default="1")
    concurrent = mode_choice == "2"
    
    # Quality
    console.print("\n[bold yellow]📺 Select Quality:[/]")
    q_choice = Prompt.ask("   Quality (best/1080/720/480/worst)", default="best")
    
    # Start Batch Download
    from .batch import BatchDownloader
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    
    downloader = BatchDownloader(
        concurrent=concurrent,
        max_workers=3 if concurrent else 1,
        quality=q_choice
    )
    
    downloader.AddUrls(urls)
    
    # Progress tracking (copied from batch_download_interactive for consistency)
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
        
        def on_error(url, error):
            nonlocal completed_count
            completed_count += 1
            progress.update(task, completed=completed_count)
            progress.console.print(f"[red]✗[/] Failed: {url[:50]}... - {str(error)[:80]}")
        
        downloader.DownloadAll(
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error
        )
    
    console.print(f"\n[bold green]✅ Channel Download Complete![/]")
    Prompt.ask("\n[dim]Press Enter to return to menu...[/]")


if __name__ == '__main__':
    main()
