---

# Auth Service

A Django-based authentication service using **PostgreSQL**, **Redis**, and **JWT**.

---

## 🚀 Setup

1. Clone repo:

   ```bash
   git clone https://github.com/tesimune/auth-django.git
   cd auth-service
   ```
2. Create a `.env` file (set DB, Redis, JWT, and Django secrets).
3. Run with Docker:

   ```bash
   docker compose up --build
   ```

App runs at [http://localhost:8000](http://localhost:8000).

---

## ⚙️ Environment Variables

* `SECRET_KEY`, `DEBUG`
* `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST`, `DB_PORT`
* `REDIS_URL`
* `JWT_SECRET`, `JWT_ALGORITHM`

---

## 📡 API Endpoints

* `POST /accounts/create/` → Create account
* `POST /accounts/session/` → Login & return JWT
* `GET /accounts/profile/` → Profile (JWT required)

Docs: `/swagger/` (Swagger UI), `/redoc/` (ReDoc).

---

