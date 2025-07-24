from pathlib import Path

BASE_URL = "https://otakudesu.cloud"

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
EXPORT_DIR = APP_DIR / "exports"
CACHE_FILE = DATA_DIR / "cache.json"

DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

EMOJI_HEADER = "🎌"
EMOJI_SEARCH = "🔍"
EMOJI_ONGOING = "📺"
EMOJI_COMPLETED = "📚"
EMOJI_ALL_ANIME = "🗂️"
EMOJI_SCHEDULE = "📅"
EMOJI_GENRE = "🎭"
EMOJI_FAVORITE = "⭐"
EMOJI_STATS = "📊"
EMOJI_HELP = "❓"
EMOJI_HISTORY = "🕘"
EMOJI_EXPORT = "📥"
EMOJI_QUIT = "🚪"
EMOJI_NOTIFICATION = "🔔"
EMOJI_DOWNLOAD = "💾"
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_BACK = "↩️"

CACHE_KEY_FAVORITES = "favorites"
CACHE_KEY_ANIME_DETAILS = "anime_details"
CACHE_KEY_SEARCH_HISTORY = "search_history"
CACHE_KEY_WATCHED_EPISODES = "watched_episodes"
CACHE_KEY_LAST_EPISODE_CHECK = "last_episode_check"
CACHE_KEY_FULL_ANIME_LIST = "full_anime_list"

DEFAULT_CACHE = {
    CACHE_KEY_FAVORITES: [],
    CACHE_KEY_ANIME_DETAILS: {},
    CACHE_KEY_SEARCH_HISTORY: [],
    CACHE_KEY_WATCHED_EPISODES: {},
    CACHE_KEY_LAST_EPISODE_CHECK: {},
    CACHE_KEY_FULL_ANIME_LIST: {}
}

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
}
