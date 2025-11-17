# Server (FastAPI) - Quick README

This folder contains a minimal FastAPI server used for the blog backend.

Quick start (assuming you already created and activated the virtualenv `.venv`):

1. Set DB credentials in `server/.env` (example below):

```
DB_USER=root
DB_PASS=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=blog_db
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the server (from `server/`):

```bash
python -m uvicorn app.main:app --reload --port 8000
```

4. Open the API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`

Notes about the `Post` model:
- `content` is mapped to a TEXT column to allow full article bodies.
- During development `SQLModel.metadata.create_all(engine)` creates tables automatically.

If you change the `Post` model column types and want to recreate the table during development, you can drop the table in MySQL and restart the server (development only):

```sql
DROP TABLE IF EXISTS post;
```

For production, use Alembic for proper migrations instead of dropping tables.
