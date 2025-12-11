import requests
from bs4 import BeautifulSoup
from rich.console import Console
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
        try:
            sort_map = {
                'mostviewed': 'mv',
                'toprated': 'tr',
                'newest': 'ht'
            }
            sort_param = sort_map.get(sort_by, 'mv')
            
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
                all_links = soup.find_all('a', href=re.compile(r'/view_video\.php\?viewkey='))
                for link in all_links[:20]:
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
                    
                    title_elem = link_elem.get('title', '')
                    if not title_elem:
                        img_elem = link_elem.find('img')
                        if img_elem:
                            title_elem = img_elem.get('alt', img_elem.get('title', 'Unknown'))
                    
                    title = title_elem.strip() if title_elem else 'Unknown Title'
                    
                    duration = 'Unknown'
                    parent = item.find_parent('li')
                    if parent:
                        duration_elem = parent.find('var', class_='duration')
                        if duration_elem:
                            duration = duration_elem.text.strip()
                    
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
