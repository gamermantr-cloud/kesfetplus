"""Server-side proxy for displaying real Google Places photos safely.

Context: `scripts/fetch_google_places_photos.py` attached real Google Places
photo *metadata* (`place_id`, `photo_name`, `attribution`) to 363 seed venues
in `database/seed/places.json`/`gurme.json`/`hotels.json`. It deliberately
left `photos[].url` as `null` for those entries: `database/seed/*.json` is
mirrored verbatim into `frontend/public/data/*.json` and served to the
browser as a static file (see CLAUDE.md), so writing a Google Photo Media
URL with an embedded `?key=...` into that JSON would leak the API key to
every visitor (open devtools -> steal the key -> drain the project's quota).

This module is the "proxy endpoint" that script's docstring said was needed:
it calls Google's Place Photo Media (New) endpoint *from the backend*, using
the key from `GOOGLE_PLACES_API_KEY` (read once via `os.getenv`, never
logged/returned/embedded anywhere), and hands back only the short-lived,
key-free `photoUri` Google's own CDN already signs for us. See
api/main.py's `GET /places/photo` for the route that puts this behind a
307 redirect.

Cache: same in-memory dict + threading.Lock + TTL pattern as
database/weather_cache.py (no disk persistence - a cache miss just costs one
more Google call). 12-hour TTL: Google's documented guidance is that a
`photoUri` stays valid for roughly that long, and re-resolving well before
expiry avoids ever handing out a URL that's about to 403.

Honesty rule (CLAUDE.md "sahte/uydurma veri kesinlikle yasak"): if Google
can't actually be reached, or returns an error/unparseable body,
`resolve_photo_uri` raises `PhotoUnavailableError` - never a placeholder or
previously-cached-forever URL once it's known stale.

SECURITY - closed proxy, not an open one: `resolve_photo_uri` first checks
that `photo_name` is one that genuinely exists in our own seed data (loaded
from the same three JSON files `fetch_google_places_photos.py` writes to,
via `_known_photo_names()`). Without this check, this module would let
anyone who can reach the API ask our backend to spend our Google quota
resolving *any* Google Place's photo they like - an open proxy / quota-
exhaustion vector. An unrecognized `photo_name` raises `UnknownPhotoNameError`
(api/main.py turns this into 404) before any network call or cache lookup
happens, so it costs nothing.

Seed data is loaded once per process and cached with `functools.lru_cache`,
same choice `database/photo_compare.py._venue_first_photo_urls` already
made for the identical "place_id -> seed field" lookup shape: this data only
changes when a script rewrites the seed files and the backend restarts, so
re-reading three ~tens-of-thousands-line JSON files on every single photo
request would be pure waste for no freshness benefit.
"""

from __future__ import annotations

import json
import os
import threading
import time
from functools import lru_cache

import requests

_SEED_DIR = os.path.join(os.path.dirname(__file__), "seed")
_SEED_FILES = ("places.json", "gurme.json", "hotels.json")

_PHOTO_MEDIA_BASE_URL = "https://places.googleapis.com/v1"
_REQUEST_TIMEOUT_SECONDS = 10

# Google's Place Photo Media (New) endpoint accepts maxWidthPx in [1, 4800].
# We additionally cap it well below that server-side: nothing in this app
# needs a wider image than this, and refusing silly values keeps a buggy/
# malicious caller from using this proxy to pull needlessly large (quota-
# costly) images.
MIN_MAX_WIDTH_PX = 10
MAX_MAX_WIDTH_PX = 1600
DEFAULT_MAX_WIDTH_PX = 800

CACHE_TTL_SECONDS = 12 * 60 * 60  # 12 saat - modül docstring'ine bak

_lock = threading.Lock()
# (photo_name, max_width_px) -> (fetched_at_monotonic, photo_uri)
_cache: dict[tuple[str, int], tuple[float, str]] = {}


class PhotoUnavailableError(Exception):
    """Google'a gerçekten ulaşılamadı / anlamlı bir yanıt dönmedi. Çağıran
    bunu dürüst bir hata olarak göstermeli - asla sahte/placeholder bir URL
    ile telafi etmemeli (CLAUDE.md "sahte veri yasak")."""


class UnknownPhotoNameError(Exception):
    """`photo_name` bizim kendi seed verimizde (places/gurme/hotels.json)
    gerçekten yok. Bu, bu proxy'nin rastgele bir Google photo_name için
    çağrılmasını (kota tüketimi/kötüye kullanım riski) önleyen güvenlik
    kontrolüdür - api/main.py bunu 404'e çevirir."""


@lru_cache(maxsize=1)
def _known_photo_names() -> frozenset[str]:
    """Her üç seed dosyasındaki tüm venue.photos[].photo_name değerlerinin
    kümesi. Süreç başına bir kez yüklenir (bkz. modül docstring'i) -
    fetch_google_places_photos.py'nin yazdığı dosyalarla aynı konum/şekil."""
    names: set[str] = set()
    for filename in _SEED_FILES:
        path = os.path.join(_SEED_DIR, filename)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for venue in json.load(f):
                for photo in venue.get("photos") or []:
                    photo_name = photo.get("photo_name")
                    if photo_name:
                        names.add(photo_name)
    return frozenset(names)


def is_known_photo_name(photo_name: str) -> bool:
    """Public helper so api/main.py can return a clean 404 for an unknown
    photo_name without having to know resolve_photo_uri's internals."""
    return photo_name in _known_photo_names()


def _clamp_max_width(max_width_px: int) -> int:
    return max(MIN_MAX_WIDTH_PX, min(MAX_MAX_WIDTH_PX, max_width_px))


def _fetch_photo_uri_from_google(photo_name: str, max_width_px: int, api_key: str) -> str:
    url = f"{_PHOTO_MEDIA_BASE_URL}/{photo_name}/media"
    try:
        response = requests.get(
            url,
            params={
                "key": api_key,
                "maxWidthPx": str(max_width_px),
                # Google resolves and returns the CDN URL as JSON instead of
                # issuing an HTTP redirect itself - we do our own 307 at the
                # api/main.py layer, after stripping our key out of the
                # picture entirely.
                "skipHttpRedirect": "true",
            },
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise PhotoUnavailableError(f"Google Places Photo Media'ya ulaşılamadı: {exc}") from exc

    if response.status_code != 200:
        # Never include the request URL/params in the message - the key is
        # a query param on `url`/`response.request.url` and must not leak
        # into logs or an API error response.
        raise PhotoUnavailableError(
            f"Google Places Photo Media beklenmeyen durum kodu döndürdü: {response.status_code}"
        )

    try:
        payload = response.json()
        photo_uri = payload["photoUri"]
    except (ValueError, KeyError, TypeError) as exc:
        raise PhotoUnavailableError(
            f"Google Places Photo Media yanıtı beklenmeyen biçimde: {exc}"
        ) from exc

    if not isinstance(photo_uri, str) or not photo_uri:
        raise PhotoUnavailableError("Google Places Photo Media boş bir photoUri döndürdü.")
    return photo_uri


def resolve_photo_uri(photo_name: str, max_width_px: int = DEFAULT_MAX_WIDTH_PX) -> str:
    """`photo_name` (ör. "places/ChIJ.../photos/Aa-ng...") için Google'ın
    kendi CDN'inden gelen, bizim API key'imizi İÇERMEYEN imzalı `photoUri`'yi
    döndürür.

    Güvenlik: `photo_name` seed verimizde yoksa hiçbir ağ çağrısı/cache
    kontrolü yapılmadan UnknownPhotoNameError fırlatılır (bkz. modül
    docstring'i "SECURITY" bölümü).

    Taze bir cache kaydı varsa (CACHE_TTL_SECONDS'tan genç) onu döner;
    yoksa Google'a gerçekten çağrı yapar ve sonucu cache'e yazar. Google'a
    ulaşılamazsa/hata dönerse PhotoUnavailableError fırlatır - asla sahte/
    placeholder bir URL döndürmez.

    GOOGLE_PLACES_API_KEY değeri hiçbir zaman loglanmaz, response'a
    yazılmaz ya da hata mesajına gömülmez - sadece Google'a yapılan isteğin
    bir query param'ı olarak kullanılır.
    """
    if not is_known_photo_name(photo_name):
        raise UnknownPhotoNameError("Bilinmeyen photo_name - seed verimizde bu fotoğraf kaydı yok.")

    max_width_px = _clamp_max_width(max_width_px)
    cache_key = (photo_name, max_width_px)
    now = time.monotonic()

    with _lock:
        cached = _cache.get(cache_key)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise PhotoUnavailableError(
            "GOOGLE_PLACES_API_KEY .env içinde tanımlı değil - fotoğraf çözümlenemez."
        )

    photo_uri = _fetch_photo_uri_from_google(photo_name, max_width_px, api_key)

    with _lock:
        _cache[cache_key] = (now, photo_uri)
    return photo_uri
