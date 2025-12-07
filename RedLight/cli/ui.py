from rich.console import Console
from rich.panel import Panel
from rich import box
from ..database import DatabaseManager
from ..version import __version__, __description__, __author__

console = Console()
db = DatabaseManager()

BANNER = """
[bold cyan]╔══════════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold magenta]██████╗ ███████╗██████╗ ██╗     ██╗ ██████╗ ██╗  ██╗████████╗[/]   [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔══██╗██╔════╝██╔══██╗██║     ██║██╔════╝ ██║  ██║╚══██╔══╝[/]   [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██████╔╝█████╗  ██║  ██║██║     ██║██║  ███╗███████║   ██║   [/]   [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██╔══██╗██╔══╝  ██║  ██║██║     ██║██║   ██║██╔══██║   ██║   [/]   [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]██║  ██║███████╗██████╔╝███████╗██║╚██████╔╝██║  ██║   ██║   [/]   [bold cyan]║[/]
[bold cyan]║[/]  [bold magenta]╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   [/]   [bold cyan]║[/]
[bold cyan]║[/]          [bold yellow]Professional Adult Content Downloader                [/]   [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════════════════╝[/]
                [dim]version 1.0.14 • RedLight DL[/]
"""

def show_banner():
    console.print(BANNER)

def show_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    
    version_info = Panel(
        f"[bold cyan]RedLight DL[/]\n\n"
        f"[yellow]Version:[/] [bold white]{__version__}[/]\n"
        f"[yellow]Author:[/] [bold white]{__author__}[/]\n"
        f"[yellow]Description:[/] [dim]{__description__}[/]\n\n"
        f"[dim]For more information, visit:[/]\n"
        f"[link=https://github.com/diastom/RedLightDL]https://github.com/diastom/RedLightDL[/]",
        title="[bold magenta]📦 Package Info[/]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(version_info)
    ctx.exit()

def show_history(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    db.show_history(console)
    ctx.exit()

def show_stats(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    db.show_stats(console)
    ctx.exit()
