"""Attach real Google Places photo metadata to seed entries missing photos.

Scope and intentional limitations (read before running):

1. This script NEVER downloads or stores any image/binary file. It only
   calls the Places API (New) Text Search endpoint
   (https://places.googleapis.com/v1/places:searchText) with a narrow
   field mask and copies a tiny bit of *metadata* about each matching
   photo into the seed JSON (`database/seed/places.json` / `gurme.json` /
   `hotels.json`).

2. `database/seed/*.json` is served to the browser as a static file via
   `frontend/public/data/*.json` (see CLAUDE.md). If a Google Photo Media
   URL with an embedded `?key=...` were ever written into that JSON, the
   API key would leak to every visitor and the project's quota could be
   drained by anyone who opens devtools. To avoid that, this script never
   writes a key-bearing URL anywhere. Each new photo entry only gets:
     - `place_id`      - the matched Google place id
     - `photo_name`    - Google's opaque photo resource name
                          ("places/<id>/photos/<ref>"), NOT a usable URL
     - `attribution`   - the photographer / "Google Places" attribution
                          text Google's Places API ToS requires showing
   The existing `url` and `source` fields are left as `null` placeholders
   on purpose. Actually resolving `photo_name` into a displayable image
   requires a *server-side* endpoint that calls the Place Photo (New)
   media endpoint with the key kept in a backend environment variable
   and streams/redirects the bytes to the client - that proxy endpoint is
   OUT OF SCOPE for this script (see CLAUDE.md's FastAPI app in
   `api/main.py`, which has no such route yet). Until that proxy exists,
   the frontend has no safe way to actually render these new photos.

3. Matching is fuzzy (Text Search returns a best-effort result, it does
   not guarantee the seed entry and the API result are the same place).
   Each result's `displayName` is compared against the seed `name` with
   stdlib `difflib.SequenceMatcher` (same technique already used in
   `database/trust_scoring.py`'s `_text_similarity_score`). Below the
   similarity threshold, the match is NOT applied automatically - it is
   recorded in a "needs review" file for a human to check by hand,
   consistent with CLAUDE.md's "sahte/uydurma veri yasak" rule (we would
   rather show nothing than silently attach the wrong place's photo).

4. Costs real Google API quota. A running counter + `--max-requests`
   (default 900, comfortably under the typical monthly free-tier Text
   Search allowance) makes the script stop itself mid-run rather than
   over-spend; progress is saved to `.places_photo_progress.json` so the
   next run resumes instead of re-querying places already handled.

Usage:
    venv\\Scripts\\python.exe scripts\\fetch_google_places_photos.py --dry-run
    venv\\Scripts\\python.exe scripts\\fetch_google_places_photos.py --limit 5
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = PROJECT_ROOT / "database" / "seed"
DEFAULT_PROGRESS_FILE = PROJECT_ROOT / "scripts" / ".places_photo_progress.json"
DEFAULT_NEEDS_REVIEW_FILE = PROJECT_ROOT / "scripts" / "needs_review.json"

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
# Narrow field mask on purpose: every extra field costs more and we only
# ever use these four.
FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.photos"
REQUEST_TIMEOUT_SECONDS = 10

DATASET_FILES = {
    "places": "places.json",
    "gurme": "gurme.json",
    "hotels": "hotels.json",
}

DEFAULT_SIMILARITY_THRESHOLD = 0.6
DEFAULT_MAX_REQUESTS = 900
DEFAULT_PHOTOS_PER_PLACE = 2
DEFAULT_REQUEST_DELAY_SECONDS = 0.2


@dataclass
class Candidate:
    dataset: str
    index: int
    entry: dict[str, Any]

    @property
    def key(self) -> str:
        return f"{self.dataset}:{self.entry.get('id')}"


@dataclass
class RunStats:
    requests_made: int = 0
    matched: int = 0
    needs_review: int = 0
    errors: int = 0
    per_dataset: dict[str, int] = field(default_factory=dict)


def needs_photos(entry: dict[str, Any]) -> bool:
    """True when the seed entry has no usable photo yet."""
    return not entry.get("photos")


def load_seed(dataset: str) -> list[dict[str, Any]]:
    path = SEED_DIR / DATASET_FILES[dataset]
    with open(path, encoding="utf-8") as f:
        data: list[dict[str, Any]] = json.load(f)
    return data


def save_seed(dataset: str, data: list[dict[str, Any]]) -> None:
    path = SEED_DIR / DATASET_FILES[dataset]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_json_if_exists(path: Path) -> Any:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_progress(path: Path) -> dict[str, Any]:
    data = load_json_if_exists(path)
    if not isinstance(data, dict):
        return {"processed": {}, "total_requests_lifetime": 0}
    data.setdefault("processed", {})
    data.setdefault("total_requests_lifetime", 0)
    return data


def build_query(entry: dict[str, Any]) -> str:
    name = entry.get("name", "")
    area = entry.get("area", "")
    return f"{name} {area}, İstanbul"


def name_similarity(seed_name: str, found_name: str) -> float:
    """Same technique as database/trust_scoring.py's _text_similarity_score:
    plain stdlib difflib.SequenceMatcher, no extra dependency."""
    if not seed_name or not found_name:
        return 0.0
    return SequenceMatcher(None, seed_name, found_name).ratio()


def text_search(session: requests.Session, api_key: str, query: str) -> dict[str, Any]:
    response = session.post(
        TEXT_SEARCH_URL,
        json={"textQuery": query, "languageCode": "tr"},
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    result: dict[str, Any] = response.json()
    return result


def build_attribution(photo: dict[str, Any]) -> str:
    authors = photo.get("authorAttributions") or []
    names = [a.get("displayName", "").strip() for a in authors if a.get("displayName")]
    names = [n for n in names if n]
    if names:
        return f"Fotoğraf: {', '.join(names)} — Google Places"
    return "Fotoğraf: Google Places kullanıcısı"


def build_photo_entries(
    place_id: str, photos: list[dict[str, Any]], max_photos: int
) -> list[dict[str, Any]]:
    entries = []
    for photo in photos[:max_photos]:
        photo_name = photo.get("name")
        if not photo_name:
            continue
        entries.append(
            {
                # Intentionally left as placeholders - see module docstring
                # point 2: filling these with a key-bearing Google Photo
                # Media URL would leak the API key through the public
                # static JSON. A backend proxy endpoint is needed first.
                "url": None,
                "source": None,
                "attribution": build_attribution(photo),
                "place_id": place_id,
                "photo_name": photo_name,
            }
        )
    return entries


def collect_candidates(
    datasets: dict[str, list[dict[str, Any]]], progress: dict[str, Any]
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for dataset in ("places", "gurme", "hotels"):
        for index, entry in enumerate(datasets[dataset]):
            if not needs_photos(entry):
                continue
            candidate = Candidate(dataset=dataset, index=index, entry=entry)
            if candidate.key in progress["processed"]:
                continue
            candidates.append(candidate)
    return candidates


def merge_needs_review(path: Path, new_rows: list[dict[str, Any]]) -> None:
    existing = load_json_if_exists(path)
    rows: list[dict[str, Any]] = existing if isinstance(existing, list) else []
    by_key = {(row.get("dataset"), row.get("id")): row for row in rows}
    for row in new_rows:
        by_key[(row.get("dataset"), row.get("id"))] = row
    save_json(path, list(by_key.values()))


def run(args: argparse.Namespace) -> int:
    progress_path = Path(args.progress_file)
    needs_review_path = Path(args.needs_review_file)
    progress = load_progress(progress_path)

    datasets: dict[str, list[dict[str, Any]]] = {
        dataset: load_seed(dataset) for dataset in DATASET_FILES
    }
    candidates = collect_candidates(datasets, progress)
    pending = candidates[: args.limit] if args.limit is not None else candidates

    per_dataset_pending: dict[str, int] = {}
    for c in candidates:
        per_dataset_pending[c.dataset] = per_dataset_pending.get(c.dataset, 0) + 1

    if args.dry_run:
        print("DRY RUN - hiçbir gerçek API çağrısı yapılmadı, hiçbir dosya değiştirilmedi.\n")
        print(
            f"Henüz fotoğrafı olmayan, önceki çalıştırmalarda işlenmemiş mekan sayısı: "
            f"{len(candidates)}"
        )
        for dataset, count in per_dataset_pending.items():
            print(f"  - {dataset}: {count}")
        to_process = len(pending)
        print(f"\nBu çalıştırmada (--limit={args.limit}) işlenecek mekan sayısı: {to_process}")
        print(
            f"Tahmini gerçek istek sayısı: {to_process} "
            "(mekan başına 1 Text Search isteği; Photo Media çağrısı yok çünkü "
            "hiçbir görsel indirilmiyor)"
        )
        print(f"--max-requests eşiği: {args.max_requests}")
        if to_process > args.max_requests:
            print(
                f"UYARI: istek sayısı eşiği aşıyor, script gerçek çalıştırmada "
                f"{args.max_requests}. istekte kendini durduracak."
            )
        return 0

    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print(
            "GOOGLE_PLACES_API_KEY .env içinde tanımlı değil - gerçek çağrı yapılamaz.",
            file=sys.stderr,
        )
        return 1

    session = requests.Session()
    stats = RunStats()
    touched_datasets: set[str] = set()
    needs_review_rows: list[dict[str, Any]] = []
    stopped_reason: str | None = None

    for candidate in pending:
        if stats.requests_made >= args.max_requests:
            stopped_reason = f"max-requests eşiğine ulaşıldı ({args.max_requests})"
            break

        seed_name = candidate.entry.get("name", "")
        query = build_query(candidate.entry)

        try:
            result = text_search(session, api_key, query)
            stats.requests_made += 1
        except requests.RequestException as exc:
            stats.requests_made += 1
            stats.errors += 1
            # Deliberately NOT marked in progress["processed"]: a request
            # error (invalid/expired key, network blip, rate limit, ...)
            # is often transient or fixable, unlike a real "no good match"
            # verdict. Leaving it out of "processed" means the next run
            # retries this candidate automatically instead of skipping it
            # forever.
            needs_review_rows.append(
                {
                    "dataset": candidate.dataset,
                    "id": candidate.entry.get("id"),
                    "seed_name": seed_name,
                    "found_name": None,
                    "similarity": 0.0,
                    "reason": f"request_error: {type(exc).__name__}",
                }
            )
            continue

        places = result.get("places") or []
        if not places:
            stats.needs_review += 1
            progress["processed"][candidate.key] = "needs_review"
            needs_review_rows.append(
                {
                    "dataset": candidate.dataset,
                    "id": candidate.entry.get("id"),
                    "seed_name": seed_name,
                    "found_name": None,
                    "similarity": 0.0,
                    "reason": "no_results",
                }
            )
            if args.request_delay:
                time.sleep(args.request_delay)
            continue

        top = places[0]
        found_name = top.get("displayName", {}).get("text", "")
        similarity = name_similarity(seed_name, found_name)

        if similarity < args.similarity_threshold:
            stats.needs_review += 1
            progress["processed"][candidate.key] = "needs_review"
            needs_review_rows.append(
                {
                    "dataset": candidate.dataset,
                    "id": candidate.entry.get("id"),
                    "seed_name": seed_name,
                    "found_name": found_name,
                    "similarity": round(similarity, 3),
                    "reason": "low_similarity",
                }
            )
            if args.request_delay:
                time.sleep(args.request_delay)
            continue

        place_id = top.get("id", "")
        photos = top.get("photos") or []
        photo_entries = build_photo_entries(place_id, photos, args.photos_per_place)

        if not photo_entries:
            stats.needs_review += 1
            progress["processed"][candidate.key] = "needs_review"
            needs_review_rows.append(
                {
                    "dataset": candidate.dataset,
                    "id": candidate.entry.get("id"),
                    "seed_name": seed_name,
                    "found_name": found_name,
                    "similarity": round(similarity, 3),
                    "reason": "matched_but_no_photos",
                }
            )
            if args.request_delay:
                time.sleep(args.request_delay)
            continue

        candidate.entry["photos"] = photo_entries
        touched_datasets.add(candidate.dataset)
        stats.matched += 1
        stats.per_dataset[candidate.dataset] = stats.per_dataset.get(candidate.dataset, 0) + 1
        progress["processed"][candidate.key] = "matched"

        if args.request_delay:
            time.sleep(args.request_delay)

    if not stopped_reason and len(pending) < len(candidates):
        stopped_reason = f"--limit {args.limit} tamamlandı"

    for dataset in touched_datasets:
        save_seed(dataset, datasets[dataset])

    progress["total_requests_lifetime"] = (
        progress.get("total_requests_lifetime", 0) + stats.requests_made
    )
    progress["last_run_at"] = datetime.now(UTC).isoformat()
    save_json(progress_path, progress)

    if needs_review_rows:
        merge_needs_review(needs_review_path, needs_review_rows)

    print(f"Bu çalıştırmada yapılan gerçek API isteği: {stats.requests_made}")
    print(f"Eşleşip fotoğraf eklenen mekan: {stats.matched}")
    print(f"needs_review'a giden mekan: {stats.needs_review}")
    print(f"Hata alınan mekan: {stats.errors}")
    if stopped_reason:
        print(f"Script erken durdu: {stopped_reason}")
    processed_count = stats.matched + stats.needs_review + stats.errors
    remaining = len(candidates) - processed_count
    print(f"Bir sonraki çalıştırmaya kalan işlenmemiş mekan sayısı: {remaining}")
    print(
        "\nHATIRLATMA: eklenen 'photos' kayıtlarında 'url' alanı bilerek boş (null) - "
        "Google Photo Media URL'sine key gömmek, statik JSON üzerinden public olarak "
        "sızdırır. Gerçek görüntüleme için api/main.py'ye key'i backend'de tutan bir "
        "proxy endpoint eklenmesi gerekiyor (bu script'in kapsamı dışında)."
    )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Google Places (New) Text Search ile seed mekanlarına gerçek fotoğraf "
            "metadata'sı (place_id/photo_name/attribution) ekler. Hiçbir görsel "
            "dosyası indirmez."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Gerçek API çağrısı yapma, sadece ne kadar iş olduğunu raporla.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Bu çalıştırmada en fazla N mekan işle (test için, ör. 5).",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=DEFAULT_MAX_REQUESTS,
        help=f"Bu çalıştırmada en fazla kaç gerçek API isteği yapılsın "
        f"(varsayılan {DEFAULT_MAX_REQUESTS}).",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=DEFAULT_SIMILARITY_THRESHOLD,
        help=f"Eşleşmeyi otomatik kabul etmek için gereken minimum benzerlik "
        f"(0-1 arası, varsayılan {DEFAULT_SIMILARITY_THRESHOLD}).",
    )
    parser.add_argument(
        "--photos-per-place",
        type=int,
        default=DEFAULT_PHOTOS_PER_PLACE,
        help=f"Mekan başına en fazla kaç foto metadata'sı alınsın "
        f"(varsayılan {DEFAULT_PHOTOS_PER_PLACE}).",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
        help="İstekler arası bekleme (saniye).",
    )
    parser.add_argument(
        "--progress-file",
        type=str,
        default=str(DEFAULT_PROGRESS_FILE),
        help="İlerleme dosyası yolu (nereden devam edileceğini tutar).",
    )
    parser.add_argument(
        "--needs-review-file",
        type=str,
        default=str(DEFAULT_NEEDS_REVIEW_FILE),
        help="Düşük benzerlikli/eşleşmeyen kayıtların yazıldığı dosya.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
