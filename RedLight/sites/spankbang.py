import requests
import re
import json
import subprocess
import shutil
import concurrent.futures
import time
import ast
import html
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from .base import BaseSiteDownloader, BaseSiteSearch


class SpankBangDownloader(BaseSiteDownloader):
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://spankbang.com/',
        }
        self.session.headers.update(self.headers)
        self.driver = None
    
    def download(
        self,
        url: str,
        quality: str = "best",
        output_dir: str = "./downloads",
        filename: Optional[str] = None,
        keep_original: bool = False,
        proxy: Optional[str] = None,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> str:
        
        title, links = self._extract_info(url)
        
        selected_quality = self._select_quality(links, quality)
        download_url = links[selected_quality]
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if filename:
            output_file = output_path / filename
        else:
            clean_quality = selected_quality.replace(' ', '').replace('(', '').replace(')', '')
            output_file = output_path / f"{self._sanitize_filename(title)}_{clean_quality}.mp4"
            
        if 'm3u8' in download_url:
            self._download_hls_ffmpeg(download_url, str(output_file))
        else:
            self._download_manager(download_url, str(output_file), on_progress)
            
        return str(output_file)
    
    def get_info(self, url: str) -> Dict[str, Any]:
        title, links = self._extract_info(url)
        
        available_qualities = []
        for q in links.keys():
            match = re.search(r'(\d+)p', q) or re.search(r'(4k)', q)
            if match:
                val = match.group(1)
                if val == '4k': val = 2160
                else: val = int(val)
                available_qualities.append(val)
                
        return {
            "title": title,
            "available_qualities": sorted(available_qualities, reverse=True),
            "site": "spankbang"
        }
    
    def list_qualities(self, url: str) -> List[int]:
        info = self.get_info(url)
        return info["available_qualities"]
    
    @staticmethod
    def is_supported_url(url: str) -> bool:
        return "spankbang.com" in url.lower()
    
    @staticmethod
    def get_site_name() -> str:
        return "spankbang"
        
    def _extract_info(self, url: str) -> tuple[str, Dict[str, str]]:
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 403:
                raise requests.exceptions.HTTPError("403 Forbidden")
            
            response.raise_for_status()
            return self._parse_html(response.text)
            
        except (requests.exceptions.RequestException, ValueError):
            if not SELENIUM_AVAILABLE:
                raise RuntimeError("Requests failed and Selenium is not available. Please install selenium and webdriver-manager.")
            return self._extract_with_selenium(url)
            
    def _parse_html(self, html_content: str) -> tuple[str, Dict[str, str]]:
        title_match = re.search(r'<h1[^>]*title="([^"]+)"', html_content)
        if not title_match:
            title_match = re.search(r'<title>(.*?)</title>', html_content)
        
        title = "spankbang_video"
        if title_match:
            raw_title = html.unescape(title_match.group(1))
            title = re.sub(r'\s*-\s*SpankBang.*$', '', raw_title, flags=re.IGNORECASE)
            title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
            
        stream_match = re.search(r'var\s+stream_data\s*=\s*({.*?});', html_content, re.DOTALL)
        if not stream_match:
            raise ValueError("stream_data not found in HTML source.")
        
        stream_data_str = stream_match.group(1)
        try:
            data = ast.literal_eval(stream_data_str)
        except:
            data = {}
            matches = re.findall(r"'(\d+p|4k)'\s*:\s*\['([^']+)'\]", stream_data_str)
            for q, l in matches:
                data[q] = [l]
                
        return self._process_stream_data(data, title)
        
    def _extract_with_selenium(self, url: str) -> tuple[str, Dict[str, str]]:
        if not SELENIUM_AVAILABLE:
             raise RuntimeError("Selenium not installed")
             
        try:
            self._init_driver()
            self.driver.get(url)
            time.sleep(5) 
            
            title = self.driver.title.replace(" - SpankBang", "").strip()
            title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
            
            stream_data = self.driver.execute_script("return (typeof stream_data !== 'undefined') ? stream_data : null;")
            if not stream_data:
                stream_data = self.driver.execute_script("return window.stream_data;")
            
            if not stream_data:
                raise ValueError("Could not extract stream_data even with Selenium.")
                
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            ua = self.driver.execute_script("return navigator.userAgent;")
            self.session.headers.update({'User-Agent': ua})
            
            return self._process_stream_data(stream_data, title)
            
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def _process_stream_data(self, data: Dict, title: str) -> tuple[str, Dict[str, str]]:
        download_links = {}
        qualities = ['4k', '1080p', '720p', '480p', '240p']
        
        for q in qualities:
            if q in data and isinstance(data[q], list) and len(data[q]) > 0:
                download_links[q] = data[q][0]
        
        if not download_links and 'm3u8' in data and data['m3u8']:
             download_links['HLS (m3u8)'] = data['m3u8'][0]

        if not download_links:
            raise ValueError("No streams found.")
            
        return title, download_links
        
    def _select_quality(self, links: Dict[str, str], quality: str) -> str:
        def sort_key(k):
            if k == '4k': return 2160
            if 'm3u8' in k: return 0
            match = re.search(r'(\d+)p', k)
            return int(match.group(1)) if match else 0
            
        sorted_keys = sorted(links.keys(), key=sort_key, reverse=True)
        
        if quality == 'best':
            return sorted_keys[0]
        elif quality == 'worst':
            return sorted_keys[-1]
        else:
            try:
                req_q = int(quality)
                best_match = sorted_keys[0]
                min_diff = float('inf')
                
                for key in sorted_keys:
                    val = sort_key(key)
                    if val == 0: continue
                    diff = abs(val - req_q)
                    if diff < min_diff:
                        min_diff = diff
                        best_match = key
                return best_match
            except ValueError:
                return sorted_keys[0]

    def _download_manager(self, url: str, filename: str, on_progress: Optional[Callable] = None):
        if shutil.which("aria2c"):
            if self._download_with_aria2c(url, filename):
                return
        
        self._download_python_multithreaded(url, filename, on_progress)
        
    def _download_with_aria2c(self, url: str, filename: str) -> bool:
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.session.cookies.get_dict().items()])
        cmd = [
            'aria2c', url, '-o', filename, '-x', '16', '-s', '16', '-j', '1',
            '--header', f'User-Agent: {self.session.headers["User-Agent"]}',
            '--header', f'Referer: {self.session.headers["Referer"]}',
            '--header', f'Cookie: {cookie_str}',
            '--summary-interval=0', '--console-log-level=warn', '--download-result=hide'
        ]
        try:
            subprocess.run(cmd, check=True)
            return True
        except:
            return False
            
    def _download_python_multithreaded(self, url: str, filename: str, on_progress: Optional[Callable], num_threads: int = 16):
        try:
            head = self.session.head(url, allow_redirects=True)
            file_size = int(head.headers.get('content-length', 0))
        except:
            with self.session.get(url, stream=True) as r:
                r.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return
        
        with open(filename, 'wb') as f: f.truncate(file_size)
        
        chunk_size = file_size // num_threads
        ranges = []
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size - 1
            if i == num_threads - 1: end = file_size - 1
            ranges.append((start, end, i))
            
        completed = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {
                executor.submit(self._download_chunk, url, filename, start, end): i
                for start, end, i in ranges
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    downloaded = future.result()
                    completed += downloaded
                    if on_progress:
                        on_progress(completed, file_size)
                except Exception:
                    pass

    def _download_chunk(self, url: str, filename: str, start: int, end: int) -> int:
        headers = self.session.headers.copy()
        headers['Range'] = f'bytes={start}-{end}'
        response = self.session.get(url, headers=headers, stream=True, timeout=20)
        
        with open(filename, 'r+b') as f:
            f.seek(start)
            total = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                total += len(chunk)
        return total

    def _download_hls_ffmpeg(self, url: str, filename: str):
        if not shutil.which("ffmpeg"):
            raise RuntimeError("FFmpeg not found")
        cmd = ['ffmpeg', '-y', '-i', url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', filename]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def _sanitize_filename(self, title: str) -> str:
        return re.sub(r'[\\/*?:"<>|]', "", title)


class SpankBangSearch(BaseSiteSearch):
    
    def __init__(self):
        self.base_url = "https://spankbang.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        
    def search(self, query: str, page: int = 1, sort_by: str = "relevance", duration: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        search_url = f"{self.base_url}/s/{query}/{page}/"
        params = {}
        if sort_by == 'views': params['o'] = 'trending'
        elif sort_by == 'date': params['o'] = 'new'
        
        try:
            response = self.session.get(search_url, params=params)
            if response.status_code == 403:
                raise requests.exceptions.HTTPError("403 Forbidden")
            
            response.raise_for_status()
            return self._parse_results(response.text)
        except (requests.exceptions.RequestException, ValueError):
            if SELENIUM_AVAILABLE:
                return self._search_with_selenium(search_url, params)
            return []

    def _parse_results(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        items = soup.select('div[data-testid="video-item"]')
        if not items:
            items = soup.select('div.video-item')
            
        for item in items:
            try:
                link = item.find('a', href=True)
                if not link: continue
                
                href = link['href']
                if not href.startswith('http'): href = self.base_url + href
                
                img = item.find('img')
                title = link.get('title') or (img.get('alt') if img else None) or "Unknown Video"
                
                thumb = ''
                if img:
                    thumb = img.get('src') or img.get('data-src') or ''
                
                duration = ''
                dur_elem = item.select_one('[data-testid="video-item-length"]')
                if dur_elem:
                    duration = dur_elem.text.strip()
                else:
                    dur_elem = item.select_one('span.l')
                    if dur_elem: duration = dur_elem.text.strip()
                
                results.append({
                    "title": title,
                    "url": href,
                    "duration": duration,
                    "thumbnail": thumb,
                    "site": "spankbang"
                })
            except Exception: 
                continue
        return results

    def _search_with_selenium(self, url: str, params: Dict) -> List[Dict[str, Any]]:
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            if params:
                from urllib.parse import urlencode
                if '?' in url: url += '&' + urlencode(params)
                else: url += '?' + urlencode(params)
            
            driver.get(url)
            time.sleep(5)
            
            return self._parse_results(driver.page_source)
        except Exception:
            return []
        finally:
            if driver:
                driver.quit()

    @staticmethod
    def get_site_name() -> str:
        return "spankbang"
        
    def get_search_filters(self) -> Dict[str, List[str]]:
        return {
            "sort_by": ["relevance", "views", "date"],
            "duration": []
        }
