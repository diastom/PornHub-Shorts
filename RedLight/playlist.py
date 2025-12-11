import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import re
from urllib.parse import urljoin


class PlaylistDownloader:
    
    def __init__(self):
        self.base_url = "https://www.pornhub.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def GetChannelVideos(self, target: str, limit: int = 10) -> List[str]:
        if "eporner.com" in target:
            return self._get_eporner_videos(target, limit)
        elif "xvideos.com" in target:
            return self._get_xvideos_videos(target, limit)
        elif "spankbang.com" in target:
            return self._get_spankbang_videos(target, limit)
        return self._get_pornhub_videos(target, limit)

    def _get_eporner_videos(self, target: str, limit: int) -> List[str]:
        videos = []
        page = 1
        
        if not target.startswith("http"):
            target = f"https://www.eporner.com/channel/{target}/"
            
        print(f"Scanning Eporner: {target}")
        
        while len(videos) < limit:
            try:
                if page > 1:
                    if target.endswith('/'):
                        page_url = f"{target}{page}/"
                    else:
                        page_url = f"{target}/{page}/"
                else:
                    page_url = target
                    
                response = self.session.get(page_url, timeout=10)
                if response.status_code == 404:
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                found_on_page = 0
                
                for item in soup.find_all('div', class_='mb'):
                    link = item.find('a', href=True)
                    if link:
                        href = link['href']
                        if '/video-' in href or '/video/' in href:
                            full_url = urljoin("https://www.eporner.com", href)
                            if full_url not in videos:
                                videos.append(full_url)
                                found_on_page += 1
                                if len(videos) >= limit:
                                    break
                
                if found_on_page == 0:
                    break
                    
                page += 1
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                break
                
        return videos[:limit]

    def _get_pornhub_videos(self, target: str, limit: int = 10) -> List[str]:
        if target.startswith("http"):
            url = target
            if "/videos" not in url and "pornhub.com" in url:
                url = f"{url.rstrip('/')}/videos"
        else:
            url = f"{self.base_url}/users/{target}/videos"
            
        print(f"Scanning: {url}")
        
        videos = []
        page = 1
        
        while len(videos) < limit:
            try:
                page_url = f"{url}?page={page}"
                response = self.session.get(page_url, timeout=10)
                
                if response.status_code == 404:
                    if page == 1 and "/users/" in url:
                        url = url.replace("/users/", "/channels/")
                        print(f"User not found, trying channel: {url}")
                        continue
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                found_on_page = 0
                
                for link in soup.select('ul.videos.row-5-thumbs li.pcVideoListItem a'):
                    href = link.get('href')
                    if href and 'view_video.php' in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in videos:
                            videos.append(full_url)
                            found_on_page += 1
                            if len(videos) >= limit:
                                break
                
                if found_on_page == 0:
                    for link in soup.select('div.videoBox a'):
                        href = link.get('href')
                        if href and 'view_video.php' in href:
                            full_url = urljoin(self.base_url, href)
                            if full_url not in videos:
                                videos.append(full_url)
                                found_on_page += 1
                                if len(videos) >= limit:
                                    break
                
                if found_on_page == 0:
                    break
                    
                page += 1
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                break
                
        return videos[:limit]

    def _get_xvideos_videos(self, target: str, limit: int) -> List[str]:
        videos = []
        page = 0
        
        if not target.startswith("http"):
            target = f"https://www.xvideos.com/{target}"
        
        base_url = target.rstrip('/')
        print(f"Scanning XVideos: {base_url}")
        
        while len(videos) < limit:
            try:
                page_url = f"{base_url}/{page}" if page > 0 else base_url
                response = self.session.get(page_url, timeout=15)
                
                if response.status_code == 404:
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                found_on_page = 0
                
                for item in soup.find_all('div', class_='thumb-block'):
                    for link in item.find_all('a', href=True):
                        href = link['href']
                        if '/video.' in href or '/video/' in href:
                            full_url = urljoin("https://www.xvideos.com", href)
                            full_url = re.sub(r'/\d+/', '/', full_url)
                            full_url = re.sub(r'/THUMBNUM/', '/', full_url)
                            if full_url not in videos:
                                videos.append(full_url)
                                found_on_page += 1
                                if len(videos) >= limit:
                                    break
                    if len(videos) >= limit:
                        break
                
                if found_on_page == 0:
                    for item in soup.find_all('div', class_='post-block'):
                        for link in item.find_all('a', href=True):
                            href = link['href']
                            if '/video.' in href or '/video/' in href:
                                full_url = urljoin("https://www.xvideos.com", href)
                                full_url = re.sub(r'/\d+/', '/', full_url)
                                full_url = re.sub(r'/THUMBNUM/', '/', full_url)
                                if full_url not in videos:
                                    videos.append(full_url)
                                    found_on_page += 1
                                    if len(videos) >= limit:
                                        break
                        if len(videos) >= limit:
                            break
                
                if found_on_page == 0:
                    for link in soup.select('.mozaique .thumb a'):
                        href = link.get('href', '')
                        if '/video' in href:
                            full_url = urljoin("https://www.xvideos.com", href)
                            if full_url not in videos:
                                videos.append(full_url)
                                found_on_page += 1
                                if len(videos) >= limit:
                                    break
                
                if found_on_page == 0:
                    break
                    
                page += 1
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                break
                
        return videos[:limit]

    def _get_spankbang_videos(self, target: str, limit: int) -> List[str]:
        videos = []
        page = 1
        
        if not target.startswith("http"):
            target = f"https://spankbang.com/profile/{target}/videos"
        
        base_url = target.rstrip('/')
        if '/videos' not in base_url:
            base_url = f"{base_url}/videos"
        
        print(f"Scanning SpankBang: {base_url}")
        
        while len(videos) < limit:
            try:
                page_url = f"{base_url}/{page}/" if page > 1 else f"{base_url}/"
                response = self.session.get(page_url, timeout=10)
                
                if response.status_code == 404:
                    break
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                found_on_page = 0
                
                for item in soup.find_all('div', class_='video-item'):
                    link = item.find('a', href=True)
                    if link:
                        href = link['href']
                        if href and not href.startswith('#'):
                            full_url = urljoin("https://spankbang.com", href)
                            if '/video/' in full_url or re.match(r'.*/[\w]+/video/', full_url):
                                if full_url not in videos:
                                    videos.append(full_url)
                                    found_on_page += 1
                                    if len(videos) >= limit:
                                        break
                
                if found_on_page == 0:
                    break
                    
                page += 1
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                break
                
        return videos[:limit]
