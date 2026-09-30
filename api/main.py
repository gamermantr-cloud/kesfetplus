import os

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from database.checkins_store import (
    GOZCU_THRESHOLD,
    STATUS_TAGS,
    SelfHelpfulError,
    StatusError,
    add_checkin,
    add_status,
    count_all_checkins,
    count_all_status,
    count_recent_checkins,
    count_user_statuses,
    list_hidden_status,
    list_place_ids_with_activity,
    list_status,
    restore_status,
    toggle_helpful_status,
)
from database.comments_store import (
    CommentError,
    add_comment,
    count_all_comments,
    list_comments,
    list_hidden_comments,
    list_place_ids_with_comments,
    restore_comment,
    toggle_helpful_comment,
)
from database.comments_store import (
    SelfHelpfulError as CommentSelfHelpfulError,
)
from database.photo_compare import (
    InvalidImageError,
    PhotoCompareError,
    ReferenceDownloadError,
    compare_images,
    get_reference_photo_url,
)
from database.push_subscriptions_store import (
    add_subscription,
    remove_subscription,
)
from database.reports_store import (
    VALID_TARGET_TYPES,
    ReportError,
    add_report,
    list_all_reports,
    list_reports_by_user,
    resolve_report,
)
from database.users_store import (
    UserError,
    authenticate,
    count_users,
    create_session,
    delete_session,
    get_public_profile,
    get_user_by_token,
    register_user,
    set_blocked,
)

app = FastAPI(title="KesfetPlus")

# Dev-only: allow the Vite dev server from localhost and the local network
# (phone-on-same-wifi access). Not meant for a public deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):5173",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Rate limiting (IP-based) - /auth/register and /auth/login are the only
# endpoints that work without a token (they run *before* a user has one),
# so they're this app's real brute-force/spam-account attack surface. Every
# other endpoint already requires get_current_user, which register/login
# hands out. See per-route @limiter.limit(...) below for the actual values.
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Çok fazla deneme yapıldı. Lütfen bir süre bekleyip tekrar deneyin."},
    )


# ---------------------------------------------------------------------------
# Auth dependencies - opaque Bearer token, see database/users_store.py for
# why this isn't JWT.
# ---------------------------------------------------------------------------


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Required auth: raises 401 if no/invalid token. Use for any endpoint
    that must know a real, logged-in user (posting content, blocking,
    reporting)."""
    token = _extract_token(authorization)
    user = get_user_by_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Giriş gerekli.")
    return user


def get_current_user_optional(authorization: str | None = Header(default=None)) -> dict | None:
    """Optional auth: returns None instead of raising. Use for public GET
    endpoints that should still apply the caller's block-list when a token
    is present (comments/status listing)."""
    token = _extract_token(authorization)
    return get_user_by_token(token) if token else None


def get_current_moderator(user: dict = Depends(get_current_user)) -> dict:
    """Required auth + is_moderator check: raises 403 if the logged-in user
    isn't a moderator. See database/users_store.py "MODERATION MVP" note
    for how a user becomes a moderator (MODERATOR_EMAILS env var)."""
    if not user.get("is_moderator"):
        raise HTTPException(status_code=403, detail="Bu işlem için moderatör yetkisi gerekli.")
    return user


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=200)
    display_name: str = Field(min_length=1, max_length=80)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=200)


class ReportCreate(BaseModel):
    target_type: str
    target_id: str = Field(min_length=1, max_length=100)
    place_id: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=500)

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, value: str) -> str:
        if value not in VALID_TARGET_TYPES:
            raise ValueError(f"target_type must be one of {VALID_TARGET_TYPES}")
        return value


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    lat: float | None = None
    lng: float | None = None
    accuracy: float | None = None


class CheckinCreate(BaseModel):
    lat: float | None = None
    lng: float | None = None
    accuracy: float | None = None


class StatusCreate(BaseModel):
    tag: str
    text: str = Field(default="", max_length=280)

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, value: str) -> str:
        if value not in STATUS_TAGS:
            raise ValueError(f"tag must be one of {STATUS_TAGS}")
        return value


class PushSubscriptionKeys(BaseModel):
    p256dh: str = Field(min_length=1, max_length=500)
    auth: str = Field(min_length=1, max_length=500)


class PushSubscriptionCreate(BaseModel):
    """Mirrors the browser's PushSubscription.toJSON() shape exactly (see
    frontend/src/lib/push.js) - no reshaping on either side of the wire."""

    endpoint: str = Field(min_length=1, max_length=2000)
    keys: PushSubscriptionKeys


class PushUnsubscribeRequest(BaseModel):
    endpoint: str = Field(min_length=1, max_length=2000)


@app.get("/")
def read_root():
    return {"name": "KesfetPlus", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


@app.post("/auth/register", status_code=201)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterRequest):
    try:
        user = register_user(payload.email, payload.password, payload.display_name)
    except UserError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    token = create_session(user["id"])
    return {"token": token, "user": user}


@app.post("/auth/login")
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest):
    try:
        user = authenticate(payload.email, payload.password)
    except UserError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    token = create_session(user["id"])
    return {"token": token, "user": user}


@app.post("/auth/logout", status_code=204)
def logout(authorization: str | None = Header(default=None)):
    token = _extract_token(authorization)
    if token:
        delete_session(token)


@app.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return user


@app.get("/users/{user_id}")
def get_user_profile(user_id: str):
    """Public, minimal profile (id + display_name only) - used e.g. to show
    a name for an entry in the current user's blocked list."""
    profile = get_public_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return profile


@app.get("/users/{user_id}/stats")
def get_user_stats(user_id: str):
    """Real, on-demand computed stats for the "Teşvik Katmanı" (see
    docs/research/anlik-bilgi-akisi.md) - status_count is counted fresh
    from status.json every call (database/checkins_store.count_user_statuses),
    never stored, so it can't drift from reality. badges is ["gozcu"] once
    status_count reaches GOZCU_THRESHOLD, else []. Public (no auth) so
    PlaceDetail.jsx can show a "Gözcü" tag next to any author's post, not
    just the logged-in user's own profile."""
    profile = get_public_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    status_count = count_user_statuses(user_id)
    badges = ["gozcu"] if status_count >= GOZCU_THRESHOLD else []
    return {"status_count": status_count, "badges": badges, "gozcu_threshold": GOZCU_THRESHOLD}


# ---------------------------------------------------------------------------
# Blocking
# ---------------------------------------------------------------------------


@app.post("/users/{user_id}/block")
def block_user(user_id: str, user: dict = Depends(get_current_user)):
    try:
        blocked_user_ids = set_blocked(user["id"], user_id, blocked=True)
    except UserError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"blocked_user_ids": blocked_user_ids}


@app.post("/users/{user_id}/unblock")
def unblock_user(user_id: str, user: dict = Depends(get_current_user)):
    try:
        blocked_user_ids = set_blocked(user["id"], user_id, blocked=False)
    except UserError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"blocked_user_ids": blocked_user_ids}


# ---------------------------------------------------------------------------
# Reports - never auto-delete the reported content, see reports_store.py.
# ---------------------------------------------------------------------------


@app.post("/reports", status_code=201)
def create_report(payload: ReportCreate, user: dict = Depends(get_current_user)):
    return add_report(
        user["id"], payload.target_type, payload.target_id, payload.place_id, payload.reason
    )


@app.get("/reports")
def get_reports(user: dict = Depends(get_current_user)):
    """Minimal self-service listing: a logged-in user sees only the
    reports *they* filed, not everyone's. The moderator-only view of
    *everyone's* reports lives at GET /moderation/reports below."""
    return list_reports_by_user(user["id"])


# ---------------------------------------------------------------------------
# Comments / check-ins / status - posting now requires a real account
# (App Store Guideline 1.2 "real identity" requirement). Listing stays
# public but applies the caller's block-list server-side when a token is
# present.
# ---------------------------------------------------------------------------


@app.post("/places/{place_id}/comments", status_code=201)
def create_comment(place_id: str, comment: CommentCreate, user: dict = Depends(get_current_user)):
    return add_comment(
        place_id,
        user["display_name"],
        comment.text,
        comment.lat,
        comment.lng,
        comment.accuracy,
        user["id"],
    )


@app.get("/places/{place_id}/comments")
def get_comments(place_id: str, user: dict | None = Depends(get_current_user_optional)):
    exclude = set(user["blocked_user_ids"]) if user else None
    return list_comments(
        place_id, exclude_user_ids=exclude, viewer_user_id=user["id"] if user else None
    )


@app.post("/places/{place_id}/comments/{comment_id}/helpful")
def mark_comment_helpful(place_id: str, comment_id: str, user: dict = Depends(get_current_user)):
    """Toggle: first call marks helpful, a second call from the same user
    unmarks it (see database/comments_store.toggle_helpful_comment). Marking
    your own comment is refused with 400; an unknown comment_id is a 404."""
    try:
        return toggle_helpful_comment(place_id, comment_id, user["id"])
    except CommentSelfHelpfulError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except CommentError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/places/{place_id}/checkins", status_code=201)
def create_checkin(place_id: str, checkin: CheckinCreate, user: dict = Depends(get_current_user)):
    return add_checkin(
        place_id, user["display_name"], checkin.lat, checkin.lng, checkin.accuracy, user["id"]
    )


@app.get("/places/{place_id}/checkin-count")
def get_checkin_count(place_id: str):
    return {"count": count_recent_checkins(place_id)}


@app.post("/places/{place_id}/status", status_code=201)
def create_status(place_id: str, status: StatusCreate, user: dict = Depends(get_current_user)):
    return add_status(place_id, user["display_name"], status.tag, status.text, user["id"])


@app.get("/places/{place_id}/status")
def get_status(place_id: str, user: dict | None = Depends(get_current_user_optional)):
    exclude = set(user["blocked_user_ids"]) if user else None
    return list_status(
        place_id, exclude_user_ids=exclude, viewer_user_id=user["id"] if user else None
    )


@app.post("/places/{place_id}/status/{status_id}/helpful")
def mark_status_helpful(place_id: str, status_id: str, user: dict = Depends(get_current_user)):
    """Toggle: first call marks helpful, a second call from the same user
    unmarks it (see database/checkins_store.toggle_helpful_status). Marking
    your own status update is refused with 400; an unknown status_id is a
    404."""
    try:
        return toggle_helpful_status(place_id, status_id, user["id"])
    except SelfHelpfulError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except StatusError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Web Push (RFC 8030 + VAPID/RFC 8292) - see database/push_notify.py and
# scripts/generate_vapid_keys.py. No third-party account/API key is needed
# (unlike FCM/APNs): VAPID is a self-generated key pair the server keeps in
# .env. Real sends only start once VAPID_PRIVATE_KEY/VAPID_CLAIMS_EMAIL are
# actually set - see GET /push/vapid-public-key for the honest "not
# configured yet" case.
# ---------------------------------------------------------------------------


@app.get("/push/vapid-public-key")
def get_vapid_public_key():
    """The frontend needs this to call PushManager.subscribe({
    applicationServerKey }) - see frontend/src/lib/push.js. Returns 503
    with an honest message (not a fake/placeholder key) if the server
    hasn't had a real VAPID key pair generated yet (see
    scripts/generate_vapid_keys.py)."""
    public_key = os.getenv("VAPID_PUBLIC_KEY")
    if not public_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "VAPID anahtarları henüz üretilmedi. Sunucuda "
                "scripts/generate_vapid_keys.py çalıştırılıp .env dosyasına "
                "VAPID_PUBLIC_KEY/VAPID_PRIVATE_KEY eklenmeli."
            ),
        )
    return {"public_key": public_key}


@app.post("/push/subscribe", status_code=201)
def push_subscribe(payload: PushSubscriptionCreate, user: dict = Depends(get_current_user)):
    return add_subscription(user["id"], payload.endpoint, payload.keys.p256dh, payload.keys.auth)


@app.post("/push/unsubscribe", status_code=204)
def push_unsubscribe(payload: PushUnsubscribeRequest, user: dict = Depends(get_current_user)):
    remove_subscription(user["id"], payload.endpoint)


# ---------------------------------------------------------------------------
# Photo comparison - real perceptual-hash similarity (see
# database/photo_compare.py), never a fabricated/guessed percentage. Auth
# required (same "real identity" reasoning as comments/checkins/status).
# The uploaded photo is only ever read into memory for this one request and
# handed to compare_images() - it is never written to disk or stored
# anywhere (privacy), and goes out of scope (garbage-collectable) as soon as
# this function returns.
# ---------------------------------------------------------------------------

MAX_COMPARE_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_COMPARE_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@app.post("/places/{place_id}/compare-photo")
async def compare_photo(
    place_id: str,
    photo: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    if photo.content_type not in ALLOWED_COMPARE_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Desteklenmeyen dosya formatı. jpg, png veya webp yükle.",
        )

    reference_url = get_reference_photo_url(place_id)
    if not reference_url:
        raise HTTPException(status_code=404, detail="Bu mekan için referans fotoğraf yok.")

    uploaded_bytes = await photo.read()
    if len(uploaded_bytes) > MAX_COMPARE_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Dosya çok büyük (maks. 10MB).")

    try:
        return compare_images(reference_url, uploaded_bytes)
    except ReferenceDownloadError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except InvalidImageError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except PhotoCompareError as e:  # pragma: no cover - safety net
        raise HTTPException(status_code=500, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Moderation - moderator-only visibility panel. Before this, reports/hidden
# content were recorded but never surfaced to anyone (see
# docs/research/sonraki-adimlar-firsat-analizi.md) - moderation was
# effectively blind. See database/users_store.py "MODERATION MVP" note for
# how a user becomes a moderator (MODERATOR_EMAILS env var, no admin UI).
# ---------------------------------------------------------------------------


@app.get("/moderation/reports")
def moderation_list_reports(moderator: dict = Depends(get_current_moderator)):
    """Every report from every user, not just the caller's own."""
    return list_all_reports()


@app.post("/moderation/reports/{report_id}/resolve")
def moderation_resolve_report(report_id: str, moderator: dict = Depends(get_current_moderator)):
    """Mark a report as reviewed. Never touches the reported content
    itself - use /moderation/content/{content_type}/{content_id}/restore
    for that."""
    try:
        return resolve_report(report_id)
    except ReportError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/moderation/hidden-content")
def moderation_hidden_content(moderator: dict = Depends(get_current_moderator)):
    """Every comment/status update across every place currently hidden by
    the content filter (review_status == "hidden") or otherwise flagged."""
    return {
        "comments": list_hidden_comments(),
        "status_updates": list_hidden_status(),
    }


@app.post("/moderation/content/{content_type}/{content_id}/restore")
def moderation_restore_content(
    content_type: str,
    content_id: str,
    moderator: dict = Depends(get_current_moderator),
):
    """Moderator override for a content-filter false positive: sets the
    item's review_status back to "visible"."""
    try:
        if content_type == "comment":
            return restore_comment(content_id)
        if content_type == "status":
            return restore_status(content_id)
    except (CommentError, StatusError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    raise HTTPException(status_code=400, detail="content_type 'comment' veya 'status' olmalı.")


@app.get("/moderation/stats")
def moderation_stats(moderator: dict = Depends(get_current_moderator)):
    """Basit, moderatör-korumalı istatistik görünümü. Her sayı ilgili
    JSON deposundan bu çağrıda taze hesaplanır - hiçbiri saklanmaz/önbelleğe
    alınmaz ve hiçbiri uydurulmaz (bkz. CLAUDE.md "sahte veri yasak"): bir
    dosya yoksa/boşsa ilgili sayı sadece 0 olur, hata fırlatılmaz (her store
    fonksiyonu zaten dosya yoksa boş dict/list döner)."""
    reports = list_all_reports()
    venues_with_activity = list_place_ids_with_comments() | list_place_ids_with_activity()
    return {
        "total_users": count_users(),
        "total_comments": count_all_comments(),
        "total_checkins": count_all_checkins(),
        "total_status_updates": count_all_status(),
        "hidden_comments_count": len(list_hidden_comments()),
        "hidden_status_count": len(list_hidden_status()),
        "open_reports_count": sum(1 for r in reports if r["status"] == "open"),
        "resolved_reports_count": sum(1 for r in reports if r["status"] == "resolved"),
        "venues_with_activity": len(venues_with_activity),
    }
