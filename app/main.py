from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, SQLModel
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
from uuid import uuid4
from .database import engine
from .models import Post
from pydantic import BaseModel
from datetime import datetime

class PostCreate(BaseModel):
    title: str
    content: str
    description: str | None = None
    tags: list[str] | None = None

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    created_at: datetime | None = None

app = FastAPI()

from fastapi.responses import RedirectResponse

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173", "http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/")
def root():
        """Redirect root to API docs to avoid 404 when browsing to /"""
        return RedirectResponse(url="/docs")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    # mount static files directory for uploaded assets
    static_dir = Path(__file__).resolve().parents[1] / 'static'
    uploads_dir = static_dir / 'uploads'
    uploads_dir.mkdir(parents=True, exist_ok=True)
    # mount once (mounting again will raise if already mounted)
    try:
        app.mount('/static', StaticFiles(directory=str(static_dir)), name='static')
    except Exception:
        pass

@app.get("/api/posts")
def list_posts():
    def post_to_dict(p: Post):
        return {
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "description": p.description,
            # expose tags as array for frontend convenience
            "tags": p.tags.split(',') if p.tags else [],
            "created_at": p.created_at,
        }

    with Session(engine) as session:
        posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()
        return [post_to_dict(p) for p in posts]

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="not found")
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "description": post.description,
            "tags": post.tags.split(',') if post.tags else [],
            "created_at": post.created_at,
        }

@app.post("/api/posts", status_code=201)
def create_post(payload: PostCreate):
    tags_str = ",".join(payload.tags) if payload.tags else None
    post = Post(title=payload.title, content=payload.content, description=payload.description, tags=tags_str)
    with Session(engine) as session:
        session.add(post)
        session.commit()
        session.refresh(post)
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "description": post.description,
            "tags": post.tags.split(',') if post.tags else [],
            "created_at": post.created_at,
        }


@app.post("/api/uploads")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Upload an image and return a URL.
    Saves files to server/static/uploads and returns {'url': '/static/uploads/<name>'}
    """
    static_dir = Path(__file__).resolve().parents[1] / 'static'
    uploads_dir = static_dir / 'uploads'
    uploads_dir.mkdir(parents=True, exist_ok=True)
    filename = file.filename or 'upload'
    ext = Path(filename).suffix
    name = f"{uuid4().hex}{ext}"
    dest = uploads_dir / name
    try:
        with dest.open('wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()
    # build absolute URL based on request (includes scheme and host)
    base = str(request.base_url).rstrip('/')
    url = f"{base}/static/uploads/{name}"
    return {"url": url, "filename": name}

@app.put("/api/posts/{post_id}")
def update_post(post_id: int, payload: PostUpdate):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="not found")
        if payload.title is not None: post.title = payload.title
        if payload.content is not None: post.content = payload.content
        if payload.description is not None: post.description = payload.description
        if payload.tags is not None: post.tags = ",".join(payload.tags)
        if payload.created_at is not None:
            post.created_at = payload.created_at
        session.add(post)
        session.commit()
        session.refresh(post)
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "description": post.description,
            "tags": post.tags.split(',') if post.tags else [],
            "created_at": post.created_at,
        }

@app.delete("/api/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    with Session(engine) as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="not found")
        session.delete(post)
        session.commit()
        return None