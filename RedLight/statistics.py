"""Download statistics and analytics for RedLight DL."""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


class DownloadStatistics:
    """Download history analytics with rich display."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else Path.home() / ".RedLight" / "history.db"
        self.console = Console()
    
    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.db_path.exists():
            return {"total_downloads": 0, "total_size": 0, "avg_quality": 0, 
                    "top_site": None, "first_download": None, "last_download": None}
        
        conn = self._get_connection()
        c = conn.cursor()
        result = {"total_downloads": 0, "total_size": 0, "avg_quality": 0,
                  "top_site": None, "first_download": None, "last_download": None}
        
        try:
            c.execute('SELECT COUNT(*) FROM history')
            result["total_downloads"] = c.fetchone()[0]
            
            if result["total_downloads"] == 0:
                return result
            
            try:
                c.execute('SELECT SUM(file_size) FROM history WHERE file_size IS NOT NULL')
                size = c.fetchone()[0]
                result["total_size"] = size if size else 0
            except sqlite3.OperationalError:
                pass
            
            c.execute('SELECT AVG(CAST(quality AS INTEGER)) FROM history WHERE quality IS NOT NULL')
            avg = c.fetchone()[0]
            result["avg_quality"] = int(avg) if avg else 0
            
            try:
                c.execute('''SELECT site, COUNT(*) as count FROM history 
                            WHERE site IS NOT NULL GROUP BY site ORDER BY count DESC LIMIT 1''')
                row = c.fetchone()
                result["top_site"] = row[0] if row else None
            except sqlite3.OperationalError:
                pass
            
            c.execute('SELECT MIN(date_downloaded), MAX(date_downloaded) FROM history')
            row = c.fetchone()
            if row:
                result["first_download"], result["last_download"] = row
        except Exception:
            pass
        finally:
            conn.close()
        
        return result
    
    def get_by_site(self) -> Dict[str, Dict[str, Any]]:
        if not self.db_path.exists():
            return {}
        
        conn = self._get_connection()
        c = conn.cursor()
        result = {}
        
        try:
            c.execute("PRAGMA table_info(history)")
            columns = [col[1] for col in c.fetchall()]
            
            if 'site' not in columns:
                c.execute('SELECT url, quality FROM history')
                site_data = defaultdict(lambda: {"count": 0, "qualities": []})
                
                for url, quality in c.fetchall():
                    site = self._infer_site(url)
                    site_data[site]["count"] += 1
                    if quality:
                        try:
                            site_data[site]["qualities"].append(int(quality))
                        except ValueError:
                            pass
                
                for site, data in site_data.items():
                    result[site] = {
                        "count": data["count"], "size": 0,
                        "avg_quality": int(sum(data["qualities"]) / len(data["qualities"])) if data["qualities"] else 0
                    }
            else:
                c.execute('''SELECT site, COUNT(*), COALESCE(SUM(file_size), 0), AVG(CAST(quality AS INTEGER))
                            FROM history WHERE site IS NOT NULL GROUP BY site''')
                
                for site, count, size, avg_quality in c.fetchall():
                    result[site] = {"count": count, "size": size or 0, "avg_quality": int(avg_quality) if avg_quality else 0}
        except Exception:
            pass
        finally:
            conn.close()
        
        return result
    
    def _infer_site(self, url: str) -> str:
        if not url:
            return "unknown"
        url = url.lower()
        for site in ["pornhub", "eporner", "spankbang", "xvideos"]:
            if site in url:
                return site
        return "unknown"
    
    def get_by_quality(self) -> Dict[str, int]:
        if not self.db_path.exists():
            return {}
        
        conn = self._get_connection()
        c = conn.cursor()
        result = {}
        
        try:
            c.execute('''SELECT quality, COUNT(*) FROM history WHERE quality IS NOT NULL 
                        GROUP BY quality ORDER BY CAST(quality AS INTEGER) DESC''')
            for quality, count in c.fetchall():
                result[str(quality)] = count
        except Exception:
            pass
        finally:
            conn.close()
        
        return result
    
    def get_by_date(self, days: int = 30) -> List[Dict[str, Any]]:
        if not self.db_path.exists():
            return []
        
        conn = self._get_connection()
        c = conn.cursor()
        result = []
        
        try:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            c.execute('''SELECT DATE(date_downloaded) as d, COUNT(*) FROM history 
                        WHERE DATE(date_downloaded) >= ? GROUP BY d ORDER BY d DESC''', (cutoff,))
            
            for date_str, count in c.fetchall():
                result.append({"date": date_str, "count": count, "size": 0})
        except Exception:
            pass
        finally:
            conn.close()
        
        return result
    
    def get_top_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.db_path.exists():
            return []
        
        conn = self._get_connection()
        c = conn.cursor()
        result = []
        
        try:
            c.execute('''SELECT query, COUNT(*) as count, MAX(timestamp) as last 
                        FROM search_history GROUP BY query ORDER BY count DESC LIMIT ?''', (limit,))
            for query, count, last in c.fetchall():
                result.append({"query": query, "count": count, "last_searched": last})
        except Exception:
            pass
        finally:
            conn.close()
        
        return result
    
    def get_search_stats(self) -> Dict[str, Any]:
        if not self.db_path.exists():
            return {"total_searches": 0, "unique_queries": 0, "searches_by_site": {}}
        
        conn = self._get_connection()
        c = conn.cursor()
        result = {"total_searches": 0, "unique_queries": 0, "searches_by_site": {}}
        
        try:
            c.execute('SELECT COUNT(*) FROM search_history')
            result["total_searches"] = c.fetchone()[0]
            
            c.execute('SELECT COUNT(DISTINCT query) FROM search_history')
            result["unique_queries"] = c.fetchone()[0]
            
            c.execute('SELECT site, COUNT(*) FROM search_history GROUP BY site')
            for site, count in c.fetchall():
                result["searches_by_site"][site] = count
        except Exception:
            pass
        finally:
            conn.close()
        
        return result
    
    # Display methods
    
    def show_dashboard(self, console: Optional[Console] = None):
        console = console or self.console
        summary = self.get_summary()
        
        if summary["total_downloads"] == 0:
            console.print("[yellow]No download statistics available yet.[/]")
            return
        
        console.print("\n[bold cyan]📊 RedLight DL Statistics Dashboard[/]\n")
        
        text = f"""[bold green]Total Downloads:[/] {summary['total_downloads']}
[bold green]Total Size:[/] {self._format_size(summary['total_size'])}
[bold green]Average Quality:[/] {summary['avg_quality']}p
[bold green]Top Site:[/] {summary['top_site'] or 'N/A'}"""
        
        if summary['first_download']:
            try:
                first = datetime.fromisoformat(summary['first_download']).strftime("%Y-%m-%d")
                last = datetime.fromisoformat(summary['last_download']).strftime("%Y-%m-%d")
                text += f"\n[bold green]Period:[/] {first} → {last}"
            except:
                pass
        
        console.print(Panel(text, title="📈 Summary", border_style="cyan"))
        self.show_site_breakdown(console)
        self.show_quality_distribution(console)
    
    def show_site_breakdown(self, console: Optional[Console] = None):
        console = console or self.console
        stats = self.get_by_site()
        
        if not stats:
            return
        
        table = Table(title="🌐 Downloads by Site", box=box.ROUNDED)
        table.add_column("Site", style="cyan")
        table.add_column("Downloads", style="green", justify="right")
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("Avg Quality", style="magenta", justify="right")
        
        for site, s in sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True):
            table.add_row(site.title(), str(s["count"]), self._format_size(s["size"]),
                         f"{s['avg_quality']}p" if s["avg_quality"] else "N/A")
        
        console.print(table)
    
    def show_quality_distribution(self, console: Optional[Console] = None):
        console = console or self.console
        stats = self.get_by_quality()
        
        if not stats:
            return
        
        total = sum(stats.values())
        
        table = Table(title="📺 Quality Distribution", box=box.ROUNDED)
        table.add_column("Quality", style="cyan")
        table.add_column("Count", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")
        table.add_column("Bar", style="magenta")
        
        for quality, count in stats.items():
            pct = (count / total) * 100
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            table.add_row(f"{quality}p", str(count), f"{pct:.1f}%", bar)
        
        console.print(table)
    
    def show_timeline(self, console: Optional[Console] = None, days: int = 7):
        console = console or self.console
        stats = self.get_by_date(days)
        
        if not stats:
            console.print("[yellow]No recent download data available.[/]")
            return
        
        table = Table(title=f"📅 Last {days} Days", box=box.ROUNDED)
        table.add_column("Date", style="cyan")
        table.add_column("Downloads", style="green", justify="right")
        table.add_column("Activity", style="magenta")
        
        max_count = max(d["count"] for d in stats) if stats else 1
        
        for day in stats:
            bar = "█" * int((day["count"] / max_count) * 20)
            table.add_row(day["date"], str(day["count"]), bar)
        
        console.print(table)
    
    def show_search_stats(self, console: Optional[Console] = None):
        console = console or self.console
        stats = self.get_search_stats()
        top = self.get_top_searches(5)
        
        console.print(f"\n[bold cyan]🔍 Search Statistics[/]")
        console.print(f"Total Searches: [green]{stats['total_searches']}[/]")
        console.print(f"Unique Queries: [green]{stats['unique_queries']}[/]")
        
        if top:
            console.print("\n[bold]Top Searches:[/]")
            for i, s in enumerate(top, 1):
                console.print(f"  {i}. {s['query']} ([green]{s['count']}[/] times)")
    
    def _format_size(self, size_bytes: int) -> str:
        if size_bytes <= 0:
            return "N/A"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"


_default_stats: Optional[DownloadStatistics] = None


def GetStatistics() -> DownloadStatistics:
    global _default_stats
    if _default_stats is None:
        _default_stats = DownloadStatistics()
    return _default_stats
