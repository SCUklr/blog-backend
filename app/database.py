from sqlmodel import create_engine, SQLModel
import os
from dotenv import load_dotenv
load_dotenv()

# 优先使用 DATABASE_URL（Render 自动提供），如果没有则用本地 MySQL 配置
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 本地开发：使用 MySQL
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "blog_db")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # 线上生产：DATABASE_URL 是 PostgreSQL（Render 提供）
    # 需要将 postgresql:// 改为 postgresql+psycopg2://
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=True)