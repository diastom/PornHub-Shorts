import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box
import re

console = Console()

class PornHubSearch:
    def __init__(self):
        self.base_url = "https://www.pornhub.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def search(self, query, page=1, sort_by="mostviewed", duration=None):
        """
        Search PornHub and return list of video results.
        
        Args:
            query: Search term
            page: Page number
            sort_by: Sort order ('mostviewed', 'toprated', 'newest')
            duration: Duration filter ('short', 'medium', 'long')
        """
        try:
            # Map sort options
            sort_map = {
                'mostviewed': 'mv',
                'toprated': 'tr',
                'newest': 'ht'
            }
            sort_param = sort_map.get(sort_by, 'mv')
            
            # Map duration options
            # short < 10min, medium 10-20min, long > 20min
            duration_map = {
                'short': '10minus',
                'medium': '10-20',
                'long': '20plus'
            }
            duration_param = duration_map.get(duration)
            
            url = f"{self.base_url}/video/search?search={query}&page={page}&o={sort_param}"
            if duration_param:
                url += f"&filter_duration={duration_param}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            # Try multiple selectors
            selectors = [
                ('div', 'phimage'),
                ('li', 'pcVideoListItem'),
                ('div', 'videoBox'),
            ]
            
            video_items = []
            for tag, class_name in selectors:
                items = soup.find_all(tag, class_=class_name)
                if items:
                    video_items = items
                    break
            
            if not video_items:
                # Fallback: Try to find any links that look like video links
                all_links = soup.find_all('a', href=re.compile(r'/view_video\.php\?viewkey='))
                for link in all_links[:20]:  # Limit to first 20
                    try:
                        url = link.get('href', '')
                        if not url.startswith('http'):
                            url = f"{self.base_url}{url}"
                        
                        title = link.get('title', link.text.strip() or 'Unknown')
                        videos.append({
                            'title': title,
                            'url': url,
                            'duration': 'Unknown',
                            'views': 'Unknown'
                        })
                    except:
                        continue
                return videos
            
            for item in video_items:
                try:
                    link_elem = item.find('a')
                    if not link_elem:
                        continue
                    
                    link = link_elem.get('href', '')
                    if not link:
                        continue
                    
                    if not link.startswith('http'):
                        link = f"{self.base_url}{link}"
                    
                    # Extract title
                    title_elem = link_elem.get('title', '')
                    if not title_elem:
                        img_elem = link_elem.find('img')
                        if img_elem:
                            title_elem = img_elem.get('alt', img_elem.get('title', 'Unknown'))
                    
                    title = title_elem.strip() if title_elem else 'Unknown Title'
                    
                    # Extract duration
                    duration = 'Unknown'
                    parent = item.find_parent('li')
                    if parent:
                        duration_elem = parent.find('var', class_='duration')
                        if duration_elem:
                            duration = duration_elem.text.strip()
                    
                    # Extract views
                    views = 'Unknown'
                    if parent:
                        views_elem = parent.find(class_='views')
                        if views_elem:
                            views = views_elem.text.strip()
                    
                    videos.append({
                        'title': title,
                        'url': link,
                        'duration': duration,
                        'views': views
                    })
                except Exception:
                    continue
            
            return videos
            
        except Exception as e:
            console.print(f"[red]Search failed: {e}[/]")
            return []
    
    def cli_search(self, query, sort_by="mostviewed", duration=None):
        """Search from CLI with provided query"""
        page = 1
        
        while True:
            console.print(f"\n[bold cyan]Search Results: {query} (Page {page})[/]")
            console.print(f"[dim]Sort: {sort_by}, Duration: {duration or 'Any'}[/]\n")
            
            results = self.search(query, page, sort_by, duration)
            
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
                    
                    # Quality selection
                    console.print("[bold yellow]📺 Select Quality:[/]")
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
                    
                    from .cli import download_video
                    download_video(selected_video['url'], quality=quality)
                    
                    if not Prompt.ask("\n[bold cyan]Continue searching?[/]", choices=['y', 'n'], default='y') == 'y':
                        break
                else:
                    console.print("[red]Invalid selection[/]")
            else:
                console.print("[red]Invalid action[/]")
    
    def interactive_search(self):
        """Interactive search with pagination"""
        query = Prompt.ask("\n[bold green]🔍 Enter search term[/]")
        
        if not query:
            console.print("[yellow]No search term entered.[/]")
            return
        
        page = 1
        
        while True:
            console.print(f"\n[bold cyan]Searching for: {query} (Page {page})[/]\n")
            
            results = self.search(query, page)
            
            if not results:
                console.print("[yellow]No results found.[/]")
                break
            
            # Display results in a table
            table = Table(title=f"Search Results - Page {page}", box=box.ROUNDED)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Title", style="white")
            table.add_column("Duration", style="yellow", width=10)
            table.add_column("Views", style="green", width=12)
            
            for idx, video in enumerate(results, 1):
                # Truncate title if too long
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
            console.print("  [S]earch again")
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
            elif action == 's':
                return self.interactive_search()
            elif action.isdigit():
                idx = int(action) - 1
                if 0 <= idx < len(results):
                    selected_video = results[idx]
                    console.print(f"\n[green]Selected:[/] {selected_video['title']}")
                    console.print(f"[dim]URL: {selected_video['url']}[/]\n")
                    
                    # Quality selection
                    console.print("[bold yellow]📺 Select Quality:[/]")
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
                    
                    # Import here to avoid circular import
                    from .cli import download_video
                    download_video(selected_video['url'], quality=quality)
                    
                    # Ask if want to continue searching
                    if not Prompt.ask("\n[bold cyan]Continue searching?[/]", choices=['y', 'n'], default='y') == 'y':
                        break
                else:
                    console.print("[red]Invalid selection[/]")
            else:
                console.print("[red]Invalid action[/]")
