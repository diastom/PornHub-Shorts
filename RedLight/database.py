import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


class DatabaseManager:
    
    def __init__(self):
        self.db_path = Path.home() / ".RedLight" / "history.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                filename TEXT,
                quality TEXT,
                date_downloaded TIMESTAMP
            )
        ''')
        
        self._migrate_history_table(c)
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT,
                query TEXT,
                filters TEXT,
                results_count INTEGER,
                timestamp TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _migrate_history_table(self, cursor):
        cursor.execute("PRAGMA table_info(history)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        
        new_columns = {
            'site': 'TEXT',
            'file_size': 'INTEGER DEFAULT 0',
            'duration': 'TEXT',
            'status': "TEXT DEFAULT 'completed'"
        }
        
        for column, col_type in new_columns.items():
            if column not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE history ADD COLUMN {column} {col_type}')
                except sqlite3.OperationalError:
                    pass

    def add_entry(
        self,
        url: str,
        title: str,
        filename: str,
        quality: str,
        site: str = None,
        file_size: int = 0,
        duration: str = None
    ):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if not site:
                site = self._infer_site(url)
            
            c.execute('''
                INSERT INTO history 
                (url, title, filename, quality, date_downloaded, site, file_size, duration, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed')
            ''', (url, title, str(filename), str(quality), datetime.now(), site, file_size, duration))
            
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def _infer_site(self, url: str) -> str:
        if not url:
            return "unknown"
        url_lower = url.lower()
        if "pornhub" in url_lower:
            return "pornhub"
        elif "eporner" in url_lower:
            return "eporner"
        elif "spankbang" in url_lower:
            return "spankbang"
        elif "xvideos" in url_lower:
            return "xvideos"
        return "unknown"

    def get_history(
        self,
        limit: int = 50,
        site: str = None,
        quality: str = None
    ) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            query = '''
                SELECT id, url, title, filename, quality, date_downloaded, 
                       site, file_size, duration, status
                FROM history
            '''
            params = []
            conditions = []
            
            if site:
                conditions.append('site = ?')
                params.append(site)
            
            if quality:
                conditions.append('quality = ?')
                params.append(quality)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY date_downloaded DESC LIMIT ?'
            params.append(limit)
            
            c.execute(query, params)
            rows = c.fetchall()
            conn.close()
            
            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'filename': row[3],
                    'quality': row[4],
                    'date_downloaded': row[5],
                    'site': row[6] if len(row) > 6 else None,
                    'file_size': row[7] if len(row) > 7 else 0,
                    'duration': row[8] if len(row) > 8 else None,
                    'status': row[9] if len(row) > 9 else 'completed'
                })
            
            return result
        except Exception:
            return []
    
    def get_history_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                SELECT id, url, title, filename, quality, date_downloaded
                FROM history WHERE url = ?
                ORDER BY date_downloaded DESC LIMIT 1
            ''', (url,))
            row = c.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'filename': row[3],
                    'quality': row[4],
                    'date_downloaded': row[5]
                }
            return None
        except Exception:
            return None
    
    def clear_history(self, older_than_days: int = None) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if older_than_days is not None:
                c.execute('''
                    DELETE FROM history 
                    WHERE datetime(date_downloaded) < datetime('now', ?)
                ''', (f'-{older_than_days} days',))
            else:
                c.execute('DELETE FROM history')
            
            deleted = c.rowcount
            conn.commit()
            conn.close()
            return deleted
        except Exception:
            return 0
    
    def export_history(self, format: str = 'json', filepath: str = None) -> str:
        history = self.get_history(limit=10000)
        
        if format == 'json':
            output = json.dumps(history, indent=2, default=str)
        elif format == 'csv':
            import csv
            import io
            buffer = io.StringIO()
            if history:
                writer = csv.DictWriter(buffer, fieldnames=history[0].keys())
                writer.writeheader()
                writer.writerows(history)
            output = buffer.getvalue()
        else:
            output = json.dumps(history, indent=2, default=str)
        
        if filepath:
            Path(filepath).write_text(output, encoding='utf-8')
            return filepath
        
        return output

    def show_history(self, console: Console, limit: int = 10, site: str = None):
        history = self.get_history(limit=limit, site=site)

        if not history:
            console.print("[yellow]No download history found.[/]")
            return

        title = "📜 Download History"
        if site:
            title += f" ({site.title()})"
        
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Site", style="magenta", width=10)
        table.add_column("Title", style="white", max_width=40)
        table.add_column("Quality", style="green", width=8)
        table.add_column("Size", style="yellow", width=10)

        for idx, entry in enumerate(history, 1):
            try:
                dt = datetime.fromisoformat(entry['date_downloaded'])
                formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = str(entry['date_downloaded'])
            
            size = entry.get('file_size', 0) or 0
            if size > 0:
                if size > 1024 * 1024 * 1024:
                    size_str = f"{size / (1024**3):.1f} GB"
                elif size > 1024 * 1024:
                    size_str = f"{size / (1024**2):.1f} MB"
                else:
                    size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = "-"
            
            title_text = entry['title'] or "Unknown"
            if len(title_text) > 40:
                title_text = title_text[:37] + "..."
            
            table.add_row(
                str(idx),
                formatted_date,
                (entry.get('site') or 'unknown').title(),
                title_text,
                f"{entry['quality']}p",
                size_str
            )

        console.print(table)
        console.print(f"\n[dim]Showing {len(history)} of {self._get_total_count()} total downloads[/]")
    
    def _get_total_count(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM history')
            count = c.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

    def show_stats(self, console: Console):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM history')
        total = c.fetchone()[0]
        
        if total == 0:
            console.print("[yellow]No statistics available yet.[/]")
            conn.close()
            return

        c.execute('SELECT quality, COUNT(*) FROM history GROUP BY quality ORDER BY COUNT(*) DESC')
        quality_stats = c.fetchall()
        
        try:
            c.execute('SELECT site, COUNT(*) FROM history WHERE site IS NOT NULL GROUP BY site ORDER BY COUNT(*) DESC')
            site_stats = c.fetchall()
        except:
            site_stats = []
        
        try:
            c.execute('SELECT SUM(file_size) FROM history WHERE file_size > 0')
            total_size = c.fetchone()[0] or 0
        except:
            total_size = 0
        
        conn.close()

        size_str = self._format_size(total_size)
        summary = f"[bold green]Total Downloads:[/] {total}\n"
        summary += f"[bold green]Total Size:[/] {size_str}\n"
        if quality_stats:
            top_quality = quality_stats[0][0]
            summary += f"[bold green]Most Common Quality:[/] {top_quality}p"
        
        console.print(Panel(summary, title="📊 Download Statistics", border_style="cyan"))
        
        table = Table(title="📺 Quality Distribution", box=box.ROUNDED)
        table.add_column("Quality", style="magenta")
        table.add_column("Count", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")
        table.add_column("Bar", style="cyan")

        for quality, count in quality_stats:
            percentage = (count / total) * 100
            bar_width = int(percentage / 5)
            bar = "█" * bar_width + "░" * (20 - bar_width)
            table.add_row(f"{quality}p", str(count), f"{percentage:.1f}%", bar)

        console.print(table)
        
        if site_stats:
            site_table = Table(title="🌐 Downloads by Site", box=box.ROUNDED)
            site_table.add_column("Site", style="cyan")
            site_table.add_column("Count", style="green", justify="right")
            site_table.add_column("Percentage", style="yellow", justify="right")
            
            for site, count in site_stats:
                if site:
                    percentage = (count / total) * 100
                    site_table.add_row(site.title(), str(count), f"{percentage:.1f}%")
            
            console.print(site_table)
    
    def _format_size(self, size_bytes: int) -> str:
        if size_bytes <= 0:
            return "N/A"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    def add_search_entry(self, site: str, query: str, filters: str, results_count: int):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                'INSERT INTO search_history (site, query, filters, results_count, timestamp) VALUES (?, ?, ?, ?, ?)',
                (site, query, filters, results_count, datetime.now())
            )
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    def get_search_history(self, limit: int = 20) -> list:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(
                'SELECT site, query, results_count, timestamp FROM search_history ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            rows = c.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
    
    def clear_search_history(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('DELETE FROM search_history')
            deleted = c.rowcount
            conn.commit()
            conn.close()
            return deleted
        except Exception:
            return 0
    
    def show_search_history(self, console: Console, limit: int = 20):
        rows = self.get_search_history(limit)
        
        if not rows:
            console.print("[yellow]No search history found.[/]")
            return
        
        table = Table(title="🔍 Search History", box=box.ROUNDED)
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Site", style="magenta")
        table.add_column("Query", style="white")
        table.add_column("Results", style="green")
        
        for site, query, results, timestamp in rows:
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = timestamp
            
            table.add_row(formatted_date, site.title(), query, str(results))
        
        console.print(table)
