"""End-to-end HTTP smoke test for the KesfetPlus backend.

Hits the real, running FastAPI server (no mocking, no in-process TestClient)
to exercise the checkin / status / trust-scoring endpoints the way an actual
frontend request would. There is currently no automated test coverage for
these systems at all, so this is deliberately a black-box HTTP test against
`http://127.0.0.1:8000`.

Usage:
    venv\\Scripts\\python.exe .claude\\skills\\kesfetplus-smoke-test\\scripts\\smoke_test.py

Requires the backend to already be running (see kesfetplus-dev skill).
Exit code 0 = all checks passed, 1 = at least one failed (or backend down).

Cleanup: every request this script makes uses a throwaway author prefixed
with "SMOKE-TEST-" (see `TEST_AUTHOR`), so cleanup can find and remove
*only* the rows this run created from the JSON stores, byte-for-byte
restoring everything else.
"""

from __future__ import annotations

import json
import os
import sys
import uuid

import requests

# --- Make `database.*` importable regardless of cwd -----------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from database.checkins_store import STATUS_TAGS  # noqa: E402
from database.trust_scoring import TEXT_SIMILARITY_THRESHOLD  # noqa: E402

BASE_URL = "http://127.0.0.1:8000"
PLACES_SEED_PATH = os.path.join(_REPO_ROOT, "database", "seed", "places.json")

COMMENTS_PATH = os.path.join(_REPO_ROOT, "database", "comments.json")
CHECKINS_PATH = os.path.join(_REPO_ROOT, "database", "checkins.json")
STATUS_PATH = os.path.join(_REPO_ROOT, "database", "status.json")

TEST_AUTHOR = f"SMOKE-TEST-{uuid.uuid4().hex[:8]}"
VALID_REVIEW_STATUSES = {"visible", "pending_review", "hidden"}

_results: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> bool:
    _results.append((name, condition, detail))
    mark = "PASS" if condition else "FAIL"
    suffix = f" - {detail}" if detail and not condition else ""
    print(f"  [{mark}] {name}{suffix}")
    return condition


def fatal(message: str) -> None:
    print(f"\nHATA: {message}")
    print("\nToplam: 0 gecti, 0 basarisiz (test hic baslamadi)")
    sys.exit(1)


def require_backend_up() -> None:
    print("1. Backend saglik kontrolu")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.RequestException as exc:
        fatal(
            f"Backend {BASE_URL} calismiyor ({exc.__class__.__name__}: {exc}). "
            "Once 'kesfetplus-dev' skill'i ile backend'i baslat."
        )
        return  # unreachable, fatal() exits
    if r.status_code != 200:
        fatal(
            f"Backend /health -> HTTP {r.status_code} (200 bekleniyordu). Backend saglikli degil."
        )
    print(f"  [PASS] GET /health -> 200 {r.json()}")


def load_real_place_id() -> str:
    print("\n2. Gercek place_id okunuyor (database/seed/places.json)")
    if not os.path.exists(PLACES_SEED_PATH):
        fatal(f"{PLACES_SEED_PATH} bulunamadi.")
    with open(PLACES_SEED_PATH, encoding="utf-8") as f:
        places = json.load(f)
    if not places:
        fatal("places.json bos, test edilecek gercek bir place_id yok.")
    place_id = places[0]["id"]
    print(f"  place_id = {place_id!r} (name: {places[0].get('name')!r})")
    return place_id


def run_tests(place_id: str) -> None:
    print(f"\n3. Uctan uca istekler (author={TEST_AUTHOR})")

    # Baseline count *before* we post our checkin, so 3b can compare a real
    # before/after delta instead of just asserting ">= 1".
    r = requests.get(f"{BASE_URL}/places/{place_id}/checkin-count", timeout=5)
    count_before = r.json().get("count") if r.status_code == 200 else None

    # 3a. POST checkin (no location)
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/checkins",
        json={"author": TEST_AUTHOR},
        timeout=5,
    )
    check("POST /checkins -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    body = r.json() if r.status_code == 201 else {}
    check(
        "checkin.location_verified is bool",
        isinstance(body.get("location_verified"), bool),
        f"got {body.get('location_verified')!r}",
    )

    # 3b. GET checkin-count increased vs. the count taken before our POST
    r = requests.get(f"{BASE_URL}/places/{place_id}/checkin-count", timeout=5)
    count_after = r.json().get("count") if r.status_code == 200 else None
    check(
        "GET /checkin-count -> 200, count increased after our checkin",
        r.status_code == 200
        and isinstance(count_after, int)
        and isinstance(count_before, int)
        and count_after > count_before,
        f"status={r.status_code} before={count_before} after={count_after}",
    )

    # 3c. POST status with a real STATUS_TAGS value
    valid_tag = STATUS_TAGS[0]
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/status",
        json={"author": TEST_AUTHOR, "tag": valid_tag, "text": "smoke test"},
        timeout=5,
    )
    check("POST /status (valid tag) -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    posted_status_id = r.json().get("id") if r.status_code == 201 else None

    # 3d. GET status -> our entry is_stale == False
    r = requests.get(f"{BASE_URL}/places/{place_id}/status", timeout=5)
    ok = r.status_code == 200
    entry = None
    if ok:
        entry = next((s for s in r.json() if s.get("id") == posted_status_id), None)
    check(
        "GET /status -> new entry present with is_stale == False",
        ok and entry is not None and entry.get("is_stale") is False,
        f"status={r.status_code} entry={entry}",
    )

    # 3e. POST comment -> trust score in range, review_status valid
    comment_text = f"Smoke test yorumu {uuid.uuid4().hex}"
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/comments",
        json={"author": TEST_AUTHOR, "text": comment_text},
        timeout=5,
    )
    check("POST /comments (1st) -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    first = r.json() if r.status_code == 201 else {}
    first_score = first.get("computed_trust_score")
    check(
        "computed_trust_score in [0, 100]",
        isinstance(first_score, int | float) and 0 <= first_score <= 100,
        f"got {first_score!r}",
    )
    check(
        "review_status in expected enum",
        first.get("review_status") in VALID_REVIEW_STATUSES,
        f"got {first.get('review_status')!r}",
    )

    # 3f. Regression: same author+text again -> duplicate text detection
    # should drop the trust score (TEXT_SIMILARITY_THRESHOLD from
    # trust_scoring.py: SequenceMatcher ratio > threshold => 0 pts for the
    # text-similarity signal instead of TEXT_SIGNAL_MAX).
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/comments",
        json={"author": TEST_AUTHOR, "text": comment_text},
        timeout=5,
    )
    check(
        "POST /comments (duplicate) -> 201",
        r.status_code == 201,
        f"got {r.status_code}: {r.text}",
    )
    second = r.json() if r.status_code == 201 else {}
    second_score = second.get("computed_trust_score")
    check(
        f"duplicate comment scores lower (similarity > {TEXT_SIMILARITY_THRESHOLD} threshold)",
        isinstance(second_score, int | float)
        and isinstance(first_score, int | float)
        and second_score < first_score,
        f"first={first_score!r} second={second_score!r}",
    )
    check(
        "duplicate comment flagged_reason mentions duplicate_text",
        "duplicate_text" in (second.get("flagged_reason") or ""),
        f"got {second.get('flagged_reason')!r}",
    )

    # 4. Invalid tag -> 422
    print("\n4. Validasyon: gecersiz tag")
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/status",
        json={"author": TEST_AUTHOR, "tag": "NOT-A-REAL-TAG", "text": ""},
        timeout=5,
    )
    check(
        "POST /status (invalid tag) -> 422",
        r.status_code == 422,
        f"got {r.status_code}: {r.text}",
    )


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cleanup_and_verify(before_snapshots: dict[str, dict]) -> bool:
    """Remove only rows authored by TEST_AUTHOR from the three JSON stores,
    then assert the resulting file is byte-for-byte identical (as parsed
    JSON) to the pre-test snapshot - i.e. cleanup is exact, not "close
    enough". Returns True if all three files were fully restored.
    """
    print("\n5. Temizlik (sadece SMOKE-TEST- kayitlari)")
    all_clean = True
    for label, path in (
        ("comments.json", COMMENTS_PATH),
        ("checkins.json", CHECKINS_PATH),
        ("status.json", STATUS_PATH),
    ):
        before = before_snapshots[label]
        current = _load_json(path)
        cleaned: dict = {}
        removed = 0
        for place_id, entries in current.items():
            kept = [e for e in entries if not str(e.get("author", "")).startswith("SMOKE-TEST-")]
            removed += len(entries) - len(kept)
            # Keep the key if it still has rows, or if it existed before
            # the test (even as an empty list) - i.e. never introduce a
            # place_id key that wasn't there before, and never drop one
            # that was.
            if kept or place_id in before:
                cleaned[place_id] = kept
        if os.path.exists(path) or cleaned:
            _save_json(path, cleaned)
        restored = cleaned == before
        check(f"{label}: {removed} smoke kaydi silindi, dosya test-oncesi hale esit", restored)
        all_clean = all_clean and restored
    return all_clean


def main() -> int:
    print(f"=== KesfetPlus smoke test ({BASE_URL}) ===\n")

    require_backend_up()
    place_id = load_real_place_id()

    before_snapshots = {
        "comments.json": _load_json(COMMENTS_PATH),
        "checkins.json": _load_json(CHECKINS_PATH),
        "status.json": _load_json(STATUS_PATH),
    }

    try:
        run_tests(place_id)
    finally:
        cleanup_and_verify(before_snapshots)

    passed = sum(1 for _, ok, _ in _results if ok)
    failed = sum(1 for _, ok, _ in _results if not ok)
    print(f"\n=== Sonuc: {passed} gecti, {failed} basarisiz ===")
    if failed:
        print("Basarisiz testler:")
        for name, ok, detail in _results:
            if not ok:
                print(f"  - {name}: {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
