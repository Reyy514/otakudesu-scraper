import requests
from pathlib import Path
from typing import Optional

from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.console import Console

from constants import EXPORT_DIR, HTTP_HEADERS
from themes import CUSTOM_THEME

console = Console(theme=CUSTOM_THEME)

def download_file(url: str, title: str) -> Optional[Path]:
    safe_filename = "".join([c for c in title if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()
    if not Path(safe_filename).suffix:
        safe_filename += ".mp4"
        
    destination = EXPORT_DIR / safe_filename

    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
        transient=True
    )

    try:
        with requests.get(url, stream=True, headers=HTTP_HEADERS, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with progress:
                task_id = progress.add_task("download", total=total_size, filename=safe_filename)
                with open(destination, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task_id, advance=len(chunk))
        
        console.print(f"[success]✅ Unduhan selesai! File disimpan di:[/success] [info]{destination}[/info]")
        return destination
    except requests.exceptions.RequestException as e:
        console.print(f"[error]❌ Gagal mengunduh file: {e}[/error]")
        if destination.exists():
            destination.unlink()
        return None
    except Exception as e:
        console.print(f"[error]❌ Terjadi error tak terduga saat mengunduh: {e}[/error]")
        if destination.exists():
            destination.unlink()
        return None
