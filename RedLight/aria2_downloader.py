import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def IsAria2cAvailable() -> bool:
    return shutil.which("aria2c") is not None


class Aria2cDownloader:
    
    def __init__(self, connections: int = 16, speed_limit: str = "", timeout: int = 30):
        self.connections = connections
        self.speed_limit = speed_limit
        self.timeout = timeout
    
    @staticmethod
    def is_available() -> bool:
        return IsAria2cAvailable()
    
    def download(
        self,
        url: str,
        output_path: str,
        on_progress: Optional[Callable[[int, int], None]] = None,
        headers: Optional[dict] = None
    ) -> bool:
        if not self.is_available():
            raise RuntimeError("aria2c not installed")
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "aria2c", url,
            "-x", str(self.connections),
            "-s", str(self.connections),
            "-k", "1M",
            "-d", str(output.parent),
            "-o", output.name,
            "--file-allocation=none",
            "--console-log-level=error",
            "--summary-interval=1",
            "--download-result=hide",
            "-c",
        ]
        
        if self.speed_limit:
            cmd.extend(["--max-download-limit", self.speed_limit])
        
        if self.timeout:
            cmd.extend(["--timeout", str(self.timeout)])
        
        if headers:
            for key, value in headers.items():
                cmd.extend(["--header", f"{key}: {value}"])
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True)
            return output.exists() and output.stat().st_size > 0
        except Exception:
            return False
    
    def download_segments(
        self,
        urls: list,
        output_dir: str,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> list:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        input_file = output_dir / "_segments.txt"
        with open(input_file, 'w') as f:
            for i, url in enumerate(urls):
                f.write(f"{url}\n")
                f.write(f"  out=segment_{i:05d}.ts\n")
        
        cmd = [
            "aria2c", "-i", str(input_file),
            "-x", str(min(self.connections, 4)),
            "-j", str(min(len(urls), 16)),
            "-d", str(output_dir),
            "--file-allocation=none",
            "--console-log-level=error",
            "-c",
        ]
        
        try:
            subprocess.run(cmd, capture_output=True)
            input_file.unlink(missing_ok=True)
            
            results = []
            for i in range(len(urls)):
                seg = output_dir / f"segment_{i:05d}.ts"
                if seg.exists():
                    results.append(str(seg))
            return results
        except Exception:
            return []


class PythonDownloader:
    
    def __init__(self, connections: int = 4, chunk_size: int = 1024 * 1024, timeout: int = 30):
        self.connections = connections
        self.chunk_size = chunk_size
        self.timeout = timeout
        self._stop_event = threading.Event()
    
    def download(
        self,
        url: str,
        output_path: str,
        on_progress: Optional[Callable[[int, int], None]] = None,
        headers: Optional[dict] = None
    ) -> bool:
        self._stop_event.clear()
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        session = requests.Session()
        if headers:
            session.headers.update(headers)
        
        try:
            head = session.head(url, timeout=self.timeout, allow_redirects=True)
            total_size = int(head.headers.get('content-length', 0))
            supports_range = head.headers.get('accept-ranges', '').lower() == 'bytes'
        except Exception:
            total_size = 0
            supports_range = False
        
        if not supports_range or total_size < self.chunk_size * 2:
            return self._simple_download(session, url, output, on_progress, total_size)
        
        return self._chunked_download(session, url, output, total_size, on_progress)
    
    def _simple_download(self, session, url, output, on_progress, total_size):
        try:
            response = session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            downloaded = 0
            with open(output, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self._stop_event.is_set():
                        return False
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress:
                            on_progress(downloaded, total_size or downloaded)
            return True
        except Exception:
            return False
    
    def _chunked_download(self, session, url, output, total_size, on_progress):
        chunk_size = total_size // self.connections
        ranges = []
        
        for i in range(self.connections):
            start = i * chunk_size
            end = total_size - 1 if i == self.connections - 1 else (i + 1) * chunk_size - 1
            ranges.append((i, start, end))
        
        temp_dir = Path(tempfile.mkdtemp())
        chunks = {}
        downloaded = [0]
        lock = threading.Lock()
        
        def download_chunk(idx, start, end):
            if self._stop_event.is_set():
                return
            
            chunk_path = temp_dir / f"chunk_{idx}"
            headers = {'Range': f'bytes={start}-{end}'}
            
            try:
                resp = session.get(url, headers=headers, stream=True, timeout=self.timeout)
                resp.raise_for_status()
                
                with open(chunk_path, 'wb') as f:
                    for data in resp.iter_content(chunk_size=8192):
                        if self._stop_event.is_set():
                            return
                        if data:
                            f.write(data)
                            with lock:
                                downloaded[0] += len(data)
                                if on_progress:
                                    on_progress(downloaded[0], total_size)
                
                chunks[idx] = chunk_path
            except Exception:
                pass
        
        with ThreadPoolExecutor(max_workers=self.connections) as executor:
            futures = [executor.submit(download_chunk, i, s, e) for i, s, e in ranges]
            for f in as_completed(futures):
                pass
        
        if len(chunks) != self.connections:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        
        try:
            with open(output, 'wb') as out:
                for i in range(self.connections):
                    with open(chunks[i], 'rb') as chunk:
                        shutil.copyfileobj(chunk, out)
            shutil.rmtree(temp_dir, ignore_errors=True)
            return True
        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
    
    def stop(self):
        self._stop_event.set()


def get_fast_downloader(prefer_aria2c: bool = True, connections: int = 16):
    if prefer_aria2c and IsAria2cAvailable():
        return Aria2cDownloader(connections=connections)
    return PythonDownloader(connections=min(connections, 8))
