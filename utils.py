import base64
import os
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from themes import CUSTOM_THEME

console = Console(theme=CUSTOM_THEME)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def decode_base64_url(encoded_string: str) -> Optional[str]:
    try:
        padded_encoded = encoded_string + '=' * (4 - len(encoded_string) % 4)
        decoded_bytes = base64.b64decode(padded_encoded)
        return decoded_bytes.decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError):
        return None

def format_timestamp(ts: any) -> str:
    try:
        return datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return "Timestamp tidak valid"

def create_header(text: str, style: str = "header") -> Panel:
    return Panel(
        Text(text, justify="center", style=style),
        border_style="title",
        subtitle_align="center"
    )

def show_message(message: str, title: str, style: str):
    console.print(Panel(message, title=f"[{style}]{title}[/{style}]", border_style=style, expand=False))
