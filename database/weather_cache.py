"""Server-side, district-level shared weather cache for the "hava
durumuna duyarlı mekan önerileri" MVP - see
docs/research/yeni-ozellik-onerisi-hava-durumu-onerileri.md.

Calls Open-Meteo (https://open-meteo.com/en/docs): free, no API key or
account required for non-commercial use; current temperature,
precipitation and a WMO weather code for any lat/lng. Its data is
CC BY 4.0, so the frontend shows a "Hava durumu verisi: Open-Meteo.com"
attribution line (see frontend/src/screens/Home.jsx) - not optional,
see the research doc's "riskler" section.

Honesty rule (CLAUDE.md "sahte/uydurma veri kesinlikle yasak"): if
Open-Meteo can't actually be reached (network error, bad status,
unparseable body), get_weather() raises WeatherUnavailableError. There
is no synthetic/last-known-good fallback value - api/main.py turns this
into an honest error response and the frontend shows "hava durumu bilgisi
şu an yok", never a made-up temperature or condition.

Cache: a plain in-memory dict + threading.Lock, keyed by the resolved
district name, TTL-based (no disk persistence - a cache miss just means
one more Open-Meteo call, the data is trivially re-fetchable so there's
nothing worth persisting). Same "single-process only" limitation already
documented in database/checkins_store.py's KNOWN LIMITATION note - a
multi-worker deploy would need a shared cache (e.g. Redis) instead.
30-minute TTL: even if every one of Istanbul's ~37 districts below is
requested once per TTL window, that's 37 * 48 = ~1,776 calls/day, far
under Open-Meteo's free 10,000/day quota (see the research doc's
"Rate-limit hesabı").
"""

import logging
import threading
import time

import requests

logger = logging.getLogger(__name__)

# Mirrors frontend/src/lib/districts.js DISTRICT_LATLNG and
# database/checkins_store.py's _DISTRICT_LATLNG exactly - kept in sync
# manually, same pattern/caveat noted in that file (the frontend has no
# build step that shares this table with Python).
DISTRICT_LATLNG: dict[str, tuple[float, float]] = {
    "Sarıyer": (41.167, 29.058),
    "Beşiktaş": (41.043, 29.009),
    "Şişli": (41.06, 28.988),
    "Beyoğlu": (41.037, 28.977),
    "Eyüpsultan": (41.048, 28.934),
    "Kağıthane": (41.079, 28.972),
    "Fatih": (41.019, 28.949),
    "Zeytinburnu": (40.995, 28.902),
    "Bakırköy": (40.982, 28.872),
    "Bahçelievler": (41.0, 28.859),
    "Bağcılar": (41.039, 28.856),
    "Esenler": (41.045, 28.879),
    "Bayrampaşa": (41.047, 28.907),
    "Gaziosmanpaşa": (41.065, 28.915),
    "Sultangazi": (41.106, 28.867),
    "Arnavutköy": (41.185, 28.74),
    "Başakşehir": (41.093, 28.802),
    "Küçükçekmece": (41.0, 28.775),
    "Avcılar": (40.98, 28.721),
    "Esenyurt": (41.033, 28.674),
    "Beylikdüzü": (41.0, 28.64),
    "Büyükçekmece": (41.02, 28.585),
    "Çatalca": (41.143, 28.461),
    "Silivri": (41.073, 28.247),
    "Beykoz": (41.124, 29.1),
    "Üsküdar": (41.027, 29.015),
    "Kadıköy": (40.99, 29.028),
    "Ataşehir": (40.992, 29.125),
    "Ümraniye": (41.016, 29.124),
    "Çekmeköy": (41.035, 29.198),
    "Sancaktepe": (41.0, 29.228),
    "Sultanbeyli": (40.962, 29.266),
    "Kartal": (40.907, 29.188),
    "Maltepe": (40.935, 29.156),
    "Pendik": (40.877, 29.253),
    "Tuzla": (40.816, 29.301),
    "Şile": (41.174, 29.612),
    "Adalar": (40.877, 29.125),
}
# Same fallback point as database/checkins_store.py's _DEFAULT_LATLNG -
# used when the requested district doesn't match any known name (e.g. the
# frontend's "no GPS permission" default).
DEFAULT_LATLNG: tuple[float, float] = (41.02, 28.965)
DEFAULT_DISTRICT_LABEL = "İstanbul (genel)"

CACHE_TTL_SECONDS = 30 * 60  # 30 dakika - modül docstring'indeki hesaba bak

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_REQUEST_TIMEOUT_SECONDS = 6

_lock = threading.Lock()
# resolved_district_name -> (fetched_at_monotonic, payload)
_cache: dict[str, tuple[float, dict]] = {}


class WeatherUnavailableError(Exception):
    """Raised when Open-Meteo can't be reached or returns something this
    module can't parse. Callers must surface this as an honest "veri yok"
    state - never paper over it with a fabricated temperature/condition
    (see module docstring)."""


def _resolve_district(district: str | None) -> tuple[str, float, float]:
    """(display_name, lat, lng) for a requested district string.

    Same substring-match approach as checkins_store._district_center:
    `district` may be a bare district name ("Sarıyer") or a venue's full
    "area" string ("Sarıyer (Emirgan)") - either way, the first known
    district name that appears *within* it wins. Falls back to Istanbul's
    rough center (DEFAULT_LATLNG) for an unrecognized or empty district -
    this is the "kullanıcının GPS'i yoksa varsayılan İstanbul merkezi"
    case, not an error.
    """
    if district:
        for name, (lat, lng) in DISTRICT_LATLNG.items():
            if name in district:
                return name, lat, lng
    return DEFAULT_DISTRICT_LABEL, DEFAULT_LATLNG[0], DEFAULT_LATLNG[1]


# WMO weather code -> (Turkish label, coarse group). Table per Open-Meteo
# docs (https://open-meteo.com/en/docs); groups are only used to decide
# is_outdoor_friendly below.
_WMO_GROUPS: dict[str, tuple[str, tuple[int, ...]]] = {
    "clear": ("Açık", (0,)),
    "cloudy": ("Parçalı bulutlu", (1, 2, 3)),
    "fog": ("Sisli", (45, 48)),
    "rain": ("Yağmurlu", (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82)),
    "snow": ("Karlı", (71, 73, 75, 77, 85, 86)),
    "storm": ("Fırtınalı", (95, 96, 99)),
}
_CODE_TO_GROUP: dict[int, str] = {
    code: group for group, (_, codes) in _WMO_GROUPS.items() for code in codes
}
# Outdoor mekanlar için elverişsiz sayılan gruplar (yağış/görüş riski).
_BAD_OUTDOOR_GROUPS = {"rain", "snow", "storm", "fog"}
# mm cinsinden - Open-Meteo'nun "precipitation" alanı, weather_code rain/
# snow/storm/fog grubunda olmasa bile hafif bir yağışı yakalayabilir.
_PRECIPITATION_THRESHOLD_MM = 0.2


def _condition_for_code(code: int | None) -> tuple[str, str]:
    if code is None:
        return "Bilinmiyor", "unknown"
    group = _CODE_TO_GROUP.get(code)
    if group is None:
        return "Bilinmiyor", "unknown"
    label = _WMO_GROUPS[group][0]
    return label, group


def _fetch_from_open_meteo(lat: float, lng: float) -> dict:
    try:
        response = requests.get(
            _OPEN_METEO_URL,
            params={
                "latitude": str(lat),
                "longitude": str(lng),
                "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
                "timezone": "Europe/Istanbul",
            },
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise WeatherUnavailableError(f"Open-Meteo'ya ulaşılamadı: {exc}") from exc

    if response.status_code != 200:
        raise WeatherUnavailableError(
            f"Open-Meteo beklenmeyen durum kodu döndürdü: {response.status_code}"
        )

    try:
        payload = response.json()
        current = payload["current"]
        temperature = float(current["temperature_2m"])
        precipitation = float(current.get("precipitation") or 0.0)
        raw_code = current.get("weather_code")
        weather_code = int(raw_code) if raw_code is not None else None
        wind_speed = current.get("wind_speed_10m")
        observed_at = current.get("time")
    except (KeyError, TypeError, ValueError) as exc:
        raise WeatherUnavailableError(f"Open-Meteo yanıtı beklenmeyen biçimde: {exc}") from exc

    condition_label, condition_group = _condition_for_code(weather_code)
    is_outdoor_friendly = (
        condition_group not in _BAD_OUTDOOR_GROUPS and precipitation <= _PRECIPITATION_THRESHOLD_MM
    )

    return {
        "temperature": temperature,
        "precipitation": precipitation,
        "condition": condition_label,
        "condition_group": condition_group,
        "wind_speed": wind_speed,
        "is_outdoor_friendly": is_outdoor_friendly,
        "observed_at": observed_at,
        "source": "open-meteo.com",
    }


def get_weather(district: str | None) -> dict:
    """Public entry point for GET /weather/{district} (api/main.py).

    Resolves `district` to a coordinate (see _resolve_district), serves a
    cached response if it's younger than CACHE_TTL_SECONDS, otherwise
    calls Open-Meteo and caches the fresh result. Raises
    WeatherUnavailableError - never a fabricated fallback - if Open-Meteo
    can't be reached; the lock is only held around the cache dict itself,
    never around the network call.
    """
    resolved_name, lat, lng = _resolve_district(district)
    now = time.monotonic()

    with _lock:
        cached = _cache.get(resolved_name)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return {**cached[1], "district": resolved_name, "cached": True}

    fresh = _fetch_from_open_meteo(lat, lng)
    with _lock:
        _cache[resolved_name] = (now, fresh)
    return {**fresh, "district": resolved_name, "cached": False}
