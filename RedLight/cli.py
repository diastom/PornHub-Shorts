
"""
CLI interface for RedLight DL using Rich and Click
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
[bold cyan]╔══════════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold magenta]██████╗ ███████╗██████╗ ██╗     ██╗ ██████╗ ██╗  ██╗████████╗[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔══██╗██╔════╝██╔══██╗██║     ██║██╔════╝ ██║  ██║╚══██╔══╝[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██████╔╝█████╗  ██║  ██║██║     ██║██║  ███╗███████║   ██║   [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔══██╗██╔══╝  ██║  ██║██║     ██║██║   ██║██╔══██║   ██║   [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██║  ██║███████╗██████╔╝███████╗██║╚██████╔╝██║  ██║   ██║   [/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   [/]  [bold cyan]║[/]
[bold cyan]║[/]          [bold yellow]Professional Adult Content Downloader[/]              [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════════════════╝[/]
                [dim]version 1.0.11 • RedLight DL[/]
"""


def show_banner():
    """Display the awesome banner"""
    console.print(BANNER)


def show_version(ctx, param, value):
    """Display version information"""
    if not value or ctx.resilient_parsing:
        return
    
    version_info = Panel(
        f"[bold cyan]RedLight DL[/]\n\n"
        f"[yellow]Version:[/] [bold white]{__version__}[/]\n"
        f"[yellow]Author:[/] [bold white]{__author__}[/]\n"
        f"[yellow]Description:[/] [dim]{__description__}[/]\n\n"
        f"[dim]For more information, visit:[/]\n"
        f"[link=https://github.com/diastom/RedLightDL]https://github.com/diastom/RedLightDL[/]",
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

    from rich.table import Table
    from rich import box

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
            # Multi-site search
            from .sites import SiteRegistry
            from .multi_search import MultiSiteSearch
            from .database import DatabaseManager
            from rich.table import Table
            
            registry = SiteRegistry()
            sites = registry.get_all_sites()
            
            # Show site selection menu
            console.print("\n[bold cyan]🔍 Select Search Site:[/]")
            for idx, site in enumerate(sites, 1):
                console.print(f"{idx}. [bold]{site['display_name']}[/]")
            console.print(f"{len(sites) + 1}. [bold yellow]Search in All Sites[/]")
            
            site_choice = Prompt.ask(
                "   Select site",
                choices=[str(i) for i in range(1, len(sites) + 2)],
                default="1"
            )
            
            # Get search query
            query = Prompt.ask("\n[bold green]🔎 Enter search query[/]")
            if not query:
                continue
            
            # Perform search based on selection
            if int(site_choice) == len(sites) + 1:
                # Search all sites
                console.print(f"\n[cyan]Searching all sites for: {query}...[/]\n")
                multi_search = MultiSiteSearch()
                all_results = multi_search.search_all(query)
                
                # Save to history
                db.add_search_entry("all", query, "", len(all_results))
                
                if all_results:
                    # Create Rich Table
                    table = Table(title=f"🔍 Search Results: {query} (All Sites)", box=box.ROUNDED)
                    table.add_column("#", style="cyan", width=4)
                    table.add_column("Site", style="magenta", width=10)
                    table.add_column("Title", style="white")
                    table.add_column("Duration", style="yellow", width=10)
                    
                    for i, result in enumerate(all_results[:20], 1):
                        table.add_row(
                            str(i),
                            result.get('site', 'unknown').title(),
                            result.get('title', 'No title'),
                            result.get('duration', 'N/A')
                        )
                    
                    console.print(table)
                    console.print(f"\n[green]✓ Found {len(all_results)} results across all sites[/]")
                    console.print("[dim]Copy the URL from the table above to download[/]\n")
                else:
                    console.print("[yellow]No results found[/]")
            else:
                # Search specific site
                site_name = sites[int(site_choice) - 1]["name"]
                searcher = registry.get_search_by_name(site_name)
                
                if searcher:
                    console.print(f"\n[cyan]Searching {site_name.title()} for: {query}...[/]\n")
                    results = searcher.search(query)
                    
                    # Save to history
                    db.add_search_entry(site_name, query, "", len(results))
                    
                    if results:
                        # Create Rich Table
                        table = Table(title=f"🔍 Search Results: {query} ({site_name.title()})", box=box.ROUNDED)
                        table.add_column("#", style="cyan", width=4)
                        table.add_column("Title", style="white")
                        table.add_column("URL", style="blue", overflow="fold")
                        table.add_column("Duration", style="yellow", width=10)
                        
                        # Add views column if available (PornHub has it)
                        has_views = any('views' in r and r.get('views') for r in results[:5])
                        if has_views:
                            table.add_column("Views", style="green", width=12)
                        
                        for i, result in enumerate(results[:20], 1):
                            row_data = [
                                str(i),
                                result.get('title', 'No title'),
                                result.get('url', ''),
                                result.get('duration', 'N/A')
                            ]
                            
                            if has_views:
                                row_data.append(result.get('views', 'N/A'))
                            
                            table.add_row(*row_data)
                        
                        console.print(table)
                        console.print(f"\n[green]✓ Found {len(results)} results[/]")
                        console.print("[dim]Copy the URL from the table above to download[/]\n")
                    else:
                        console.print("[yellow]No results found[/]")
            
            Prompt.ask("\n[dim]Press Enter to return to menu...[/]")
            
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
    """Download a video with fancy progress bars using multi-site API"""
    
    try:
        from .sites import SiteRegistry
        from .api import GetVideoInfo, DownloadVideo
        
        # Phase 1: Get video info and display
        with console.status("[bold cyan]🔍 Detecting site and fetching video information...", spinner="dots"):
            registry = SiteRegistry()
            site_name = registry.detect_site(url)
            
            if not site_name:
                raise ValueError("Unsupported URL. Please use a PornHub or Eporner link.")
            
            # Get video info
            info = GetVideoInfo(url)
        
        # Display video information
        console.print(f"[green]✓[/] Site: [bold]{site_name.title()}[/]")
        console.print(f"[green]✓[/] Video: [bold]{info['title']}[/]")
        console.print(f"[green]✓[/] Available Qualities: [bold]{', '.join([f'{q}p' for q in info['available_qualities']])}[/]")
        
        # Determine selected quality
        if quality == 'best':
            selected_q = max(info['available_qualities'])
        elif quality == 'worst':
            selected_q = min(info['available_qualities'])
        else:
            try:
                req_q = int(quality)
                # Find closest quality
                selected_q = min(info['available_qualities'], key=lambda x: abs(x - req_q))
            except:
                selected_q = max(info['available_qualities'])
        
        console.print(f"[green]✓[/] Selected Quality: [bold]{selected_q}p[/]")
        
        if proxy:
            console.print(f"[green]✓[/] Proxy: [bold]{proxy}[/]")
        
        # Phase 2: Download with progress tracking
        console.print("\n[bold cyan]📥 Downloading...[/]")
        output_dir = "./downloads"
        
        # For Eporner, disable aria2c to get progress feedback
        # We'll use the Python multi-threaded downloader
        if site_name == "eporner":
            # Temporarily disable aria2c for better progress tracking
            import shutil
            aria2c_path = shutil.which("aria2c")
            
            # Get the downloader instance
            downloader = registry.get_downloader_for_url(url)
            
            # Monkey-patch to disable aria2c
            original_which = shutil.which
            def mock_which(cmd):
                if cmd == "aria2c":
                    return None
                return original_which(cmd)
            
            shutil.which = mock_which
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="cyan", finished_style="green"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                
                # Progress tracking
                task_id = None
                
                def on_progress(current, total):
                    nonlocal task_id
                    if task_id is None:
                        task_id = progress.add_task(
                            f"[cyan]Downloading {selected_q}p...", 
                            total=total
                        )
                    progress.update(task_id, completed=current)
                
                # Download using the multi-site API with progress callback
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
            # Restore aria2c detection if we disabled it
            if site_name == "eporner":
                shutil.which = original_which
        
        # Success message
        console.print()
        success_panel = Panel(
            f"[bold green]✓ Download Successful![/]\n\n"
            f"[cyan]Site:[/] [bold white]{site_name.title()}[/]\n"
            f"[cyan]Title:[/] [bold white]{info['title']}[/]\n"
            f"[cyan]Quality:[/] [bold white]{selected_q}p[/]\n"
            f"[cyan]File:[/] [bold white]{Path(result_path).name}[/]\n"
            f"[cyan]Location:[/] [dim]{Path(result_path).absolute()}[/]",
            title="[bold green]Success[/]",
            border_style="green",
            box=box.DOUBLE
        )
        console.print(success_panel)
        
        # Save to history
        db.add_entry(url, info['title'], result_path, selected_q)
        
        return result_path
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Download cancelled by user[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/] {str(e)}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/]")
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
    ║                    REDLIGHT DL                        ║
    ╚═══════════════════════════════════════════════════════╝
    
    Professional adult content downloader with a beautiful interface!
    
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
      GitHub: https://github.com/diastom/RedLightDL
      Issues: https://github.com/diastom/RedLightDL/issues
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
