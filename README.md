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
  
