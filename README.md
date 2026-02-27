# Personal Blog Platform (Flask + PostgreSQL)

A production-oriented blog platform built with Flask and PostgreSQL that showcases backend engineering fundamentals: authentication, ORM-based data modeling, secure credential handling, and cloud deployment.

> **Live Demo:** _https://blogwebsite-production-63da.up.railway.app/_
> **Tech:** Flask · SQLAlchemy · PostgreSQL · Railway · Flask-Login

---
## Backend Engineering HIghlights

- Implemented session-based authentication using Flask-Login
- Secured user credentials with hashed passwords (Werkzeug)
- Designed relational database schema using SQLAlchemy ORM
- Enforced CSRF protection on all form submissions via Flask-WTF
- Configured environment-based settings for development vs production
- Deployed application with managed PostgreSQL database (Railway)
- Structured application with separation of routing, models, and templates
- Implemented persistent file handling for uploaded thumbnail assets

---

## Architecture Overview

**Request flow:** Client → Flask Routes → Auth/Validation → Service/DB Layer (SQLAlchemy) → PostgreSQL

- **Routing layer:** handles HTTP requests and maps them to views/actions
- **Auth layer:** restricts admin-only actions (create/edit) using Flask-Login
- **Validation layer:** validates form input and enforces CSRF protection (Flask-WTF)
- **Persistence layer:** SQLAlchemy models + ORM queries for database access
- **Storage layer:** thumbnail uploads saved to persistent storage; thumbnails only update when a new file is provided

This layered structure keeps business logic organized and supports portability between local SQLite development and production PostgreSQL.

---

## Database Design

### User Model

- `id` (Primary Key)
- `name`
- `email` (Unique)
- `password_hash`

### Post Model

- `id` (Primary Key)
- `title`
- `body` (Markdown content)
- `thumbnail_filename`
- `is_featured` (Boolean)
- `author_id` (Foreign Key → User.id)
- `timestamp`

### Relationships

- One-to-many relationship between `User` and `Post`
- Foreign key constraints enforce referential integrity
- ORM relationships simplify querying associated posts by author

---

## Security Practices

- Passwords are hashed before storage using Werkzeug (`generate_password_hash`)
- No plaintext passwords are stored in the database
- CSRF protection enforced on form submissions via Flask-WTF
- Privileged actions (create/edit posts) are restricted to authenticated users
- Secrets (e.g., `SECRET_KEY`, `DATABASE_URL`) are managed via environment variables
- Separate configurations for development (SQLite) and production (PostgreSQL)

---

## Tech Stack

**Backend**
- Python
- Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Werkzeug

**Database**
- PostgreSQL (Production)
- SQLite (Development)

**Deployment**
- Railway (Cloud hosting)

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/blog-project.git
cd blog-project
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the environment:

**Mac/Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///blog.db
```

For production (example):

```env
DATABASE_URL=postgresql://username:password@host:port/dbname
```

### 5. Initialize the database

```bash
flask shell
```

Inside the Flask shell:

```python
from app import db
db.create_all()
exit()
```

### 6. Run the application

```bash
flask run
```
  
