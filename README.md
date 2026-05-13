# FastAPI Blog

A full-stack blog application built with **FastAPI**, featuring JWT authentication, async PostgreSQL, AWS S3 media storage, and server-side rendering with Jinja2. Deployed on **Google Cloud** via Docker.

🌐 **Live Demo:** https://fastapi-service-1079761656263.us-east4.run.app/

---

## Features

- **JWT Authentication** — secure login, registration, and token-based sessions stored in HTTP-only cookies
- **Password Reset Flow** — time-limited reset tokens sent via email (aiosmtplib + SHA-256 hashed tokens)
- **Post Management** — create, view, and delete blog posts with like counts; paginated infinite scroll via REST API
- **Profile Pictures** — image upload with Pillow validation, stored on **AWS S3**
- **Security Middleware** — HSTS, X-Frame-Options, X-Content-Type-Options, and Content Security Policy headers
- **Async Database** — SQLAlchemy 2.0 async ORM with PostgreSQL; migrations managed by Alembic
- **Server-Side Rendering** — Jinja2 templates with vanilla JavaScript for dynamic interactions
- **Tests** — pytest test suite covering user and post endpoints

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.135 + Uvicorn |
| Language | Python 3.14 |
| Database | PostgreSQL + SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | PyJWT + pwdlib (Argon2) |
| Storage | AWS S3 (boto3) |
| Email | aiosmtplib |
| Templates | Jinja2 |
| Validation | Pydantic v2 + pydantic-settings |
| Containerisation | Docker (multi-stage build with UV) |
| Cloud | Google Cloud (Cloud Run / GCE) |
| Previous Deploy | Nginx + Linode + FreeDNS |

---

## Project Structure

```
fastapi-blog/
├── main.py               # App entry point, middleware, lifespan
├── models.py             # SQLAlchemy ORM models (User, Post, PasswordResetToken)
├── schemas.py            # Pydantic request/response schemas
├── auth.py               # JWT creation/verification, password hashing, reset tokens
├── database.py           # Async engine, session factory, Base
├── config.py             # Pydantic settings (loaded from .env)
├── email_utils.py        # Async email sending via aiosmtplib
├── image_utils.py        # Pillow image processing & S3 upload
├── routers/
│   ├── posts.py          # Post CRUD + likes + pagination API
│   └── users.py          # Register, login, token, profile, password reset
├── templates/            # Jinja2 HTML templates
├── static/               # CSS and JavaScript
├── alembic/              # Database migration scripts
├── tests/                # pytest test suite
└── Dockerfile            # Multi-stage production build (UV + slim Python)
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL database
- AWS S3 bucket (or compatible storage)
- SMTP server for email (e.g. Gmail, Mailtrap)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/fastapi-blog.git
cd fastapi-blog
```

### 2. Create a `.env` file

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/blogdb

SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your@email.com
MAIL_USE_TLS=true

FRONTEND_URL=http://localhost:8000
```

> ⚠️ Never commit `.env` to version control.

### 3. Run with Docker (recommended)

```bash
docker build -t fastapi-blog .
docker run -p 8080:8080 --env-file .env fastapi-blog
```

Then visit [http://localhost:8080](http://localhost:8080)

### 4. Run locally without Docker

```bash
# Install uv (https://docs.astral.sh/uv/)
uv sync

# Run database migrations
uv run alembic upgrade head

# Start the server
uv run fastapi dev main.py
```

### 5. Run tests

```bash
uv run pytest
```

---

## Deployment

### Google Cloud (current)

The app is containerised using a **multi-stage Dockerfile** (builder stage with [UV](https://github.com/astral-sh/uv) for fast dependency resolution, production stage with a minimal Python slim image). The container is deployed to Google Cloud.

Key Docker optimisations:
- Non-root `appuser` for security
- `UV_COMPILE_BYTECODE=1` for faster startup
- Dependencies cached separately from app code for faster rebuilds
- `exec fastapi run` so the process receives SIGTERM cleanly

### Previous deployment

The app was also deployed manually on a **Linode VPS** behind **Nginx** as a reverse proxy, with a free domain via **FreeDNS**.

---

## Environment Variables Reference

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime (default: 30) |
| `S3_BUCKET_NAME` | S3 bucket for profile picture uploads |
| `S3_REGION` | AWS region (default: us-east-1) |
| `MAIL_SERVER` | SMTP host |
| `MAIL_FROM` | Sender email address |
| `FRONTEND_URL` | Base URL for email links (e.g. password reset) |
| `POSTS_PER_PAGE` | Pagination page size (default: 10) |
| `MAX_UPLOAD_SIZE_BYTES` | Max profile picture size (default: 5 MB) |
| `RESET_TOKEN_EXPIRE_MINUTES` | Password reset token lifetime (default: 60) |

---

## API Docs

Interactive Swagger docs are available at `/docs` and ReDoc at `/redoc` when the server is running.

---
