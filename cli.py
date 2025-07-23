import csv
import json
import time
from typing import List, Dict, Any, Optional
from collections import defaultdict

from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns

from cache_manager import CacheManager
from constants import *
from scraper import Scraper
from themes import CUSTOM_THEME
from utils import clear_screen, create_header, format_timestamp, show_message

class OtakuCLI:
    def __init__(self):
        self.console = Console(theme=CUSTOM_THEME)
        self.scraper = Scraper()
        self.cache = CacheManager()

    def run(self):
        try:
            self._check_connection_and_notify()
            self.main_menu()
        except KeyboardInterrupt:
            self.console.print("\n[warning]Program dihentikan oleh pengguna. Sampai jumpa![/warning]")
        finally:
            self.cache.save()

    def _check_connection_and_notify(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_HEADER} OTAKUDESU SCRAPER {EMOJI_HEADER}"))
        with self.console.status("[bold green]Menghubungi server Otakudesu...[/bold green]"):
            if not self.scraper.check_connection():
                show_message(f"Tidak dapat terhubung ke {BASE_URL}. Periksa koneksi internet Anda.", "Koneksi Gagal", "error")
                exit()
            self.console.print(f"[success]{EMOJI_SUCCESS} Koneksi ke {BASE_URL} berhasil![/success]\n")
        
        self._check_new_episodes()
        time.sleep(1)

    def _check_new_episodes(self):
        favorites = self.cache.get_favorites()
        if not favorites:
            return

        notifications = []
        with self.console.status("[bold blue]Mengecek episode baru untuk favorit...[/bold blue]"):
            for fav in favorites:
                last_known_count = self.cache.get_last_episode_check(fav['url'])
                details = self.scraper.get_anime_details(fav['url'])
                if details and details.get('episodes'):
                    current_episode_count = len(details['episodes'])
                    if last_known_count is None:
                        self.cache.update_last_episode_check(fav['url'], current_episode_count)
                    elif current_episode_count > last_known_count:
                        notifications.append(f"[highlight]{fav['title']}[/highlight] memiliki {current_episode_count - last_known_count} episode baru!")
                        self.cache.update_last_episode_check(fav['url'], current_episode_count)
        
        if notifications:
            notif_text = "\n".join(notifications)
            self.console.print(Panel.fit(notif_text, title=f"[{'accent'}]{EMOJI_NOTIFICATION} Notifikasi Episode Baru[{'accent'}]", border_style="accent"))
            self.console.print()


    def main_menu(self):
        while True:
            clear_screen()
            self.console.print(create_header(f"{EMOJI_HEADER} OTAKUDESU SCRAPER {EMOJI_HEADER}"))
            
            stats = self.cache.get_stats()
            status_text = (
                f"🌐 [bold]Server Aktif:[/bold] [info]{BASE_URL}[/info]\n"
                f"⭐ [bold]Favorit:[/bold] [info]{stats['favorites_count']}[/info] anime\n"
                f"💾 [bold]Cache Detail:[/bold] [info]{stats['details_cached_count']}[/info] anime"
            )
            self.console.print(Panel(status_text, title="[accent]Status Aplikasi[/accent]", border_style="cyan", expand=True))

            menu = {
                "1": f"{EMOJI_SEARCH} Cari Anime",
                "2": f"{EMOJI_ONGOING} Daftar Anime Ongoing",
                "3": f"{EMOJI_COMPLETED} Daftar Anime Completed",
                "4": f"{EMOJI_ALL_ANIME}  Daftar Lengkap Anime (A-Z)",
                "5": f"{EMOJI_SCHEDULE} Jadwal Rilis",
                "6": f"{EMOJI_GENRE} Daftar Genre",
                "7": f"{EMOJI_FAVORITE} Kelola Favorit",
                "8": f"{EMOJI_HISTORY} Riwayat & Statistik",
                "9": f"{EMOJI_EXPORT} Ekspor Data",
                "10": f"{EMOJI_HELP} Bantuan",
                "11": f"{EMOJI_QUIT} Keluar",
            }

            table = Table(show_header=False, border_style="border", expand=True)
            table.add_column("No.", style="dim", width=5)
            table.add_column("Opsi")
            for num, opt in menu.items():
                table.add_row(f"({num})", opt)
            
            self.console.print(table)
            choice = Prompt.ask("[prompt]➤ Masukkan pilihan Anda[/prompt]", choices=list(menu.keys()))

            actions = {
                '1': self.search_anime_menu,
                '2': lambda: self.anime_list_menu('ongoing-anime', "Anime Ongoing"),
                '3': lambda: self.anime_list_menu('complete-anime', "Anime Completed"),
                '4': self.full_anime_list_menu,
                '5': self.release_schedule_menu,
                '6': self.genre_list_menu,
                '7': self.manage_favorites_menu,
                '8': self.history_and_stats_menu,
                '9': self.export_data_menu,
                '10': self.show_help_menu,
                '11': lambda: None,
            }
            
            action = actions.get(choice)
            if action:
                if choice == '11':
                    self.console.print(Panel(f"[success]{EMOJI_SUCCESS} Terima kasih telah menggunakan aplikasi ini! Sampai jumpa![/success]", border_style="success"))
                    break
                action()

    def search_anime_menu(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_SEARCH} Cari Anime"))
        query = Prompt.ask("[prompt]Masukkan judul anime[/prompt]").strip()
        if not query:
            return

        self.cache.add_to_search_history(query)
        with self.console.status(f"[bold green]Mencari '{query}'...[/bold green]"):
            results = self.scraper.search_anime(query)
        
        self.display_anime_list(results, f"Hasil Pencarian: '{query}'")

    def anime_list_menu(self, list_type: str, title: str):
        page = 1
        while True:
            clear_screen()
            self.console.print(create_header(f"{EMOJI_ONGOING if 'ongoing' in list_type else EMOJI_COMPLETED} {title} - Halaman {page}"))
            with self.console.status("[bold green]Memuat daftar anime...[/bold green]"):
                result, has_next_page = self.scraper.get_anime_list(list_type, page)
            
            if not result:
                show_message("Tidak ada anime di halaman ini atau halaman terakhir tercapai.", "Info", "warning")
                break
            
            self.display_anime_list(result, f"{title} - Halaman {page}")

            if has_next_page:
                if not Confirm.ask(f"[prompt]Lanjut ke halaman {page + 1}?[/prompt]"):
                    break
                page += 1
            else:
                self.console.print("[info]Ini adalah halaman terakhir.[/info]")
                Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
                break

    def full_anime_list_menu(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_ALL_ANIME} Daftar Lengkap Anime (A-Z)"))
        
        with self.console.status("[bold green]Mengambil seluruh daftar anime dari situs... Ini mungkin perlu beberapa saat.[/bold green]"):
            full_list = self.scraper.get_full_anime_list()

        if not full_list:
            show_message("Gagal mengambil daftar anime lengkap.", "Error", "error")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return
        
        grouped_anime = defaultdict(list)
        for anime in full_list:
            first_letter = anime['title'][0].upper() if anime['title'] else '#'
            if first_letter.isalpha():
                grouped_anime[first_letter].append(anime)
            else:
                grouped_anime['#'].append(anime)

        while True:
            clear_screen()
            self.console.print(create_header(f"{EMOJI_ALL_ANIME} Daftar Lengkap Anime (A-Z)"))
            
            table = Table(title="[highlight]Pilih Huruf Awal[/highlight]", border_style="cyan")
            table.add_column("Huruf", style="accent", justify="center")
            table.add_column("Jumlah Anime", style="info", justify="center")

            sorted_letters = sorted(grouped_anime.keys())
            for letter in sorted_letters:
                table.add_row(letter, str(len(grouped_anime[letter])))
            
            self.console.print(table)
            self.console.print(Panel.fit(f"• Masukkan [highlight]huruf[/highlight] untuk melihat daftar\n• Ketik [highlight]'kembali'[/highlight] untuk kembali {EMOJI_BACK}", title="[accent]Kontrol[/accent]"))

            choice = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").strip()

            if choice.lower() == 'kembali':
                break
            
            choice = choice.upper()
            if choice in grouped_anime:
                self.display_anime_list(grouped_anime[choice], f"Daftar Anime: '{choice}'")
            else:
                show_message("Pilihan tidak valid.", "Error", "error")
                time.sleep(1)

    def release_schedule_menu(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_SCHEDULE} Jadwal Rilis Anime"))
        with self.console.status("[bold green]Mengambil jadwal rilis...[/bold green]"):
            schedule = self.scraper.get_release_schedule()

        if not schedule:
            show_message("Gagal mengambil jadwal rilis.", "Error", "error")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return
        
        tree = Tree(f"[bold accent]{EMOJI_SCHEDULE} Jadwal Rilis Mingguan[/bold accent]", guide_style="cyan")
        
        flat_anime_list = []
        for day, animes in schedule.items():
            if animes:
                day_branch = tree.add(f"[highlight]{day}[/highlight]")
                for anime in animes:
                    day_branch.add(f"({len(flat_anime_list) + 1}) [info]{anime['title']}[/info]")
                    flat_anime_list.append(anime)
        
        self.console.print(tree)
        self.console.print(Panel.fit(f"• Masukkan [highlight]nomor[/highlight] untuk melihat detail\n• Ketik [highlight]'k'[/highlight] untuk kembali {EMOJI_BACK}", title="[accent]Kontrol[/accent]"))
        
        choice_str = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").lower().strip()

        if choice_str == 'k':
            return
        
        try:
            idx = int(choice_str) - 1
            if 0 <= idx < len(flat_anime_list):
                self.display_anime_details(flat_anime_list[idx]['url'])
            else:
                show_message("Nomor tidak valid.", "Error", "error")
        except ValueError:
            show_message("Input tidak valid.", "Error", "error")

    def genre_list_menu(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_GENRE} Daftar Genre"))
        with self.console.status("[bold green]Mengambil daftar genre...[/bold green]"):
            genres = self.scraper.get_genre_list()

        if not genres:
            show_message("Gagal mengambil daftar genre.", "Error", "error")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return
        
        while True:
            clear_screen()
            self.console.print(create_header(f"{EMOJI_GENRE} Daftar Genre"))
            
            table = Table(title="[highlight]Pilih Genre[/highlight]", border_style="cyan")
            table.add_column("No.", width=5)
            table.add_column("Nama Genre")
            
            for i, genre in enumerate(genres):
                table.add_row(str(i+1), genre['name'])
            
            self.console.print(table)
            self.console.print(Panel.fit(f"• Masukkan [highlight]nomor[/highlight] untuk melihat daftar anime\n• Ketik [highlight]'k'[/highlight] untuk kembali {EMOJI_BACK}", title="[accent]Kontrol[/accent]"))

            choice_str = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").lower().strip()

            if choice_str == 'k':
                break
            
            try:
                idx = int(choice_str) - 1
                if 0 <= idx < len(genres):
                    selected_genre = genres[idx]
                    genre_slug = selected_genre['url'].strip('/').split('/')[-1]
                    
                    with self.console.status(f"[bold green]Mengambil semua anime dari genre '{selected_genre['name']}'... Ini mungkin perlu waktu.[/bold green]"):
                        all_anime_in_genre = self.scraper.get_all_anime_from_genre(genre_slug)
                    
                    self.display_anime_list(all_anime_in_genre, f"Genre: {selected_genre['name']}")
                else:
                    show_message("Nomor tidak valid.", "Error", "error")
            except ValueError:
                show_message("Input tidak valid.", "Error", "error")

    def display_anime_list(self, animes: Optional[List[Dict]], title: str):
        if not animes:
            show_message("Tidak ada anime untuk ditampilkan.", "Kosong", "warning")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return

        while True:
            clear_screen()
            self.console.print(create_header(title))
            table = Table(title="[highlight]Pilih Anime[/highlight]", border_style="cyan", show_header=True, header_style="bold blue")
            table.add_column("No.", style="dim", width=5, justify="center")
            table.add_column("Judul Anime", style="info")
            
            for i, anime in enumerate(animes):
                table.add_row(str(i + 1), anime['title'])
            self.console.print(table)

            self.console.print(Panel.fit(
                f"• Masukkan [highlight]nomor[/highlight] untuk melihat detail\n"
                f"• Ketik [highlight]'f <nomor>'[/highlight] untuk menambah ke favorit\n"
                f"• Ketik [highlight]'k'[/highlight] untuk kembali {EMOJI_BACK}",
                title="[accent]Kontrol[/accent]", border_style="border"
            ))
            
            choice_str = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").lower().strip()
            
            if choice_str == 'k':
                break
            elif choice_str.startswith('f '):
                try:
                    idx = int(choice_str.split(' ')[1]) - 1
                    if 0 <= idx < len(animes):
                        if self.cache.add_to_favorites(animes[idx]):
                            show_message(f"'{animes[idx]['title']}' berhasil ditambah ke favorit!", "Sukses", "success")
                        else:
                            show_message(f"'{animes[idx]['title']}' sudah ada di favorit.", "Info", "warning")
                        time.sleep(1.5)
                    else:
                        show_message("Nomor tidak valid.", "Error", "error")
                except (ValueError, IndexError):
                    show_message("Format salah. Contoh: f 1", "Error", "error")
            else:
                try:
                    idx = int(choice_str) - 1
                    if 0 <= idx < len(animes):
                        self.display_anime_details(animes[idx]['url'])
                    else:
                        show_message("Nomor tidak valid.", "Error", "error")
                except ValueError:
                    show_message("Input tidak valid.", "Error", "error")

    def display_anime_details(self, anime_url: str):
        details = self.cache.get_anime_details(anime_url)
        if not details:
            with self.console.status("[bold green]Mengambil detail anime dari web...[/bold green]"):
                details = self.scraper.get_anime_details(anime_url)
                if details:
                    self.cache.set_anime_details(anime_url, details)
        else:
            self.console.print("[info]Memuat detail dari cache...[/info]")
            time.sleep(0.5)

        if not details:
            show_message("Gagal mengambil detail anime.", "Error", "error")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return

        while True:
            clear_screen()
            self.console.print(create_header(details.get('title', 'Detail Anime')))
            
            info_text = ""
            info_keys = ['judul', 'japanese', 'skor', 'produser', 'tipe', 'status', 'total_episode', 'durasi', 'tanggal_rilis', 'studio', 'genre']
            for key in info_keys:
                if key in details:
                    info_text += f"[bold]{key.replace('_', ' ').capitalize()}:[/bold] {details[key]}\n"
            
            info_panel = Panel.fit(info_text, title="[accent]Info[/accent]", border_style="cyan")
            
            sinopsis_panel = Panel(
                Markdown(f"### Sinopsis\n\n{details.get('sinopsis', 'N/A')}"),
                title="[accent]Cerita[/accent]", 
                border_style="border",
                expand=True
            )
            
            self.console.print(Columns([info_panel, sinopsis_panel], expand=True))

            options = []
            if details.get('episodes'):
                options.append("Lihat Daftar Episode")
            if details.get('batch_links'):
                options.append("Lihat Link Batch")
            options.append("Kembali")

            menu_table = Table(show_header=False, border_style="yellow", title="[accent]Kontrol[/accent]")
            menu_table.add_column("No.", style="dim")
            menu_table.add_column("Aksi")
            for i, opt in enumerate(options):
                menu_table.add_row(f"({i+1})", opt)
            
            self.console.print(Align.center(Panel.fit(menu_table)))
            
            choice_str = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]", choices=[str(i+1) for i in range(len(options))])
            choice_idx = int(choice_str) - 1
            selected_option = options[choice_idx]

            if selected_option == "Kembali":
                break
            elif selected_option == "Lihat Daftar Episode":
                self.display_episode_list(details.get('episodes', []), details['title'])
            elif selected_option == "Lihat Link Batch":
                self.display_batch_list(details.get('batch_links', []), details['title'])

    def display_episode_list(self, episodes: List[Dict], anime_title: str):
        if not episodes:
            show_message("Tidak ada episode untuk ditampilkan.", "Info", "warning")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return

        while True:
            clear_screen()
            self.console.print(create_header(f"Daftar Episode - {anime_title}"))
            table = Table(title="[highlight]Pilih Episode[/highlight]", border_style="cyan")
            table.add_column("No.", width=5)
            table.add_column("Judul Episode")
            table.add_column("Status", justify="center")
            for i, ep in enumerate(episodes):
                watched_status = f"[success]{EMOJI_SUCCESS}[/success]" if self.cache.is_episode_watched(ep['url']) else ""
                table.add_row(str(i + 1), ep['title'], watched_status)
            self.console.print(table)

            self.console.print(Panel.fit(f"• Masukkan [highlight]nomor[/highlight] untuk melihat link unduhan\n• Ketik [highlight]'k'[/highlight] untuk kembali {EMOJI_BACK}", title="[accent]Kontrol[/accent]"))
            choice_str = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").lower().strip()

            if choice_str == 'k':
                break
            try:
                idx = int(choice_str) - 1
                if 0 <= idx < len(episodes):
                    selected_ep = episodes[idx]
                    self.display_download_links(selected_ep['url'], selected_ep['title'])
                else:
                    show_message("Nomor tidak valid.", "Error", "error")
            except ValueError:
                show_message("Input tidak valid.", "Error", "error")

    def display_batch_list(self, batch_links: List[Dict], anime_title: str):
        if not batch_links:
            show_message("Tidak ada link batch untuk ditampilkan.", "Info", "warning")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return

        while True:
            clear_screen()
            self.console.print(create_header(f"Link Batch - {anime_title}"))
            table = Table(title="[highlight]Pilih File Batch[/highlight]", border_style="cyan")
            table.add_column("No.", width=5)
            table.add_column("Nama File")
            for i, batch in enumerate(batch_links):
                table.add_row(str(i + 1), batch['title'])
            self.console.print(table)

            self.console.print(Panel.fit(f"• Masukkan [highlight]nomor[/highlight] untuk melihat link unduhan\n• Ketik [highlight]'k'[/highlight] untuk kembali {EMOJI_BACK}", title="[accent]Kontrol[/accent]"))
            choice_str = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").lower().strip()

            if choice_str == 'k':
                break
            try:
                idx = int(choice_str) - 1
                if 0 <= idx < len(batch_links):
                    selected_batch = batch_links[idx]
                    self.display_download_links(selected_batch['url'], selected_batch['title'])
                else:
                    show_message("Nomor tidak valid.", "Error", "error")
            except ValueError:
                show_message("Input tidak valid.", "Error", "error")

    def display_download_links(self, url: str, title: str):
        with self.console.status(f"[bold green]Mengambil link untuk {title}...[/bold green]"):
            links = self.scraper.get_download_links(url)

        if not links:
            show_message("Gagal mengambil link download atau tidak ada link yang ditemukan.", "Error", "error")
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
            return
        
        while True:
            clear_screen()
            self.console.print(create_header(f"Link Download - {title}"))
            
            tree = Tree(f"[bold accent]{EMOJI_DOWNLOAD} Kualitas & Server[/bold accent]", guide_style="cyan")
            link_map = {}
            counter = 1
            for resolution, link_list in links.items():
                res_branch = tree.add(f"[info]✨ {resolution}[/info]")
                for link in link_list:
                    res_branch.add(f"({counter}) [green]{link['host']}[/green]")
                    link_map[counter] = link
                    counter += 1
            
            self.console.print(tree)
            self.console.print(Panel.fit(
                f"• Masukkan [highlight]nomor[/highlight] untuk menampilkan URL unduhan\n"
                f"• URL ini dapat Anda [highlight]salin[/highlight] dan tempel di browser atau manajer unduhan\n"
                f"• Ketik [highlight]'k'[/highlight] untuk kembali {EMOJI_BACK}", 
                title="[accent]Kontrol[/accent]"
            ))
            
            choice_str = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").lower().strip()
            if choice_str == 'k':
                break
            
            try:
                choice_idx = int(choice_str)
                if choice_idx in link_map:
                    selected_link = link_map[choice_idx]
                    self.console.print(Panel(
                        f"[bold]Host:[/bold] {selected_link['host']}\n"
                        f"[bold]URL:[/bold] [link={selected_link['url']}]{selected_link['url']}[/link]",
                        title="[success]URL Unduhan Final[/success]",
                        border_style="success",
                        expand=False
                    ))
                    self.cache.mark_episode_as_watched(url)
                    Prompt.ask("[dim]Tekan Enter untuk kembali ke daftar link...[/dim]")
                else:
                    show_message("Nomor tidak valid.", "Error", "error")
            except ValueError:
                show_message("Input tidak valid.", "Error", "error")

    def manage_favorites_menu(self):
        while True:
            clear_screen()
            self.console.print(create_header(f"{EMOJI_FAVORITE} Kelola Favorit"))
            favorites = self.cache.get_favorites()
            
            if not favorites:
                show_message("Belum ada anime favorit.", "Info", "warning")
                Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")
                return

            table = Table(title="[highlight]⭐ Daftar Favorit[/highlight]", border_style="accent")
            table.add_column("No.", width=5)
            table.add_column("Judul")
            for i, fav in enumerate(favorites):
                table.add_row(str(i + 1), fav['title'])
            self.console.print(table)
            
            self.console.print(Panel.fit(
                f"• Masukkan [highlight]nomor[/highlight] untuk melihat detail\n"
                f"• Ketik [highlight]'h <nomor>'[/highlight] untuk menghapus\n"
                f"• Ketik [highlight]'k'[/highlight] untuk kembali {EMOJI_BACK}",
                title="[accent]Kontrol Favorit[/accent]", border_style="border"
            ))
            
            choice = Prompt.ask("[prompt]➤ Pilihan Anda[/prompt]").lower().strip()
            
            if choice == 'k':
                break
            elif choice.startswith('h '):
                try:
                    idx = int(choice.split(' ')[1]) - 1
                    removed = self.cache.remove_from_favorites(idx)
                    if removed:
                        show_message(f"'{removed['title']}' dihapus dari favorit.", "Sukses", "success")
                        time.sleep(1.5)
                    else:
                        show_message("Nomor tidak valid.", "Error", "error")
                except (ValueError, IndexError):
                    show_message("Format salah. Contoh: h 1", "Error", "error")
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(favorites):
                        self.display_anime_details(favorites[idx]['url'])
                    else:
                        show_message("Nomor tidak valid.", "Error", "error")
                except ValueError:
                    show_message("Input tidak valid.", "Error", "error")

    def history_and_stats_menu(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_HISTORY} Riwayat & Statistik"))

        layout = Layout()
        layout.split_column(
            Layout(name="stats", size=8),
            Layout(name="history")
        )

        stats = self.cache.get_stats()
        stats_text = (
            f"⭐ [bold]Total Favorit:[/bold] [info]{stats['favorites_count']}[/info]\n"
            f"💾 [bold]Detail di Cache:[/bold] [info]{stats['details_cached_count']}[/info]\n"
            f"🕘 [bold]Riwayat Pencarian:[/bold] [info]{stats['search_history_count']}[/info]\n"
            f"✅ [bold]Episode Ditonton:[/bold] [info]{stats['watched_episodes_count']}[/info]\n"
            f"📁 [bold]Lokasi Cache:[/bold] [dim]{stats['cache_file_location']}[/dim]"
        )
        layout["stats"].update(Panel(stats_text, title="[highlight]📊 Statistik Aplikasi[/highlight]", border_style="cyan"))

        history = self.cache.get_search_history()
        history_table = Table(title="[highlight]Riwayat Pencarian Terakhir[/highlight]", border_style="accent")
        history_table.add_column("No.", width=5)
        history_table.add_column("Query")
        history_table.add_column("Waktu")
        for i, item in enumerate(history[:10]):
            history_table.add_row(str(i+1), item['query'], format_timestamp(item['timestamp']))
        
        layout["history"].update(Panel(history_table, border_style="border"))
        
        self.console.print(layout)

        if Confirm.ask("[prompt]Apakah Anda ingin membersihkan cache detail anime?[/prompt]"):
            self.cache.clear_anime_details_cache()
            show_message("Cache detail anime telah dibersihkan!", "Sukses", "success")
            time.sleep(1.5)
        else:
            Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")

    def export_data_menu(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_EXPORT} Ekspor Data"))
        
        self.console.print(Panel.fit(
            "Pilih data yang ingin diekspor:\n"
            "(1) Daftar Favorit\n"
            "(2) Seluruh Cache Aplikasi",
            title="[accent]Opsi Ekspor[/accent]", border_style="border"
        ))
        data_choice = Prompt.ask("[prompt]Pilihan Data[/prompt]", choices=['1', '2'])
        
        self.console.print(Panel.fit(
            "Pilih format file:\n"
            "(1) JSON (.json)\n"
            "(2) CSV (.csv)",
            title="[accent]Format File[/accent]", border_style="border"
        ))
        format_choice = Prompt.ask("[prompt]Pilihan Format[/prompt]", choices=['1', '2'])

        data_to_export = self.cache.get_favorites() if data_choice == '1' else self.cache.get_all_data()
        filename_prefix = "favorites" if data_choice == '1' else "full_cache"
        
        try:
            if format_choice == '1':
                filepath = EXPORT_DIR / f"{filename_prefix}_{int(time.time())}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data_to_export, f, indent=2, ensure_ascii=False)
            else:
                filepath = EXPORT_DIR / f"{filename_prefix}_{int(time.time())}.csv"
                if isinstance(data_to_export, list) and data_to_export:
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=data_to_export[0].keys())
                        writer.writeheader()
                        writer.writerows(data_to_export)
                elif isinstance(data_to_export, dict):
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['key', 'value'])
                        for key, value in data_to_export.items():
                            writer.writerow([key, json.dumps(value)])
                else:
                    show_message("Data kosong atau format tidak didukung untuk CSV.", "Error", "error")
                    return

            show_message(f"Data berhasil diekspor ke:\n{filepath}", "Ekspor Sukses", "success")
        except Exception as e:
            show_message(f"Gagal mengekspor data: {e}", "Error", "error")
        
        Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")

    def show_help_menu(self):
        clear_screen()
        self.console.print(create_header(f"{EMOJI_HELP} Bantuan"))
        
        help_markdown = f"""
        # 📖 Panduan Penggunaan Otakudesu CLI v2.0
        
        Aplikasi ini memungkinkan Anda untuk berinteraksi dengan situs Otakudesu langsung dari terminal.

        ## Navigasi Dasar
        - Gunakan **angka** yang tertera untuk memilih opsi dari menu.
        - Tekan **Enter** setelah mengetik pilihan Anda.
        - Di dalam daftar (seperti hasil pencarian atau favorit), gunakan perintah khusus:
            - `k` untuk **kembali** ke menu sebelumnya.
            - `f <nomor>` untuk menambahkan anime ke **favorit**.
            - `h <nomor>` untuk **menghapus** anime dari favorit.
        
        ## Fitur Unduhan (v7)
        - **{EMOJI_DOWNLOAD} Tampilkan URL**: Fitur auto-downloader telah diganti. Sekarang, memilih link akan **menampilkan URL final**.
        - **Salin & Tempel**: Anda bisa menyalin URL tersebut dan menempelkannya di browser atau manajer unduhan (IDM, dll) untuk hasil yang lebih andal.

        Terima kasih telah menggunakan aplikasi ini!
        """
        self.console.print(Panel(Markdown(help_markdown), title="[highlight]Panduan[/highlight]", border_style="border"))
        Prompt.ask("[dim]Tekan Enter untuk kembali...[/dim]")