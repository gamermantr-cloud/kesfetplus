from fastapi import FastAPI
from pydantic import BaseModel, Field

from database.comments_store import add_comment, list_comments

app = FastAPI(title="KesfetPlus")


class CommentCreate(BaseModel):
    author: str = Field(min_length=1, max_length=80)
    text: str = Field(min_length=1, max_length=2000)


@app.get("/")
def read_root():
    return {"name": "KesfetPlus", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/places/{place_id}/comments", status_code=201)
def create_comment(place_id: str, comment: CommentCreate):
    return add_comment(place_id, comment.author, comment.text)


@app.get("/places/{place_id}/comments")
def get_comments(place_id: str):
    return list_comments(place_id)
