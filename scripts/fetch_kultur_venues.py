"""Muze/cami/saray/tarihi yer mekanlarini Google Places'tan cekip
database/seed/kultur.json'a yazar.

Gercek Google Places Text Search (New) sonuclari - sahte/uydurma veri
yok. Mevcut places/gurme/hotels/sahne.json'da zaten olan bir mekan
(isim benzerligiyle) tekrar eklenmez. venue_type Google'in kendi
`types` alanindan turetilir; yalnizca net bir kulturel/tarihi sinyal
tasiyan sonuclar eklenir (sadece generic "tourist_attraction" tasiyan
belirsiz sonuclar - ör. seyahat acentalari, meydanlar - atlanir).
"""

from __future__ import annotations

import json
import os
import re
from difflib import SequenceMatcher

import requests
from dotenv import load_dotenv

load_dotenv()

SEED_DIR = os.path.join(os.path.dirname(__file__), "..", "database", "seed")
API_KEY = os.environ["GOOGLE_PLACES_API_KEY"]

QUERIES = [
    "museums in Istanbul",
    "historical landmarks in Istanbul",
    "mosques in Istanbul",
    "palaces in Istanbul",
]

FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.rating,places.userRatingCount,places.types"
)

DUPLICATE_SIMILARITY_THRESHOLD = 0.85


def search(query: str) -> list[dict]:
    r = requests.post(
        "https://places.googleapis.com/v1/places:searchText",
        json={"textQuery": query},
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": FIELD_MASK,
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json().get("places", [])


def derive_venue_type(types: list[str]) -> str | None:
    if "museum" in types or "art_museum" in types:
        return "muze"
    if "mosque" in types:
        return "cami"
    if "castle" in types:
        return "saray"
    if "historical_landmark" in types or "historical_place" in types:
        return "tarihi_yer"
    return None  # sadece generic tourist_attraction/plaza/garden - belirsiz, eklenmez


def normalize(name: str) -> str:
    name = name.lower()
    for a, b in (("ı", "i"), ("ğ", "g"), ("ü", "u"), ("ş", "s"), ("ö", "o"), ("ç", "c")):
        name = name.replace(a, b)
    return re.sub(r"[^a-z0-9 ]", "", name).strip()


def slugify(name: str) -> str:
    base = normalize(name).replace(" ", "-")
    return re.sub(r"-+", "-", base).strip("-")


def load_existing_names() -> list[str]:
    names = []
    for f in ("places.json", "gurme.json", "hotels.json", "sahne.json"):
        data = json.load(open(os.path.join(SEED_DIR, f), encoding="utf-8"))
        names.extend(normalize(v["name"]) for v in data)
    return names


def is_duplicate(name: str, existing: list[str]) -> bool:
    n = normalize(name)
    return any(SequenceMatcher(None, n, e).ratio() >= DUPLICATE_SIMILARITY_THRESHOLD for e in existing)


def main() -> None:
    existing_names = load_existing_names()
    kultur_path = os.path.join(SEED_DIR, "kultur.json")
    existing_kultur = []
    if os.path.exists(kultur_path):
        existing_kultur = json.load(open(kultur_path, encoding="utf-8"))
    existing_ids = {v["id"] for v in existing_kultur}
    seen_names = [normalize(v["name"]) for v in existing_kultur] + existing_names

    new_venues = []
    skipped_duplicate = 0
    skipped_no_type = 0
    for query in QUERIES:
        results = search(query)
        print(f'"{query}": {len(results)} sonuc')
        for p in results:
            name = p.get("displayName", {}).get("text", "")
            if not name:
                continue
            if is_duplicate(name, seen_names):
                skipped_duplicate += 1
                continue
            venue_type = derive_venue_type(p.get("types", []))
            if venue_type is None:
                skipped_no_type += 1
                continue
            venue_id = slugify(name)
            if venue_id in existing_ids:
                continue
            new_venues.append(
                {
                    "id": venue_id,
                    "name": name,
                    "kind": "kultur",
                    "venue_type": venue_type,
                    "area": None,
                    "address": p.get("formattedAddress"),
                    "rating": p.get("rating"),
                    "reviewCount": p.get("userRatingCount"),
                    "photos": [],
                    # Google'in kendi place id'si - fetch_google_places_photos.py
                    # bunu dogrudan Place Details ile cekip isim-benzerligi
                    # (dil farkindan dolayi hatali reddedilebilen) eslestirmesini
                    # atlayabilsin diye saklanir.
                    "google_place_id": p.get("id"),
                }
            )
            existing_ids.add(venue_id)
            seen_names.append(normalize(name))

    print(f"Yeni mekan: {len(new_venues)}")
    print(f"Atlanan (muhtemel tekrar): {skipped_duplicate}")
    print(f"Atlanan (guvenilir tur yok / belirsiz): {skipped_no_type}")

    all_venues = existing_kultur + new_venues
    with open(kultur_path, "w", encoding="utf-8") as f:
        json.dump(all_venues, f, ensure_ascii=False, indent=2)
    print(f"Yazildi: {kultur_path} ({len(all_venues)} toplam mekan)")


if __name__ == "__main__":
    main()
