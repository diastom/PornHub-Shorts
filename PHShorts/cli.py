
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

from .downloader import CustomHLSDownloader
from .database import DatabaseManager
from . import __version__, __description__

console = Console()
db = DatabaseManager()

BANNER = """
[bold cyan]╔═══════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold magenta]██████╗ ██╗  ██╗    ███████╗██╗  ██╗ ██████╗ ██████╗ ████████╗███████╗[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔══██╗██║  ██║    ██╔════╝██║  ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██████╔╝███████║    ███████╗███████║██║   ██║██████╔╝   ██║   ███████╗[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔═══╝ ██╔══██║    ╚════██║██╔══██║██║   ██║██╔══██╗   ██║   ╚════██║[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██║     ██║  ██║    ███████║██║  ██║╚██████╔╝██║  ██║   ██║   ███████║[/]  [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]╚═╝     ╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝[/]  [bold cyan]║[/]
[bold cyan]╚═══════════════════════════════════════════════════════╝[/]
            [bold yellow]Download PornHub Shorts with Style![/]
    [dim]version 1.0.4 • Simple & Light[/]
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
        console.print("2. [bold yellow]View History[/]")
        console.print("3. [bold magenta]View Statistics[/]")
        console.print("4. [bold red]Exit[/]")
        
        choice = Prompt.ask("\n   Select an option", choices=["1", "2", "3", "4"], default="1")
        
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
            
            # Start download
            download_video(url, output=output, quality=quality, proxy=proxy, keep_ts=keep_ts, subs=subs)
            
            if not Confirm.ask("\n[bold cyan]Do you want to continue?[/]", default=True):
                console.print("[bold green]Goodbye! 👋[/]")
                break
                
        elif choice == "2":
            db.show_history(console)
            Prompt.ask("\n[dim]Press Enter to return to menu...[/]")
            
        elif choice == "3":
            db.show_stats(console)
            Prompt.ask("\n[dim]Press Enter to return to menu...[/]")
            
        elif choice == "4":
            console.print("[bold green]Goodbye! 👋[/]")
            break


def download_video(url, output=None, quality='best', proxy=None, keep_ts=False, subs=False):
    """Download a video with fancy progress bars"""
    
    headers = {'Origin': 'https://www.pornhub.com'}
    
    try:
        # Phase 1: Extracting video info
        with console.status("[bold cyan]🔍 Fetching video information...", spinner="dots"):
            downloader = CustomHLSDownloader(
                output_name=output,
                headers=headers,
                keep_ts=keep_ts,
                proxy=proxy
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
                qualities = downloader._get_qualities(playlist_content, m3u8_url)
                if qualities:
                    # Logic to select from master playlist if needed (usually we already have the stream)
                    pass
            
            # Parse segments
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
                for future in concurrent.futures.as_completed(future_to_segment):
                    idx = future_to_segment[future]
                    try:
                        file_path = future.result()
                        downloaded_files.append((idx, file_path))
                        completed += 1
                        progress_callback(completed, total_segments)
                    except Exception as e:
                        pass
            
            # Merge segments
            progress.update(task, description="[yellow]Merging segments...")
            downloaded_files.sort(key=lambda x: x[0])
            
            with open(downloader.output_name, 'wb') as outfile:
                for _, segment_file in downloaded_files:
                    with open(segment_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            shutil.rmtree(temp_dir)
            
            # Convert to MP4
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
def main(url, output, quality, proxy, keep_ts, subs):
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
    
    if not url:
        # Interactive mode
        interactive_mode()
    else:
        # CLI mode
        show_banner()
        download_video(url, output=output, quality=quality, proxy=proxy, keep_ts=keep_ts, subs=subs)


if __name__ == '__main__':
    main()
