from fastapi import FastAPI
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

app = FastAPI(title="KesfetPlus")

# Dev-only: allow the Vite dev server from localhost and the local network
# (phone-on-same-wifi access). Not meant for a public deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):5173",
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class CommentCreate(BaseModel):
    author: str = Field(min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=2000)
    lat: float | None = None
    lng: float | None = None
    accuracy: float | None = None


class CheckinCreate(BaseModel):
    author: str = Field(min_length=1, max_length=80)
    lat: float | None = None
    lng: float | None = None
    accuracy: float | None = None


class StatusCreate(BaseModel):
    author: str = Field(min_length=1, max_length=80)
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


@app.post("/places/{place_id}/comments", status_code=201)
def create_comment(place_id: str, comment: CommentCreate):
    return add_comment(
        place_id, comment.author, comment.text, comment.lat, comment.lng, comment.accuracy
    )


@app.get("/places/{place_id}/comments")
def get_comments(place_id: str):
    return list_comments(place_id)


@app.post("/places/{place_id}/checkins", status_code=201)
def create_checkin(place_id: str, checkin: CheckinCreate):
    return add_checkin(place_id, checkin.author, checkin.lat, checkin.lng, checkin.accuracy)


@app.get("/places/{place_id}/checkin-count")
def get_checkin_count(place_id: str):
    return {"count": count_recent_checkins(place_id)}


@app.post("/places/{place_id}/status", status_code=201)
def create_status(place_id: str, status: StatusCreate):
    return add_status(place_id, status.author, status.tag, status.text)


@app.get("/places/{place_id}/status")
def get_status(place_id: str):
    return list_status(place_id)
