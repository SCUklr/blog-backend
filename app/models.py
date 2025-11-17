from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from datetime import datetime


class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    # use TEXT for content to allow long article bodies
    content: str = Field(sa_column=Column(Text))
    description: Optional[str] = None
    tags: Optional[str] = None  # 逗号分隔的 tags
    created_at: datetime = Field(default_factory=datetime.utcnow)