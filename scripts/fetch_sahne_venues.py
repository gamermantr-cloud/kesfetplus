"""Konser/tiyatro/kulup mekanlarini Google Places'tan cekip
database/seed/sahne.json'a yazar.

Gercek Google Places Text Search (New) sonuclari - sahte/uydurma veri
yok. Mevcut places/gurme/hotels.json'da zaten olan bir mekan (isim
benzerligiyle) tekrar eklenmez. venue_type Google'in kendi `types`
alanindan turetilir - "movie_theater" (sinema) tipi tasiyan hicbir sonuc
alinmaz (kullanici kapsam disi birakti). Hicbir alan tahmin edilmez:
Google'in types'i net bir tur vermiyorsa venue_type None kalir.
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
    "concert halls in Istanbul",
    "performing arts theaters in Istanbul",
    "live music clubs in Istanbul",
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
    if "movie_theater" in types:
        return None  # sinema - kapsam disi, hicbir sekilde eklenmez
    if "performing_arts_theater" in types:
        return "tiyatro"
    if "concert_hall" in types or "opera_house" in types:
        return "konser_salonu"
    if "night_club" in types or "live_music_venue" in types:
        return "kulup"
    return None


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
    for f in ("places.json", "gurme.json", "hotels.json"):
        data = json.load(open(os.path.join(SEED_DIR, f), encoding="utf-8"))
        names.extend(normalize(v["name"]) for v in data)
    return names


def is_duplicate(name: str, existing: list[str]) -> bool:
    n = normalize(name)
    return any(SequenceMatcher(None, n, e).ratio() >= DUPLICATE_SIMILARITY_THRESHOLD for e in existing)


def main() -> None:
    existing_names = load_existing_names()
    sahne_path = os.path.join(SEED_DIR, "sahne.json")
    existing_sahne = []
    if os.path.exists(sahne_path):
        existing_sahne = json.load(open(sahne_path, encoding="utf-8"))
    existing_ids = {v["id"] for v in existing_sahne}
    seen_names = [normalize(v["name"]) for v in existing_sahne] + existing_names

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
                    "kind": "sahne",
                    "venue_type": venue_type,
                    "genre_tag": None,
                    "area": None,
                    "address": p.get("formattedAddress"),
                    "rating": p.get("rating"),
                    "reviewCount": p.get("userRatingCount"),
                    "photos": [],
                }
            )
            existing_ids.add(venue_id)
            seen_names.append(normalize(name))

    print(f"Yeni mekan: {len(new_venues)}")
    print(f"Atlanan (muhtemel tekrar): {skipped_duplicate}")
    print(f"Atlanan (guvenilir tur yok / sinema): {skipped_no_type}")

    all_venues = existing_sahne + new_venues
    with open(sahne_path, "w", encoding="utf-8") as f:
        json.dump(all_venues, f, ensure_ascii=False, indent=2)
    print(f"Yazildi: {sahne_path} ({len(all_venues)} toplam mekan)")


if __name__ == "__main__":
    main()
