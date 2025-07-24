import json
import time
from typing import Any, Dict, List, Optional

from constants import (CACHE_FILE, DEFAULT_CACHE,
                                     CACHE_KEY_FAVORITES,
                                     CACHE_KEY_ANIME_DETAILS,
                                     CACHE_KEY_SEARCH_HISTORY,
                                     CACHE_KEY_WATCHED_EPISODES,
                                     CACHE_KEY_LAST_EPISODE_CHECK,
                                     CACHE_KEY_FULL_ANIME_LIST)
from utils import show_message

class CacheManager:

    def __init__(self):
        self._cache: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not CACHE_FILE.exists():
            return DEFAULT_CACHE.copy()
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key, default_value in DEFAULT_CACHE.items():
                if key not in data:
                    data[key] = default_value

            favs = data.get(CACHE_KEY_FAVORITES)
            if isinstance(favs, dict):
                data[CACHE_KEY_FAVORITES] = list(favs.values())
            elif not isinstance(favs, list):
                data[CACHE_KEY_FAVORITES] = []
            
            return data
            
        except (json.JSONDecodeError, IOError):
            show_message(
                f"File cache di {CACHE_FILE} rusak atau tidak dapat dibaca. Memulai dengan cache baru.",
                "Peringatan Cache", "warning"
            )
            return DEFAULT_CACHE.copy()

    def save(self):
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except IOError:
            show_message(
                f"Gagal menyimpan cache ke {CACHE_FILE}. Periksa izin file.",
                "Error Cache", "error"
            )

    def get_anime_details(self, url: str) -> Optional[Dict[str, Any]]:
        return self._cache[CACHE_KEY_ANIME_DETAILS].get(url)

    def set_anime_details(self, url: str, details: Dict[str, Any]):
        self._cache[CACHE_KEY_ANIME_DETAILS][url] = details
        self.save()

    def get_all_cached_details(self) -> Dict[str, Any]:
        return self._cache[CACHE_KEY_ANIME_DETAILS]

    def get_favorites(self) -> List[Dict[str, Any]]:
        return self._cache[CACHE_KEY_FAVORITES]

    def add_to_favorites(self, anime: Dict[str, Any]) -> bool:
        if not any(fav['url'] == anime['url'] for fav in self.get_favorites()):
            self._cache[CACHE_KEY_FAVORITES].append(anime)
            self.save()
            return True
        return False

    def remove_from_favorites(self, index: int) -> Optional[Dict[str, Any]]:
        if 0 <= index < len(self.get_favorites()):
            removed = self._cache[CACHE_KEY_FAVORITES].pop(index)
            self.save()
            return removed
        return None

    def get_search_history(self) -> List[Dict[str, Any]]:
        return self._cache[CACHE_KEY_SEARCH_HISTORY]

    def add_to_search_history(self, query: str):
        self._cache[CACHE_KEY_SEARCH_HISTORY] = [
            item for item in self.get_search_history() if item['query'] != query
        ]
        self._cache[CACHE_KEY_SEARCH_HISTORY].insert(0, {"query": query, "timestamp": time.time()})
        self._cache[CACHE_KEY_SEARCH_HISTORY] = self.get_search_history()[:50]
        self.save()

    def is_episode_watched(self, episode_url: str) -> bool:
        return episode_url in self._cache[CACHE_KEY_WATCHED_EPISODES]

    def mark_episode_as_watched(self, episode_url: str):
        self._cache[CACHE_KEY_WATCHED_EPISODES][episode_url] = time.time()
        self.save()

    def get_last_episode_check(self, anime_url: str) -> Optional[int]:
        return self._cache[CACHE_KEY_LAST_EPISODE_CHECK].get(anime_url)

    def update_last_episode_check(self, anime_url: str, episode_count: int):
        self._cache[CACHE_KEY_LAST_EPISODE_CHECK][anime_url] = episode_count
        self.save()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "favorites_count": len(self.get_favorites()),
            "details_cached_count": len(self.get_all_cached_details()),
            "search_history_count": len(self.get_search_history()),
            "watched_episodes_count": len(self._cache[CACHE_KEY_WATCHED_EPISODES]),
            "cache_file_location": str(CACHE_FILE.resolve())
        }

    def clear_anime_details_cache(self):
        self._cache[CACHE_KEY_ANIME_DETAILS] = {}
        self.save()

    def clear_search_history(self):
        """Membersihkan riwayat pencarian."""
        self._cache[CACHE_KEY_SEARCH_HISTORY] = []
        self.save()

    def get_all_data(self) -> Dict[str, Any]:
        return self._cache
