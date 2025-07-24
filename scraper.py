import requests
import re
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from rich.console import Console

from constants import BASE_URL, HTTP_HEADERS
from utils import decode_base64_url
from themes import CUSTOM_THEME

console = Console(theme=CUSTOM_THEME)

class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

    def check_connection(self) -> bool:
        try:
            response = self.session.get(BASE_URL, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.exceptions.RequestException as e:
            console.print(f"[error]Gagal mengakses {url}: {e}[/error]")
            return None

    def search_anime(self, query: str) -> Optional[List[Dict[str, str]]]:
        search_url = f"{BASE_URL}/?s={query}&post_type=anime"
        soup = self._get_soup(search_url)
        if not soup: return None
        results = []
        search_container = soup.find('ul', class_='chivsrc')
        if not search_container: return []
        for item in search_container.find_all('li'):
            link_tag, title_tag = item.find('a'), item.find('h2')
            if link_tag and title_tag:
                results.append({"title": title_tag.text.strip(), "url": link_tag['href']})
        return results

    def get_anime_list(self, list_type: str, page: int = 1) -> Optional[Tuple[List[Dict[str, str]], bool]]:
        url = urljoin(BASE_URL, f"{list_type}/page/{page}/")
        soup = self._get_soup(url)
        if not soup: return None, False
        anime_list = []
        container = soup.find('div', class_='venz')
        if not container:
            container = soup.find('div', class_='venser')
        
        if not container: return [], False

        items = container.find_all('li')
        if not items:
            items = container.find_all('div', class_='col-anime')

        for item in items:
            title_tag = item.find('h2') or item.find(class_='col-anime-title')
            link_tag = item.find('a')
            if title_tag and link_tag:
                actual_link = title_tag.find('a') or link_tag
                anime_list.append({"title": actual_link.text.strip(), "url": actual_link['href']})

        pagination = soup.find('div', class_='pagination')
        has_next_page = pagination.find('a', class_='next') is not None if pagination else False
        return anime_list, has_next_page
    
    def get_all_anime_from_genre(self, genre_slug: str) -> Optional[List[Dict[str, str]]]:
        page = 1
        all_anime = []
        while True:
            anime_on_page, has_next_page = self.get_anime_list(f"genres/{genre_slug}", page)
            
            if anime_on_page:
                all_anime.extend(anime_on_page)
            
            if not has_next_page or not anime_on_page:
                break
            
            page += 1
            time.sleep(0.2)

        return sorted(all_anime, key=lambda x: x['title']) if all_anime else None

    def get_full_anime_list(self) -> Optional[List[Dict[str, str]]]:
        list_url = f"{BASE_URL}/anime-list/"
        soup = self._get_soup(list_url)
        if not soup: return None
        
        anime_list = []
        columns = soup.select('#abtext .bariskelom')
        for column in columns:
            links = column.find_all('a', href=True)
            for link in links:
                anime_list.append({"title": link.text.strip(), "url": link['href']})
        
        return sorted(anime_list, key=lambda x: x['title'])

    def get_release_schedule(self) -> Optional[Dict[str, List[Dict[str, str]]]]:
        schedule_url = f"{BASE_URL}/jadwal-rilis/"
        soup = self._get_soup(schedule_url)
        if not soup: return None

        schedule = {}
        schedule_container = soup.find('div', class_='kgjdwl321')
        if not schedule_container: return None
        
        day_containers = schedule_container.find_all('div', class_='kglist321')
        for day_container in day_containers:
            day_name_tag = day_container.find('h2')
            if not day_name_tag: continue
            
            day_name = day_name_tag.text.strip()
            anime_list = []
            
            anime_ul = day_container.find('ul')
            if anime_ul:
                for anime_item in anime_ul.find_all('li'):
                    link_tag = anime_item.find('a')
                    if link_tag:
                        anime_list.append({
                            "title": link_tag.text.strip(),
                            "url": link_tag['href']
                        })
            schedule[day_name] = anime_list
        return schedule

    def get_genre_list(self) -> Optional[List[Dict[str, str]]]:
        genre_list_url = f"{BASE_URL}/genre-list/"
        soup = self._get_soup(genre_list_url)
        if not soup: return None

        genres = []
        genre_container = soup.find('ul', class_='genres')
        if not genre_container:
            genre_container = soup.find('div', id='genrez')
        if not genre_container:
            genre_container = soup.find('div', class_='genre-list')

        if genre_container:
            for genre_link in genre_container.find_all('a'):
                genres.append({
                    "name": genre_link.text.strip(),
                    "url": genre_link['href']
                })
        return sorted(genres, key=lambda x: x['name'])

    def _extract_episodes_and_batch(self, soup: BeautifulSoup) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        episodes = []
        batch_links = []
        
        all_episode_lists = soup.find_all('div', class_='episodelist')
        
        for container in all_episode_lists:
            title_tag = container.find('span', class_='monktit')
            title = title_tag.text.lower() if title_tag else ""
            
            links = container.find_all('a', href=True)
            
            if 'batch' in title:
                for link in links:
                    batch_links.append({"title": link.text.strip(), "url": urljoin(BASE_URL, link['href'])})
            elif 'episode list' in title:
                for link in links:
                    episodes.append({"title": link.text.strip(), "url": urljoin(BASE_URL, link['href'])})
        
        if not episodes and not batch_links:
            all_links = soup.find_all('a', href=True)
            batch_urls = set()
            batch_pattern = re.compile(r'batch', re.I)

            for link in all_links:
                href = urljoin(BASE_URL, link['href'])
                text = link.text.strip()
                if batch_pattern.search(href) or batch_pattern.search(text):
                    if '/episode/' not in href or 'batch' in href:
                        batch_links.append({"title": text, "url": href})
                        batch_urls.add(href)

            for link in all_links:
                href = urljoin(BASE_URL, link['href'])
                if '/episode/' in href and href not in batch_urls:
                    episodes.append({"title": link.text.strip(), "url": href})

        def get_episode_number(ep_title: str) -> int:
            match = re.search(r'Episode\s+(\d+)', ep_title, re.IGNORECASE)
            if match:
                return int(match.group(1))
            return 9999

        unique_episodes = sorted(
            list({ep['url']: ep for ep in episodes}.values()),
            key=lambda x: get_episode_number(x['title'])
        )
        unique_batch_links = list({b['url']: b for b in batch_links}.values())

        return unique_episodes, unique_batch_links

    def get_anime_details(self, anime_url: str) -> Optional[Dict[str, any]]:
        soup = self._get_soup(anime_url)
        if not soup: return None

        details: Dict[str, any] = {}
        info_element = soup.find('div', class_='infozingle')
        if not info_element: return None

        title_tag = soup.find('h1', class_='posttl')
        details['title'] = title_tag.text.strip() if title_tag else (soup.find('title').text.strip() if soup.find('title') else "Judul Tidak Ditemukan")
        
        for p_tag in info_element.find_all('p'):
            if ':' in p_tag.text:
                key, value = p_tag.text.split(':', 1)
                details[key.strip().lower().replace(" ", "_")] = value.strip()

        sinopsis_element = soup.find('div', class_='sinopc')
        details['sinopsis'] = sinopsis_element.text.strip() if sinopsis_element else "Tidak ditemukan."

        details['episodes'], details['batch_links'] = self._extract_episodes_and_batch(soup)

        return details

    def get_download_links(self, page_url: str) -> Optional[Dict[str, List[Dict[str, str]]]]:
        soup = self._get_soup(page_url)
        if not soup: return None

        download_links: Dict[str, List[Dict[str, str]]] = {}
        download_containers = soup.select('.download, .dl-box, .smokeddl, .batchlink')
        if not download_containers: return {}

        for container in download_containers:
            resolution_headers = container.find_all(['strong', 'p', 'h4'])
            for header in resolution_headers:
                resolution_text = header.text.strip()
                if not re.search(r'\d{3,4}p|mkv|mp4|batch', resolution_text, re.I):
                    continue

                links = []
                link_container = header.find_next_sibling('ul') or header.parent
                
                if link_container:
                    for a_tag in link_container.find_all('a', href=True):
                        host = a_tag.text.strip()
                        url = a_tag.get('href')
                        if 'data-content' in a_tag.attrs:
                            url = decode_base64_url(a_tag['data-content'])
                        if url and url != '#':
                            links.append({"host": host, "url": url})
                
                if links:
                    clean_resolution = re.sub(r'\[.*?\]|Subtitle Indonesia', '', resolution_text).strip()
                    if not clean_resolution:
                        clean_resolution = "Unduhan Batch" if 'batch' in page_url else "Unduhan Lainnya"
                    
                    if clean_resolution in download_links:
                        download_links[clean_resolution].extend(links)
                    else:
                        download_links[clean_resolution] = links
        
        return {k: v for k, v in download_links.items() if v}
