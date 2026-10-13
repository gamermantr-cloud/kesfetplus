"""End-to-end HTTP smoke test for the KesfetPlus backend.

Hits the real, running FastAPI server (no mocking, no in-process TestClient)
to exercise the parts of the app that currently have little/no automated
test coverage, the way an actual frontend request would:

- Auth: register / login (wrong + correct password) / token-less request
  rejection.
- Check-in / status / comment posting + the trust-scoring pipeline
  (`database/trust_scoring.py`), including a regression check that
  duplicate text is actually detected and scored lower. All of these now
  require a real logged-in account (App Store Guideline 1.2), so this
  script authenticates first and posts with a real Bearer token - it no
  longer sends a free-text "author" field.
- Content filtering (`database/content_filter.py`): a comment containing a
  known objectionable term is forced to review_status="hidden".
- Reporting + blocking (`database/reports_store.py`, `database/users_store.py`):
  one test user reports and blocks a second test user, and the blocker's
  `GET /places/{id}/comments` view is verified to actually exclude (and,
  after unblocking, re-include) the blocked user's content server-side.
- Photo comparison (`database/photo_compare.py`): re-uploading a venue's
  own reference photo scores a high/"muhtemelen_ayni_yer" similarity, and
  uploading an unrelated synthetic image does not.

Deliberately NOT covered here: any moderator/admin moderation panel
endpoints (e.g. gated by a `MODERATOR_EMAILS`-style mechanism). That is a
separate, independently-evolving feature area and this script must not
depend on it.

Usage:
    venv\\Scripts\\python.exe .claude\\skills\\kesfetplus-smoke-test\\scripts\\smoke_test.py

Requires the backend to already be running (see kesfetplus-dev skill).
Exit code 0 = all checks passed, 1 = at least one failed (or backend down).

Set SKIP_PHOTO_COMPARE=1 to skip the photo-comparison scenario (section 8
below, plus the reference-photo lookup that only feeds it). That scenario
makes real network calls to Wikimedia Commons and is rate-limit-flaky by
nature - used by CI, which shouldn't fail a run over external flakiness
unrelated to this codebase. Local/manual runs should leave it unset so the
scenario still gets exercised.

Cleanup: every account/comment/check-in/status/report this script creates
is tagged with a throwaway `SMOKE-TEST-<run id>` marker (in display_name,
and therefore in the `author` field written by comments/checkins/status),
so cleanup can find and remove *only* the rows this run created - see
`cleanup_and_verify`.

Storage note: the backend is PostgreSQL-backed now (database/schema.sql,
database/*_store.py) rather than JSON files - this script talks to the
same database the running backend uses (DATABASE_URL must be set, same as
the backend) to verify cleanup, via database/db.get_cursor(), instead of
reading/writing database/*.json directly like it used to (see git history
for that version).
"""

from __future__ import annotations

import io
import json
import os
import sys
import uuid

import requests
from PIL import Image

# --- Make `database.*` importable regardless of cwd -----------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from database.checkins_store import STATUS_TAGS  # noqa: E402
from database.db import get_cursor  # noqa: E402
from database.photo_compare import get_reference_photo_url  # noqa: E402
from database.trust_scoring import TEXT_SIMILARITY_THRESHOLD  # noqa: E402

# Configurable so this can be pointed at a one-off test server (e.g. a
# second uvicorn instance on another port, running against a scratch
# database) without editing this file - defaults to the normal dev setup.
BASE_URL = os.getenv("SMOKE_TEST_BASE_URL", "http://127.0.0.1:8000")
SEED_DIR = os.path.join(_REPO_ROOT, "database", "seed")
PLACES_SEED_PATH = os.path.join(SEED_DIR, "places.json")

RUN_ID = uuid.uuid4().hex[:8]
TEST_AUTHOR = f"SMOKE-TEST-{RUN_ID}"  # kept for the pre-existing author-prefix cleanup pattern

USER_A_DISPLAY = f"{TEST_AUTHOR}-A"
USER_A_EMAIL = f"smoke-test-{RUN_ID}-a@example.test"
USER_A_PASSWORD = "SmokeTest1234!"  # noqa: S105 - throwaway test-account password, not a secret

USER_B_DISPLAY = f"{TEST_AUTHOR}-B"
USER_B_EMAIL = f"smoke-test-{RUN_ID}-b@example.test"
USER_B_PASSWORD = "SmokeTest5678!"  # noqa: S105 - throwaway test-account password, not a secret

VALID_REVIEW_STATUSES = {"visible", "pending_review", "hidden"}

# See module docstring: skips the Wikimedia-dependent photo-compare scenario
# (and its reference-photo lookup) when set - CI sets this, manual runs don't.
SKIP_PHOTO_COMPARE = os.getenv("SKIP_PHOTO_COMPARE", "") == "1"

# One entry from database/content_filter.py's own word list - used only to
# exercise the filter's end-to-end *behavior* (never copied/reproduced as a
# list here, see that module's docstring on why the list itself isn't meant
# to be duplicated around the codebase).
OBJECTIONABLE_TEST_WORD = "amk"

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


def load_place_with_reference_photo() -> tuple[str, str]:
    """A real place_id that has a reference photo, found by scanning the
    seed files (same files photo_compare.get_reference_photo_url reads)
    and asking that same public function for its photo URL - never a
    made-up id or URL."""
    print("\n2b. Referans fotografi olan gercek bir mekan araniyor (seed dosyalari)")
    for filename in ("places.json", "gurme.json", "hotels.json"):
        path = os.path.join(SEED_DIR, filename)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            venues = json.load(f)
        for venue in venues:
            place_id = venue.get("id")
            if not place_id:
                continue
            url = get_reference_photo_url(place_id)
            if url:
                print(
                    f"  place_id = {place_id!r} (name: {venue.get('name')!r}), photo_url = {url!r}"
                )
                return place_id, url
    fatal("Referans fotografi olan hicbir mekan bulunamadi (places/gurme/hotels.json).")
    raise AssertionError("unreachable")  # for type-checkers; fatal() always exits


def run_auth_tests(place_id: str) -> tuple[str | None, dict, str | None, dict]:
    """Register two throwaway accounts (A, B) and exercise register/login/
    token-less-request rejection. Returns (token_a, user_a, token_b, user_b)
    - any of these can be None/{} if a step failed, callers must guard."""
    print(f"\n3. Auth: kayit / login / token dogrulama (run={RUN_ID})")

    # 3a. Register user A -> 201, with a usable token + user back
    r = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": USER_A_EMAIL, "password": USER_A_PASSWORD, "display_name": USER_A_DISPLAY},
        timeout=5,
    )
    check("POST /auth/register (A) -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    body_a = r.json() if r.status_code == 201 else {}
    token_a = body_a.get("token")
    user_a = body_a.get("user") or {}
    check(
        "register (A) response has token + user.id",
        bool(token_a) and bool(user_a.get("id")),
        f"got {body_a!r}",
    )

    # 3b. Register user B -> 201 (needed for the block/report scenario below)
    r = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": USER_B_EMAIL, "password": USER_B_PASSWORD, "display_name": USER_B_DISPLAY},
        timeout=5,
    )
    check("POST /auth/register (B) -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    body_b = r.json() if r.status_code == 201 else {}
    token_b = body_b.get("token")
    user_b = body_b.get("user") or {}
    check(
        "register (B) response has token + user.id",
        bool(token_b) and bool(user_b.get("id")),
        f"got {body_b!r}",
    )

    # 3c. Login with the wrong password -> 401
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": USER_A_EMAIL, "password": USER_A_PASSWORD + "-wrong"},
        timeout=5,
    )
    check(
        "POST /auth/login (yanlis sifre) -> 401",
        r.status_code == 401,
        f"got {r.status_code}: {r.text}",
    )

    # 3d. Login with the correct password -> 200 + a usable token
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": USER_A_EMAIL, "password": USER_A_PASSWORD},
        timeout=5,
    )
    check(
        "POST /auth/login (dogru sifre) -> 200",
        r.status_code == 200,
        f"got {r.status_code}: {r.text}",
    )
    login_token_a = r.json().get("token") if r.status_code == 200 else None
    check("login (dogru sifre) token doner", bool(login_token_a), f"got {r.text}")

    # 3e. Token-less content POST -> 401 (posting now requires a real account)
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/comments",
        json={"text": "token'siz istek - 401 bekleniyor"},
        timeout=5,
    )
    check(
        "POST /comments (token'siz) -> 401",
        r.status_code == 401,
        f"got {r.status_code}: {r.text}",
    )

    return token_a, user_a, token_b, user_b


def run_content_tests(place_id: str, token_a: str | None) -> None:
    """Checkin / status / comment posting + trust-scoring, as user A."""
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"\n4. Uctan uca istekler (user A = {USER_A_DISPLAY!r})")

    # Baseline count *before* we post our checkin, so 4b can compare a real
    # before/after delta instead of just asserting ">= 1".
    r = requests.get(f"{BASE_URL}/places/{place_id}/checkin-count", timeout=5)
    count_before = r.json().get("count") if r.status_code == 200 else None

    # 4a. POST checkin (no location), authenticated as A
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/checkins",
        json={},
        headers=headers_a,
        timeout=5,
    )
    check("POST /checkins -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    body = r.json() if r.status_code == 201 else {}
    check(
        "checkin.location_verified is bool",
        isinstance(body.get("location_verified"), bool),
        f"got {body.get('location_verified')!r}",
    )

    # 4b. GET checkin-count increased vs. the count taken before our POST
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

    # 4c. POST status with a real STATUS_TAGS value, authenticated as A
    valid_tag = STATUS_TAGS[0]
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/status",
        json={"tag": valid_tag, "text": "smoke test"},
        headers=headers_a,
        timeout=5,
    )
    check("POST /status (valid tag) -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    posted_status_id = r.json().get("id") if r.status_code == 201 else None

    # 4d. GET status -> our entry is_stale == False
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

    # 4e. POST comment -> trust score in range, review_status valid
    comment_text = f"Smoke test yorumu {uuid.uuid4().hex}"
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/comments",
        json={"text": comment_text},
        headers=headers_a,
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

    # 4f. Regression: same author+text again -> duplicate text detection
    # should drop the trust score (TEXT_SIMILARITY_THRESHOLD from
    # trust_scoring.py: SequenceMatcher ratio > threshold => 0 pts for the
    # text-similarity signal instead of TEXT_SIGNAL_MAX).
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/comments",
        json={"text": comment_text},
        headers=headers_a,
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

    # 4g. Invalid tag -> 422
    print("\n5. Validasyon: gecersiz tag")
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/status",
        json={"tag": "NOT-A-REAL-TAG", "text": ""},
        headers=headers_a,
        timeout=5,
    )
    check(
        "POST /status (invalid tag) -> 422",
        r.status_code == 422,
        f"got {r.status_code}: {r.text}",
    )


def run_content_filter_test(place_id: str, token_a: str | None) -> None:
    """A comment containing a known objectionable term must be forced to
    review_status="hidden" / flagged_reason="objectionable_content",
    regardless of what its trust score would otherwise have been."""
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("\n6. Icerik filtreleme (database/content_filter.py)")

    comment_text = f"Bu yer {OBJECTIONABLE_TEST_WORD} gercekten berbat {uuid.uuid4().hex}"
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/comments",
        json={"text": comment_text},
        headers=headers_a,
        timeout=5,
    )
    check(
        "POST /comments (uygunsuz kelime iceren) -> 201",
        r.status_code == 201,
        f"got {r.status_code}: {r.text}",
    )
    body = r.json() if r.status_code == 201 else {}
    check(
        'objectionable comment -> review_status == "hidden"',
        body.get("review_status") == "hidden",
        f"got {body.get('review_status')!r}",
    )
    check(
        'objectionable comment -> flagged_reason == "objectionable_content"',
        body.get("flagged_reason") == "objectionable_content",
        f"got {body.get('flagged_reason')!r}",
    )


def run_block_and_report_tests(
    place_id: str, token_a: str | None, user_a: dict, token_b: str | None, user_b: dict
) -> None:
    """A (reporter/blocker) reports and blocks B (reported/blocked)'s
    comment, verifying the block actually filters B's content out of A's
    server-side GET /comments view, and back in again after unblocking."""
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print("\n7. Sikayet / Engelleme")

    # B posts a comment (unique text, well above the trust threshold so it's
    # actually visible in the normal listing before any blocking happens).
    b_comment_text = f"B kullanicisinin yorumu {uuid.uuid4().hex}"
    r = requests.post(
        f"{BASE_URL}/places/{place_id}/comments",
        json={"text": b_comment_text},
        headers=headers_b,
        timeout=5,
    )
    check("POST /comments (user B) -> 201", r.status_code == 201, f"got {r.status_code}: {r.text}")
    b_comment = r.json() if r.status_code == 201 else {}
    b_comment_id = b_comment.get("id")

    # A reports B's comment.
    r = requests.post(
        f"{BASE_URL}/reports",
        json={
            "target_type": "comment",
            "target_id": b_comment_id or "missing",
            "place_id": place_id,
            "reason": f"SMOKE-TEST sikayet {uuid.uuid4().hex}",
        },
        headers=headers_a,
        timeout=5,
    )
    check(
        "POST /reports (A, B'nin yorumunu sikayet eder) -> 201",
        r.status_code == 201,
        f"got {r.status_code}: {r.text}",
    )
    report_body = r.json() if r.status_code == 201 else {}

    r = requests.get(f"{BASE_URL}/reports", headers=headers_a, timeout=5)
    reports_list = r.json() if r.status_code == 200 else []
    check(
        "GET /reports (A) filed report'u iceriyor",
        r.status_code == 200
        and any(rep.get("id") == report_body.get("id") for rep in reports_list),
        f"status={r.status_code} report_id={report_body.get('id')!r}",
    )

    # A blocks B.
    r = requests.post(f"{BASE_URL}/users/{user_b.get('id')}/block", headers=headers_a, timeout=5)
    check("POST /users/{B}/block -> 200", r.status_code == 200, f"got {r.status_code}: {r.text}")
    blocked_ids = r.json().get("blocked_user_ids") if r.status_code == 200 else []
    check(
        "block sonrasi blocked_user_ids B'yi iceriyor",
        user_b.get("id") in (blocked_ids or []),
        f"got {blocked_ids!r}",
    )

    # GET comments as A (blocked) -> B's comment must not be served at all.
    r = requests.get(f"{BASE_URL}/places/{place_id}/comments", headers=headers_a, timeout=5)
    comments = r.json() if r.status_code == 200 else []
    check(
        "GET /comments (A, B engelliyken) B'nin yorumunu ARTIK icermiyor",
        r.status_code == 200 and not any(c.get("id") == b_comment_id for c in comments),
        f"status={r.status_code} b_comment_id={b_comment_id!r}",
    )

    # A unblocks B.
    r = requests.post(f"{BASE_URL}/users/{user_b.get('id')}/unblock", headers=headers_a, timeout=5)
    check("POST /users/{B}/unblock -> 200", r.status_code == 200, f"got {r.status_code}: {r.text}")
    blocked_ids_after = r.json().get("blocked_user_ids") if r.status_code == 200 else None
    check(
        "unblock sonrasi blocked_user_ids B'yi ARTIK icermiyor",
        blocked_ids_after is not None and user_b.get("id") not in blocked_ids_after,
        f"got {blocked_ids_after!r}",
    )

    # GET comments as A (unblocked) -> B's comment visible again.
    r = requests.get(f"{BASE_URL}/places/{place_id}/comments", headers=headers_a, timeout=5)
    comments = r.json() if r.status_code == 200 else []
    check(
        "GET /comments (A, unblock sonrasi) B'nin yorumunu TEKRAR iceriyor",
        r.status_code == 200 and any(c.get("id") == b_comment_id for c in comments),
        f"status={r.status_code} b_comment_id={b_comment_id!r}",
    )


def _guess_content_type(url: str) -> str:
    lower = url.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def _make_unrelated_image_bytes() -> bytes:
    """A small, fully deterministic synthetic checkerboard PNG - not a photo
    of anything, and about as visually unlike a real building/venue photo
    as a deterministic (no PRNG-seed footgun) image gets. Used for the
    "clearly not the same place" compare-photo case."""
    size, block = 64, 8
    img = Image.new("RGB", (size, size))
    pixels = img.load()
    for x in range(size):
        for y in range(size):
            is_white = ((x // block) + (y // block)) % 2 == 0
            pixels[x, y] = (255, 255, 255) if is_white else (0, 0, 0)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def run_photo_compare_tests(photo_place_id: str, photo_url: str, token_a: str | None) -> None:
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"\n8. Foto karsilastirma (place_id={photo_place_id!r})")

    # Download the venue's real reference photo so we can re-upload the
    # exact same bytes - same User-Agent requirement Wikimedia Commons
    # enforces (see database/photo_compare.py's _DOWNLOAD_HEADERS docstring).
    r = requests.get(
        photo_url,
        headers={"User-Agent": "KesfetPlusSmokeTest/1.0 (smoke test; contact via repo)"},
        timeout=15,
    )
    check("GET referans fotograf (indirme) -> 200", r.status_code == 200, f"got {r.status_code}")
    reference_bytes = r.content if r.status_code == 200 else b""

    # High-similarity case: re-upload the reference photo itself.
    files = {"photo": ("reference.jpg", reference_bytes, _guess_content_type(photo_url))}
    r = requests.post(
        f"{BASE_URL}/places/{photo_place_id}/compare-photo",
        files=files,
        headers=headers_a,
        timeout=20,
    )
    check(
        "POST /compare-photo (referansin kendisi) -> 200",
        r.status_code == 200,
        f"got {r.status_code}: {r.text}",
    )
    same_body = r.json() if r.status_code == 200 else {}
    check(
        'ayni gorsel -> verdict == "muhtemelen_ayni_yer" ve yuksek benzerlik',
        same_body.get("verdict") == "muhtemelen_ayni_yer"
        and isinstance(same_body.get("similarity_percent"), int | float)
        and same_body["similarity_percent"] > 75,
        f"got {same_body!r}",
    )

    # Low/ambiguous-similarity case: an unrelated synthetic image.
    files = {"photo": ("unrelated.png", _make_unrelated_image_bytes(), "image/png")}
    r = requests.post(
        f"{BASE_URL}/places/{photo_place_id}/compare-photo",
        files=files,
        headers=headers_a,
        timeout=20,
    )
    check(
        "POST /compare-photo (alakasiz gorsel) -> 200",
        r.status_code == 200,
        f"got {r.status_code}: {r.text}",
    )
    diff_body = r.json() if r.status_code == 200 else {}
    check(
        'alakasiz gorsel -> verdict "muhtemelen_ayni_yer" DEGIL (dusuk/belirsiz benzerlik)',
        diff_body.get("verdict") in ("belirsiz", "farkli_gorunuyor"),
        f"got {diff_body!r}",
    )


def _table_count(table: str) -> int:
    with get_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS n FROM {table}")  # noqa: S608 - table from a fixed list below
        row = cur.fetchone()
    return row["n"] if row else 0


def _snapshot_counts() -> dict[str, int]:
    """Row count per table this run might touch, taken *before* any smoke
    activity - the baseline cleanup must return to."""
    return {table: _table_count(table) for table in _TOUCHED_TABLES}


_TOUCHED_TABLES = ("comments", "checkins", "status_updates", "users", "sessions", "reports")


def _clean_author_keyed_table(label: str, table: str) -> int:
    """comments / checkins / status_updates: removes only rows whose
    `author` starts with the SMOKE-TEST- marker."""
    with get_cursor() as cur:
        cur.execute(f"DELETE FROM {table} WHERE author LIKE 'SMOKE-TEST-%'")  # noqa: S608
        removed = cur.rowcount
    print(f"  {label}: {removed} smoke kaydı silindi.")
    return removed


def _clean_users_and_sessions(test_user_ids: set[str]) -> None:
    """Removes exactly the accounts (and their sessions) this run created,
    matched by id - never by a string prefix - so a real account can never
    be swept up by accident."""
    if not test_user_ids:
        print("  users/sessions: silinecek smoke hesabı yok.")
        return
    ids = list(test_user_ids)
    with get_cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE user_id = ANY(%s)", (ids,))
        sessions_removed = cur.rowcount
        cur.execute("DELETE FROM users WHERE id = ANY(%s)", (ids,))
        users_removed = cur.rowcount
    print(f"  sessions: {sessions_removed} smoke session silindi.")
    print(f"  users: {users_removed} smoke hesabı silindi.")


def cleanup_and_verify(before_counts: dict[str, int], test_user_ids: set[str]) -> bool:
    """Remove every row this run created, then assert each touched table's
    row count is back to its pre-test baseline - cleanup is exact, not
    "close enough". (reports/comments/checkins/status rows created by a
    test user are removed by the ON DELETE CASCADE on users.id - see
    database/schema.sql - once _clean_users_and_sessions deletes the user
    row; comments/checkins/status_updates are *also* swept directly by
    author-prefix in case a row was posted before its author's account id
    was known to this script, e.g. nothing today, but keeps this robust.)
    """
    print("\n9. Temizlik (sadece bu run'in SMOKE-TEST- kayitlari)")
    _clean_author_keyed_table("comments", "comments")
    _clean_author_keyed_table("checkins", "checkins")
    _clean_author_keyed_table("status_updates", "status_updates")
    _clean_users_and_sessions(test_user_ids)

    all_clean = True
    after_counts = {table: _table_count(table) for table in _TOUCHED_TABLES}
    for table in _TOUCHED_TABLES:
        restored = after_counts[table] == before_counts[table]
        all_clean &= restored
        check(
            f"{table}: temizlik sonrası satır sayısı test-öncesi hale eşit",
            restored,
            f"before={before_counts[table]} after={after_counts[table]}",
        )
    return all_clean


def main() -> int:
    print(f"=== KesfetPlus smoke test ({BASE_URL}) ===\n")

    require_backend_up()
    place_id = load_real_place_id()
    if SKIP_PHOTO_COMPARE:
        photo_place_id, photo_url = None, None
        print("\n2b. Referans fotografi olan mekan araniyor... ATLANDI (SKIP_PHOTO_COMPARE=1)")
    else:
        photo_place_id, photo_url = load_place_with_reference_photo()

    before_counts = _snapshot_counts()

    user_a: dict = {}
    user_b: dict = {}
    try:
        token_a, user_a, token_b, user_b = run_auth_tests(place_id)
        run_content_tests(place_id, token_a)
        run_content_filter_test(place_id, token_a)
        run_block_and_report_tests(place_id, token_a, user_a, token_b, user_b)
        if SKIP_PHOTO_COMPARE:
            print(
                "\n8. Foto karsilastirma ATLANDI (SKIP_PHOTO_COMPARE=1 - "
                "Wikimedia Commons'a bagimli/flaky, bu calistirmada disarida "
                "birakildi)"
            )
        else:
            run_photo_compare_tests(photo_place_id, photo_url, token_a)
    finally:
        test_user_ids = {uid for uid in (user_a.get("id"), user_b.get("id")) if uid}
        cleanup_and_verify(before_counts, test_user_ids)

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
