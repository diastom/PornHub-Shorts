import sqlite3
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadState:
    download_id: str
    url: str
    output_path: str
    total_size: int = 0
    downloaded_size: int = 0
    status: str = "pending"
    quality: str = "best"
    site: str = ""
    title: str = ""
    segments_completed: List[int] = None
    temp_dir: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if self.segments_completed is None:
            self.segments_completed = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
    
    @property
    def progress_percent(self) -> float:
        if self.total_size <= 0:
            return 0.0
        return (self.downloaded_size / self.total_size) * 100
    
    @property
    def is_resumable(self) -> bool:
        return self.status in (DownloadStatus.PAUSED.value, DownloadStatus.FAILED.value)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResumeManager:
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else Path.home() / ".RedLight" / "downloads.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._active_downloads: Dict[str, bool] = {}
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS download_states (
                download_id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                output_path TEXT,
                total_size INTEGER DEFAULT 0,
                downloaded_size INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                quality TEXT DEFAULT 'best',
                site TEXT,
                title TEXT,
                segments_json TEXT,
                temp_dir TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_download(self, url: str, output_path: str, quality: str = "best",
                       site: str = "", title: str = "", total_size: int = 0) -> str:
        download_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO download_states 
            (download_id, url, output_path, total_size, downloaded_size, status, 
             quality, site, title, segments_json, temp_dir, created_at, updated_at)
            VALUES (?, ?, ?, ?, 0, 'pending', ?, ?, ?, '[]', '', ?, ?)
        ''', (download_id, url, output_path, total_size, quality, site, title, now, now))
        conn.commit()
        conn.close()
        
        self._active_downloads[download_id] = True
        return download_id
    
    def update_progress(self, download_id: str, downloaded_size: int,
                       total_size: Optional[int] = None,
                       segments_completed: Optional[List[int]] = None) -> bool:
        if download_id in self._active_downloads and not self._active_downloads[download_id]:
            return False
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        if total_size is not None and segments_completed is not None:
            c.execute('''UPDATE download_states SET downloaded_size = ?, total_size = ?, 
                        segments_json = ?, status = 'downloading', updated_at = ? WHERE download_id = ?''',
                     (downloaded_size, total_size, json.dumps(segments_completed), now, download_id))
        elif total_size is not None:
            c.execute('''UPDATE download_states SET downloaded_size = ?, total_size = ?, 
                        status = 'downloading', updated_at = ? WHERE download_id = ?''',
                     (downloaded_size, total_size, now, download_id))
        elif segments_completed is not None:
            c.execute('''UPDATE download_states SET downloaded_size = ?, segments_json = ?, 
                        status = 'downloading', updated_at = ? WHERE download_id = ?''',
                     (downloaded_size, json.dumps(segments_completed), now, download_id))
        else:
            c.execute('''UPDATE download_states SET downloaded_size = ?, 
                        status = 'downloading', updated_at = ? WHERE download_id = ?''',
                     (downloaded_size, now, download_id))
        
        conn.commit()
        conn.close()
        return self._active_downloads.get(download_id, True)
    
    def pause_download(self, download_id: str) -> bool:
        self._active_downloads[download_id] = False
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''UPDATE download_states SET status = 'paused', updated_at = ?
                    WHERE download_id = ? AND status = 'downloading' ''',
                 (datetime.now().isoformat(), download_id))
        affected = c.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def resume_download(self, download_id: str) -> Optional[DownloadState]:
        state = self.get_download_state(download_id)
        if state and state.is_resumable:
            self._active_downloads[download_id] = True
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''UPDATE download_states SET status = 'downloading', updated_at = ?
                        WHERE download_id = ?''', (datetime.now().isoformat(), download_id))
            conn.commit()
            conn.close()
            return state
        return None
    
    def cancel_download(self, download_id: str) -> bool:
        self._active_downloads[download_id] = False
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''UPDATE download_states SET status = 'cancelled', updated_at = ?
                    WHERE download_id = ?''', (datetime.now().isoformat(), download_id))
        affected = c.rowcount
        conn.commit()
        conn.close()
        
        self._active_downloads.pop(download_id, None)
        return affected > 0
    
    def complete_download(self, download_id: str, final_path: str = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        if final_path:
            c.execute('''UPDATE download_states SET status = 'completed', output_path = ?, 
                        updated_at = ? WHERE download_id = ?''', (final_path, now, download_id))
        else:
            c.execute('''UPDATE download_states SET status = 'completed', updated_at = ?
                        WHERE download_id = ?''', (now, download_id))
        
        affected = c.rowcount
        conn.commit()
        conn.close()
        self._active_downloads.pop(download_id, None)
        return affected > 0
    
    def fail_download(self, download_id: str, error: str = "") -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''UPDATE download_states SET status = 'failed', updated_at = ?
                    WHERE download_id = ?''', (datetime.now().isoformat(), download_id))
        affected = c.rowcount
        conn.commit()
        conn.close()
        self._active_downloads.pop(download_id, None)
        return affected > 0
    
    def get_download_state(self, download_id: str) -> Optional[DownloadState]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT download_id, url, output_path, total_size, downloaded_size,
                    status, quality, site, title, segments_json, temp_dir, created_at, updated_at
                    FROM download_states WHERE download_id = ?''', (download_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return self._row_to_state(row)
        return None
    
    def list_active_downloads(self) -> List[DownloadState]:
        return self._list_by_status('downloading')
    
    def list_paused_downloads(self) -> List[DownloadState]:
        return self._list_by_status('paused')
    
    def list_failed_downloads(self) -> List[DownloadState]:
        return self._list_by_status('failed')
    
    def list_all_downloads(self, limit: int = 50) -> List[DownloadState]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT download_id, url, output_path, total_size, downloaded_size,
                    status, quality, site, title, segments_json, temp_dir, created_at, updated_at
                    FROM download_states ORDER BY updated_at DESC LIMIT ?''', (limit,))
        rows = c.fetchall()
        conn.close()
        return [self._row_to_state(row) for row in rows]
    
    def _list_by_status(self, status: str) -> List[DownloadState]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT download_id, url, output_path, total_size, downloaded_size,
                    status, quality, site, title, segments_json, temp_dir, created_at, updated_at
                    FROM download_states WHERE status = ? ORDER BY updated_at DESC''', (status,))
        rows = c.fetchall()
        conn.close()
        return [self._row_to_state(row) for row in rows]
    
    def _row_to_state(self, row) -> DownloadState:
        segments = json.loads(row[9]) if row[9] else []
        return DownloadState(
            download_id=row[0], url=row[1], output_path=row[2],
            total_size=row[3], downloaded_size=row[4], status=row[5],
            quality=row[6], site=row[7] or "", title=row[8] or "",
            segments_completed=segments, temp_dir=row[10] or "",
            created_at=row[11], updated_at=row[12]
        )
    
    def cleanup_completed(self, days_old: int = 7) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''DELETE FROM download_states WHERE status IN ('completed', 'cancelled')
                    AND datetime(updated_at) < datetime('now', ?)''', (f'-{days_old} days',))
        affected = c.rowcount
        conn.commit()
        conn.close()
        return affected
    
    def cleanup_all_completed(self) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM download_states WHERE status IN ('completed', 'cancelled')")
        affected = c.rowcount
        conn.commit()
        conn.close()
        return affected
    
    def should_continue(self, download_id: str) -> bool:
        return self._active_downloads.get(download_id, True)


_default_manager: Optional[ResumeManager] = None


def GetResumeManager() -> ResumeManager:
    global _default_manager
    if _default_manager is None:
        _default_manager = ResumeManager()
    return _default_manager
