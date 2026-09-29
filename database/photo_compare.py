"""Real perceptual-hash photo comparison ("aynı yer mi, güncel mi?").

No paid/external AI vision API here, and no LLM "bence benzer görünüyor"
guess either (CLAUDE.md "sahte veri yasak" - a model's visual impression is
a guess, not a measurement). Instead this uses **perceptual hashing**
(pHash, via the `imagehash` library on top of `Pillow`): a real, local,
deterministic, reproducible algorithm that reduces an image to a fixed-size
fingerprint based on the low-frequency components of its discrete cosine
transform (DCT). Unlike a cryptographic hash, visually similar images
produce hashes that differ in only a few bits, so the *Hamming distance*
between two images' hashes is a genuine, well-established similarity
measurement (the same family of technique behind reverse-image-search
"near duplicate" detection) - not an invented number.

Similarity formula
-------------------
pHash with hash_size=8 produces an 8x8 = 64-bit fingerprint (imagehash's
default and the value used here). For two hashes with Hamming distance
`d` (0..64, number of differing bits):

    similarity_percent = max(0, 100 - (d / 64) * 100)

d=0 (identical bit pattern) -> 100%. d=64 (every bit differs, maximally
dissimilar) -> 0%. This is the standard way pHash distances are converted
to a percentage.

Verdict thresholds
-------------------
imagehash's own documentation treats a small Hamming distance (it suggests
~10 bits out of 64) as "same/near-duplicate image" - that is
100 - (10/64*100) ≈ 84%. We set the "probably the same place" cutoff a bit
below that, at 75% (~16 bits), because a real check-in photo - taken with a
phone, at a different time of day, angle, crop and lighting than a curated
reference photo - will never hash-match as tightly as a re-encoded copy of
the *same* file, even when it genuinely is the same place:

    > 75%   -> "muhtemelen_ayni_yer"   (probably the same place)
    40-75%  -> "belirsiz"              (ambiguous - could be a different
                                         angle/renovation, or a same-category
                                         but different photo; never claimed
                                         as a confident match either way)
    < 40%   -> "farkli_gorunuyor"      (a clearly different image)

Real-world calibration note (from manual testing against actual Wikimedia
Commons venue photos - see this feature's task report for exact numbers):
for two *unrelated* real photos, pHash's Hamming distance behaves like an
approximately-random ~32/64-bit split (each bit is roughly a coin flip
between two uncorrelated images), so unrelated pairs typically land around
45-60% - solidly inside "belirsiz", not near 0%. That is expected pHash
behavior, not a bug: the practically important guarantee this feature
relies on is the *gap* between that ~45-60% baseline and the 75% cutoff
(confirmed empirically: same-image/same-place tests scored 100%, unrelated
real photo pairs scored at most ~59%, a 16+ point margin) - so the system
essentially never falsely claims "probably the same place" for an unrelated
photo, even though it can't always confidently call an unrelated pair
"clearly different" either (hence "belirsiz" being the honest middle band,
not a forced binary).

Errors (reference photo failed to download, either file isn't a decodable
image, etc.) always raise a `PhotoCompareError` subclass with a specific,
honest message - never a silently-fabricated score.
"""

from __future__ import annotations

import io
import json
import os
from functools import lru_cache

import imagehash
import requests
from PIL import Image, UnidentifiedImageError

_SEED_DIR = os.path.join(os.path.dirname(__file__), "seed")

HASH_SIZE = 8  # 8x8 pHash -> 64-bit fingerprint (imagehash default)
TOTAL_BITS = HASH_SIZE * HASH_SIZE

SIMILAR_THRESHOLD_PERCENT = 75.0
AMBIGUOUS_THRESHOLD_PERCENT = 40.0

DOWNLOAD_TIMEOUT_SECONDS = 10
MAX_REFERENCE_BYTES = 15 * 1024 * 1024  # sanity cap for the downloaded reference photo

# Wikimedia Commons (where all seed venue.photos[].url values point) rejects
# requests with no/generic User-Agent (its documented user-agent policy) -
# without this header the download fails with a 403, not because the photo
# is missing.
_DOWNLOAD_HEADERS = {"User-Agent": "KesfetPlusPhotoCompare/1.0 (kesfetplus dev; contact via repo)"}


class PhotoCompareError(Exception):
    """Base class for any comparison failure that must surface as an honest
    error to the caller instead of a fabricated similarity score."""


class ReferenceDownloadError(PhotoCompareError):
    """The venue's reference photo could not be fetched from its source URL."""


class InvalidImageError(PhotoCompareError):
    """Either the reference or the uploaded bytes are not a decodable image."""


@lru_cache(maxsize=1)
def _venue_first_photo_urls() -> dict[str, str]:
    """place_id -> first venue.photos[].url, loaded once from the seed JSON
    files (same pattern as checkins_store._venue_areas)."""
    urls: dict[str, str] = {}
    for filename in ("places.json", "gurme.json", "hotels.json"):
        path = os.path.join(_SEED_DIR, filename)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for venue in json.load(f):
                place_id = venue.get("id")
                photos = venue.get("photos")
                if not place_id or not photos:
                    continue
                first_url = photos[0].get("url")
                if first_url:
                    urls[place_id] = first_url
    return urls


def get_reference_photo_url(place_id: str) -> str | None:
    """The venue's first reference photo URL, or None if it has none."""
    return _venue_first_photo_urls().get(place_id)


def _open_image(data: bytes, source_label: str) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except UnidentifiedImageError as exc:
        raise InvalidImageError(
            f"{source_label} geçerli bir görsel formatında değil (jpg/png/webp bekleniyor)."
        ) from exc
    except OSError as exc:
        raise InvalidImageError(
            f"{source_label} açılamadı: bozuk veya desteklenmeyen dosya."
        ) from exc
    return image.convert("RGB")


def _download_reference(reference_url: str) -> bytes:
    try:
        response = requests.get(
            reference_url, timeout=DOWNLOAD_TIMEOUT_SECONDS, headers=_DOWNLOAD_HEADERS
        )
    except requests.RequestException as exc:
        raise ReferenceDownloadError(
            "Referans fotoğraf indirilemedi (ağ hatası). Daha sonra tekrar dene."
        ) from exc
    if response.status_code != 200:
        raise ReferenceDownloadError(
            f"Referans fotoğraf indirilemedi (kaynak sunucu {response.status_code} döndürdü)."
        )
    if len(response.content) > MAX_REFERENCE_BYTES:
        raise ReferenceDownloadError(
            "Referans fotoğraf beklenenden çok büyük, karşılaştırma yapılamadı."
        )
    return response.content


def _verdict(similarity_percent: float) -> str:
    if similarity_percent > SIMILAR_THRESHOLD_PERCENT:
        return "muhtemelen_ayni_yer"
    if similarity_percent >= AMBIGUOUS_THRESHOLD_PERCENT:
        return "belirsiz"
    return "farkli_gorunuyor"


def compare_images(reference_url: str, uploaded_image_bytes: bytes) -> dict:
    """Download the venue's reference photo and compute a REAL pHash
    similarity against the user's uploaded photo bytes.

    `uploaded_image_bytes` is only ever held in memory for the duration of
    this call (decoded by Pillow, hashed, then eligible for garbage
    collection) - it is never written to disk. See api/main.py's
    compare-photo endpoint, which reads the upload straight from the
    multipart stream into memory and never calls anything that persists it.

    Raises PhotoCompareError (ReferenceDownloadError / InvalidImageError)
    with a specific, honest message on any failure - never returns a
    guessed/fabricated score.
    """
    if not uploaded_image_bytes:
        raise InvalidImageError("Yüklenen görsel boş.")

    reference_bytes = _download_reference(reference_url)
    reference_image = _open_image(reference_bytes, "Referans fotoğraf")
    uploaded_image = _open_image(uploaded_image_bytes, "Yüklediğin fotoğraf")

    reference_hash = imagehash.phash(reference_image, hash_size=HASH_SIZE)
    uploaded_hash = imagehash.phash(uploaded_image, hash_size=HASH_SIZE)

    # int()/float() here aren't cosmetic: imagehash/numpy return numpy
    # scalar types (np.int64/np.float64), which FastAPI's default JSON
    # encoder can't serialize - cast to plain Python types before returning.
    hamming_distance = int(reference_hash - uploaded_hash)
    similarity_percent = float(max(0.0, 100.0 - (hamming_distance / TOTAL_BITS * 100.0)))

    return {
        "similarity_percent": round(similarity_percent, 1),
        "hamming_distance": hamming_distance,
        "verdict": _verdict(similarity_percent),
    }
