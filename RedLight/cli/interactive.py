import sys
from pathlib import Path
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from .ui import console, db, show_banner
from .download import download_video
from ..sites import SiteRegistry
from ..multi_search import MultiSiteSearch
from ..batch import BatchDownloader
from ..playlist import PlaylistDownloader
from ..search import PornHubSearch
from ..api import GetVideoInfo
from ..statistics import GetStatistics
from ..resume_manager import GetResumeManager
from ..notifications import GetNotifier
from ..config import GetConfig, SaveConfig, CreateDefaultConfig, ResetConfig, ConfigManager
from ..aria2_downloader import IsAria2cAvailable


def select_quality_interactive(url: str) -> str:
    """
    Fetch video information and let user select from actual available qualities.
    
    Args:
        url: Video URL
        
    Returns:
        Selected quality string (e.g., 'best', '720', 'worst')
    """
    try:
        with console.status("[bold cyan]🔍 Fetching video information...", spinner="dots"):
            info = GetVideoInfo(url)
        
        console.print(f"\n[bold green]✓ Video:[/] {info.get('title', 'Unknown')}")
        
        available_qualities = info.get('available_qualities', [])
        
        if not available_qualities:
            console.print("[yellow]⚠ Could not detect available qualities, using default options[/]")
            return _select_generic_quality()
        
        available_qualities = sorted(available_qualities, reverse=True)
        
        console.print("\n[bold yellow]📺 Select Quality:[/]")
        quality_table = Table(show_header=False, box=box.SIMPLE)
        quality_table.add_column("Option", style="cyan", width=12)
        quality_table.add_column("Description", style="white")
        
        quality_table.add_row("1", f"🏆 Best Available ({available_qualities[0]}p)")
        
        quality_options = ["1"]
        for idx, quality in enumerate(available_qualities, 2):
            emoji = "📺" if quality >= 1080 else "📱" if quality >= 720 else "💾"
            quality_table.add_row(str(idx), f"{emoji} {quality}p")
            quality_options.append(str(idx))
        
        quality_table.add_row(str(len(available_qualities) + 2), f"📉 Lowest Available ({available_qualities[-1]}p)")
        quality_options.append(str(len(available_qualities) + 2))
        
        console.print(quality_table)
        
        choice = Prompt.ask("   Your choice", choices=quality_options, default="1")
        
        if choice == "1":
            return "best"
        elif choice == str(len(available_qualities) + 2):
            return "worst"
        else:
            quality_idx = int(choice) - 2
            return str(available_qualities[quality_idx])
            
    except Exception as e:
        console.print(f"[yellow]⚠ Error fetching video info: {str(e)}[/]")
        console.print("[dim]Using default quality options...[/]\n")
        return _select_generic_quality()


def _select_generic_quality() -> str:
    """Fallback to generic quality selection if video info fetch fails."""
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
    return quality_map[q_choice]


def search_cli_mode(query, sort_by="mostviewed", duration=None):
    """Search from CLI with provided query (Moved from search.py)"""
    searcher = PornHubSearch()
    page = 1
    
    while True:
        console.print(f"\n[bold cyan]Search Results: {query} (Page {page})[/]")
        console.print(f"[dim]Sort: {sort_by}, Duration: {duration or 'Any'}[/]\n")
        
        results = searcher.search(query, page, sort_by, duration)
        
        if not results:
            console.print("[yellow]No results found.[/]")
            break
        
        # Display results
        table = Table(title=f"Search Results - Page {page}", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Title", style="white")
        table.add_column("Duration", style="yellow", width=10)
        table.add_column("Views", style="green", width=12)
        
        for idx, video in enumerate(results, 1):
            title = video['title']
            if len(title) > 60:
                title = title[:57] + "..."
            
            table.add_row(
                str(idx),
                title,
                video['duration'],
                video['views']
            )
        
        console.print(table)
        
        # Action menu
        console.print("\n[bold cyan]Actions:[/]")
        console.print("  [1-N] - Download video by number")
        console.print("  [N]ext page")
        console.print("  [P]revious page")
        console.print("  [Q]uit")
        
        action = Prompt.ask("\n[bold]Select action[/]").lower()
        
        if action == 'q':
            break
        elif action == 'n':
            page += 1
        elif action == 'p':
            if page > 1:
                page -= 1
            else:
                console.print("[yellow]Already on first page[/]")
        elif action.isdigit():
            idx = int(action) - 1
            if 0 <= idx < len(results):
                selected_video = results[idx]
                console.print(f"\n[green]Selected:[/] {selected_video['title']}")
                console.print(f"[dim]URL: {selected_video['url']}[/]\n")
                
                quality = select_quality_interactive(selected_video['url'])
                
                download_video(selected_video['url'], quality=quality)
                
                if not Confirm.ask("\n[bold cyan]Continue searching?[/]", default=True):
                    break
        else:
            console.print("[red]Invalid action[/]")

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
        console.print("7. [bold cyan]Active Downloads[/]")
        console.print("8. [bold dark_orange]Settings[/]")
        console.print("9. [bold red]Exit[/]")
        
        choice = Prompt.ask("\n   Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"], default="1")
        
        if choice == "1":
            url = Prompt.ask("\n[bold green]🔗 Enter Video URL[/]")
            if not url:
                continue
            
            quality = select_quality_interactive(url)
            
            proxy = None
            if Confirm.ask("\n[bold yellow]🌐 Use Proxy?[/]", default=False):
                proxy = Prompt.ask("   [cyan]Enter Proxy URL (e.g., http://127.0.0.1:2080)[/]")
                if not proxy.startswith("http"):
                    proxy = f"http://{proxy}"
                    
            output = None
            if Confirm.ask("\n[bold yellow]💾 Custom Output Filename?[/]", default=False):
                output = Prompt.ask("   [cyan]Enter filename (e.g., video.mp4)[/]")

            keep_ts = Confirm.ask("\n[bold yellow]📦 Keep original .ts file?[/]", default=False)

            subs = Confirm.ask("\n[bold yellow]📝 Download Subtitles?[/]", default=False)
            
            speed_limit = None
            if Confirm.ask("\n[bold yellow]⚡ Limit download speed?[/]", default=False):
                speed_limit = Prompt.ask("   [cyan]Enter speed limit (e.g., 1M, 500K)[/]")
            
            download_video(url, output=output, quality=quality, proxy=proxy, keep_ts=keep_ts, subs=subs, speed_limit=speed_limit)
            
            if not Confirm.ask("\n[bold cyan]Do you want to continue?[/]", default=True):
                console.print("[bold green]Goodbye! 👋[/]")
                break
                
        elif choice == "2":
            # Multi-site search

            
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
            # Enhanced History Menu
            history_menu_interactive()
            
        elif choice == "6":
            # Enhanced Statistics Menu
            statistics_menu_interactive()
            
        elif choice == "7":
            # Active Downloads (Resume/Pause)
            active_downloads_menu()
        
        elif choice == "8":
            # Settings Menu
            settings_menu_interactive()
            
        elif choice == "9":
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


def history_menu_interactive():
    """Enhanced history menu with export and management options."""
    while True:
        console.print("\n[bold magenta]📜 Download History Menu[/]")
        console.print("1. [bold]View Recent History[/]")
        console.print("2. [bold]View History by Site[/]")
        console.print("3. [bold]Export History (JSON)[/]")
        console.print("4. [bold]Export History (CSV)[/]")
        console.print("5. [bold red]Clear History[/]")
        console.print("6. [bold]Back to Main Menu[/]")
        
        choice = Prompt.ask("   Select option", choices=["1", "2", "3", "4", "5", "6"], default="1")
        
        if choice == "1":
            limit = int(Prompt.ask("   [cyan]How many entries to show?[/]", default="20"))
            db.show_history(console, limit=limit)
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "2":
            console.print("\n[cyan]Select site:[/]")
            console.print("1. PornHub")
            console.print("2. Eporner")
            console.print("3. SpankBang")
            console.print("4. XVideos")
            
            site_choice = Prompt.ask("   Site", choices=["1", "2", "3", "4"], default="1")
            site_map = {"1": "pornhub", "2": "eporner", "3": "spankbang", "4": "xvideos"}
            db.show_history(console, limit=20, site=site_map[site_choice])
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "3":
            filepath = Prompt.ask("   [cyan]Export path[/]", default="./history.json")
            try:
                result = db.export_history(format="json", filepath=filepath)
                console.print(f"[green]✓ Exported to {result}[/]")
            except Exception as e:
                console.print(f"[red]✗ Export failed: {e}[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "4":
            filepath = Prompt.ask("   [cyan]Export path[/]", default="./history.csv")
            try:
                result = db.export_history(format="csv", filepath=filepath)
                console.print(f"[green]✓ Exported to {result}[/]")
            except Exception as e:
                console.print(f"[red]✗ Export failed: {e}[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "5":
            if Confirm.ask("[bold red]⚠ Clear ALL download history?[/]", default=False):
                deleted = db.clear_history()
                console.print(f"[green]✓ Deleted {deleted} entries[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "6":
            break


def statistics_menu_interactive():
    """Enhanced statistics menu with detailed views."""
    stats = GetStatistics()
    
    while True:
        console.print("\n[bold white]📊 Statistics Menu[/]")
        console.print("1. [bold]View Dashboard[/]")
        console.print("2. [bold]Site Breakdown[/]")
        console.print("3. [bold]Quality Distribution[/]")
        console.print("4. [bold]Download Timeline[/]")
        console.print("5. [bold]Search Statistics[/]")
        console.print("6. [bold]Back to Main Menu[/]")
        
        choice = Prompt.ask("   Select option", choices=["1", "2", "3", "4", "5", "6"], default="1")
        
        if choice == "1":
            stats.show_dashboard(console)
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "2":
            stats.show_site_breakdown(console)
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "3":
            stats.show_quality_distribution(console)
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "4":
            days = int(Prompt.ask("   [cyan]Show last N days[/]", default="7"))
            stats.show_timeline(console, days=days)
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "5":
            stats.show_search_stats(console)
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "6":
            break


def active_downloads_menu():
    """Menu to manage active and paused downloads (Resume/Pause)."""
    manager = GetResumeManager()
    
    while True:
        console.print("\n[bold cyan]⏯️ Active Downloads Manager[/]")
        
        # Get downloads
        active = manager.list_active_downloads()
        paused = manager.list_paused_downloads()
        failed = manager.list_failed_downloads()
        
        if not active and not paused and not failed:
            console.print("[yellow]No active, paused, or failed downloads.[/]")
            console.print("[dim]Downloads here are managed for resume/pause capability.[/]")
            Prompt.ask("\n[dim]Press Enter to return...[/]")
            break
        
        # Show active downloads
        if active:
            console.print("\n[bold green]📥 Active Downloads:[/]")
            for i, d in enumerate(active, 1):
                progress = (d.downloaded_size / d.total_size * 100) if d.total_size > 0 else 0
                console.print(f"  {i}. [cyan]{d.download_id}[/] - {d.title[:40]} ({progress:.1f}%)")
        
        # Show paused downloads
        if paused:
            console.print("\n[bold yellow]⏸️ Paused Downloads:[/]")
            for i, d in enumerate(paused, 1):
                progress = (d.downloaded_size / d.total_size * 100) if d.total_size > 0 else 0
                console.print(f"  {i}. [cyan]{d.download_id}[/] - {d.title[:40]} ({progress:.1f}%)")
        
        # Show failed downloads
        if failed:
            console.print("\n[bold red]❌ Failed Downloads (Resumable):[/]")
            for i, d in enumerate(failed, 1):
                console.print(f"  {i}. [cyan]{d.download_id}[/] - {d.title[:40]}")
        
        console.print("\n[bold]Options:[/]")
        console.print("1. [green]Resume a paused/failed download[/]")
        console.print("2. [yellow]Pause an active download[/]")
        console.print("3. [red]Cancel a download[/]")
        console.print("4. [dim]Clean up completed[/]")
        console.print("5. [bold]Back to Main Menu[/]")
        
        choice = Prompt.ask("   Select option", choices=["1", "2", "3", "4", "5"], default="5")
        
        if choice == "1":
            download_id = Prompt.ask("   [cyan]Enter Download ID to resume[/]")
            state = manager.resume_download(download_id)
            if state:
                console.print(f"[green]✓ Resumed: {state.title}[/]")
                console.print("[dim]Note: You need to restart the download process to continue.[/]")
            else:
                console.print("[red]✗ Could not resume. Download not found or not resumable.[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "2":
            download_id = Prompt.ask("   [cyan]Enter Download ID to pause[/]")
            if manager.pause_download(download_id):
                console.print(f"[green]✓ Paused: {download_id}[/]")
            else:
                console.print("[red]✗ Could not pause. Download not found or not active.[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "3":
            download_id = Prompt.ask("   [cyan]Enter Download ID to cancel[/]")
            if Confirm.ask(f"[red]Cancel download {download_id}?[/]", default=False):
                if manager.cancel_download(download_id):
                    console.print(f"[green]✓ Cancelled: {download_id}[/]")
                else:
                    console.print("[red]✗ Could not cancel.[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "4":
            cleaned = manager.cleanup_all_completed()
            console.print(f"[green]✓ Cleaned up {cleaned} completed/cancelled downloads[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "5":
            break


def settings_menu_interactive():
    """Settings menu for notifications, config, and other preferences."""
    notifier = GetNotifier()
    config = GetConfig()
    
    while True:
        console.print("\n[bold dark_orange]⚙️ Settings[/]")
        
        # Show current settings
        notif_status = "[green]Enabled[/]" if notifier.config.enabled else "[red]Disabled[/]"
        sound_status = "[green]Enabled[/]" if notifier.config.sound_enabled else "[red]Disabled[/]"
        aria2c_status = "[green]Available[/]" if IsAria2cAvailable() else "[yellow]Not installed[/]"
        
        console.print(f"\n[bold]Current Settings:[/]")
        console.print(f"  Default Quality: [cyan]{config.download.default_quality}[/]")
        console.print(f"  Output Directory: [cyan]{config.download.output_directory}[/]")
        console.print(f"  Aria2c: {aria2c_status} ({'Enabled' if config.download.use_aria2c else 'Disabled'})")
        console.print(f"  Notifications: {notif_status}")
        console.print(f"  Notification Sounds: {sound_status}")
        
        if config.proxy.enabled:
            console.print(f"  Proxy: [cyan]{config.proxy.http or config.proxy.https}[/]")
        
        console.print("\n[bold]Options:[/]")
        console.print("1. [bold]Set Default Quality[/]")
        console.print("2. [bold]Set Download Directory[/]")
        console.print("3. [bold]Configure Proxy[/]")
        console.print("4. [bold]Toggle Aria2c (Fast Downloads)[/]")
        console.print("5. [bold]Toggle Notifications[/]")
        console.print("6. [bold]Toggle Notification Sounds[/]")
        console.print("7. [bold]Test Notification[/]")
        console.print("8. [bold]Open Config File[/]")
        console.print("9. [bold]Reset to Defaults[/]")
        console.print("10. [bold]View App Info[/]")
        console.print("11. [bold]Back to Main Menu[/]")
        
        choice = Prompt.ask("   Select option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"], default="11")
        
        if choice == "1":
            console.print("\n[cyan]Quality Options:[/]")
            console.print("  best, worst, 1080, 720, 480, 360, 240")
            new_quality = Prompt.ask("   [cyan]Default quality[/]", default=config.download.default_quality)
            config.download.default_quality = new_quality
            save_config(config)
            console.print(f"[green]✓ Default quality set to: {new_quality}[/]")
            
        elif choice == "2":
            new_dir = Prompt.ask("   [cyan]Download directory[/]", default=config.download.output_directory)
            config.download.output_directory = new_dir
            SaveConfig(config)
            console.print(f"[green]✓ Download directory set to: {new_dir}[/]")
            
        elif choice == "3":
            console.print("\n[bold cyan]Proxy Configuration[/]")
            enable_proxy = Confirm.ask("   Enable proxy?", default=config.proxy.enabled)
            config.proxy.enabled = enable_proxy
            
            if enable_proxy:
                proxy_url = Prompt.ask("   [cyan]Proxy URL (e.g., http://127.0.0.1:8080)[/]", 
                                       default=config.proxy.http or "")
                config.proxy.http = proxy_url
                config.proxy.https = proxy_url
            
            save_config(config)
            console.print(f"[green]✓ Proxy settings saved[/]")
            
        elif choice == "4":
            if IsAria2cAvailable():
                config.download.use_aria2c = not config.download.use_aria2c
                save_config(config)
                status = "enabled" if config.download.use_aria2c else "disabled"
                console.print(f"[green]✓ Aria2c {status}[/]")
                
                if config.download.use_aria2c:
                    connections = Prompt.ask("   [cyan]Number of connections[/]", 
                                            default=str(config.download.aria2c_connections))
                    try:
                        config.download.aria2c_connections = int(connections)
                        save_config(config)
                    except ValueError:
                        pass
            else:
                console.print("[yellow]Aria2c is not installed. Install it for faster downloads.[/]")
                console.print("[dim]  Windows: choco install aria2 or scoop install aria2[/]")
                console.print("[dim]  Linux: sudo apt install aria2[/]")
                console.print("[dim]  macOS: brew install aria2[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "5":
            if notifier.config.enabled:
                notifier.disable()
                console.print("[yellow]✓ Notifications disabled[/]")
            else:
                notifier.enable()
                console.print("[green]✓ Notifications enabled[/]")
            
        elif choice == "6":
            if notifier.config.sound_enabled:
                notifier.disable_sound()
                console.print("[yellow]✓ Notification sounds disabled[/]")
            else:
                notifier.enable_sound()
                console.print("[green]✓ Notification sounds enabled[/]")
            
        elif choice == "7":
            console.print("[cyan]Sending test notification...[/]")
            notifier.notify_custom(
                "🔔 Test Notification",
                "RedLight DL notifications are working!",
                "success"
            )
            console.print("[green]✓ Test notification sent![/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "8":
            config_path = ConfigManager.DEFAULT_CONFIG_PATH
            CreateDefaultConfig()  # Ensure it exists
            console.print(f"\n[bold]Config File Location:[/]")
            console.print(f"  [cyan]{config_path}[/]")
            console.print("\n[dim]Edit this file directly for advanced settings.[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "9":
            if Confirm.ask("[bold red]Reset all settings to defaults?[/]", default=False):
                ResetConfig()
                config = GetConfig()  # Reload
                console.print("[green]✓ Settings reset to defaults[/]")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "10":
            from ..version import __version__, __author__, __description__
            console.print(f"\n[bold cyan]RedLight DL v{__version__}[/]")
            console.print(f"[dim]{__description__}[/]")
            console.print(f"[dim]By: {__author__}[/]")
            console.print(f"\n[bold]Supported Sites:[/] PornHub, Eporner, SpankBang, XVideos")
            console.print(f"[bold]Config File:[/] ~/.RedLight/config.yaml")
            console.print(f"[bold]Database:[/] ~/.RedLight/history.db")
            console.print(f"[bold]Downloads DB:[/] ~/.RedLight/downloads.db")
            Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
        elif choice == "11":
            break
