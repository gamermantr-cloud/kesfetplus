from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from database.checkins_store import (
    STATUS_TAGS,
    add_checkin,
    add_status,
    count_recent_checkins,
    list_status,
)
from database.comments_store import add_comment, list_comments
from database.photo_compare import (
    InvalidImageError,
    PhotoCompareError,
    ReferenceDownloadError,
    compare_images,
    get_reference_photo_url,
)
from database.reports_store import VALID_TARGET_TYPES, add_report, list_reports_by_user
from database.users_store import (
    UserError,
    authenticate,
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
def register(payload: RegisterRequest):
    try:
        user = register_user(payload.email, payload.password, payload.display_name)
    except UserError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    token = create_session(user["id"])
    return {"token": token, "user": user}


@app.post("/auth/login")
def login(payload: LoginRequest):
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
    reports *they* filed, not everyone's. A real admin/moderation view is
    out of scope here."""
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
    return list_comments(place_id, exclude_user_ids=exclude)


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
    return list_status(place_id, exclude_user_ids=exclude)


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
