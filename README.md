# Smart Notes & File Organizer

A modern, production-grade student productivity platform built with a FastAPI backend, React frontend, SQLite database, AWS S3 for file storage, and PySpark for analytics.

## Features

- **Authentication**: Secure JWT-based login/registration.
- **Dashboard**: Modern overview of all your academic materials.
- **Upload**: Drag-and-drop file upload to AWS S3.
- **Organization**: Sort by subject and search instantly.
- **Analytics**: PySpark-powered data aggregations showing upload trends and top subjects.
- **Premium UI**: Designed with Tailwind CSS v4 and Framer Motion for a startup-grade feel.

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS v4, Framer Motion, Recharts, Lucide Icons.
- **Backend**: FastAPI, SQLAlchemy, Pydantic.
- **Storage**: AWS S3.
- **Analytics**: Apache PySpark.
- **Database**: SQLite (Development) / PostgreSQL ready.

## Demo

- Watch the app demo: https://youtu.be/AysBdgxKC-Y

- Preview:

	[![Demo video](https://img.youtube.com/vi/AysBdgxKC-Y/hqdefault.jpg)](https://youtu.be/AysBdgxKC-Y)

## Project Summary for Reports

- **Purpose**: A student productivity platform to upload, organize, and analyze academic files; includes a web UI, REST API, file storage on S3, and PySpark analytics.
- **Core Capabilities**: User authentication, file upload & organization by subject, search, dashboard visualizations, and analytics (upload trends, top subjects, file-type distribution).

**Architecture & Components**
- **Frontend**: React + Vite app in [frontend](frontend). Implements pages for Auth, Dashboard, Upload, Analytics, Profile, and uses Tailwind CSS and Framer Motion for UI polish.
- **Backend**: FastAPI app in [backend/app](backend/app). Handles REST endpoints for auth, notes, uploads, analytics triggers; uses SQLAlchemy and Pydantic for models and validation.
- **Storage**: AWS S3 for user file storage. Uploads are referenced in DB and served via pre-signed URLs.
- **Database**: SQLite for development; prepared for PostgreSQL in production. Schema files and models live under `backend/app/*/models.py`.
- **Analytics**: PySpark job for aggregations located at [aws/glue/smart_notes_analytics_job.py](aws/glue/smart_notes_analytics_job.py). Runs on AWS Glue (or locally via Spark) to compute top subjects, monthly uploads, file-type distribution per user and writes JSON results back to S3.
- **Deployment scripts**: `deploy_ec2.sh` and docs in `docs/` covering AWS setup and deployment steps.

**Data Flow**
- User uploads file via frontend → frontend sends to backend → backend stores file in S3 and a metadata record in DB → periodic/triggered analytics job reads metadata from S3/json (or from consolidated dataset) → writes aggregated JSON results back to S3 → frontend fetches visualization data from backend which reads that JSON.

**Key Files & Entry Points**
- **Backend app**: [backend/app/main.py](backend/app/main.py) — FastAPI app and route registration.
- **Auth**: [backend/app/auth/router.py](backend/app/auth/router.py), [backend/app/auth/service.py](backend/app/auth/service.py) — JWT flows and password handling.
- **Notes & Uploads**: [backend/app/notes/router.py](backend/app/notes/router.py), [backend/app/storage/s3.py](backend/app/storage/s3.py).
- **Analytics job**: [aws/glue/smart_notes_analytics_job.py](aws/glue/smart_notes_analytics_job.py) — PySpark Glue job logic and S3 output.
- **Frontend boot**: [frontend/src/main.jsx](frontend/src/main.jsx) and pages at [frontend/src/pages](frontend/src/pages).

**How We Used Each Technology**
- **FastAPI**: Exposed REST endpoints for auth, notes, uploads, and analytics results. Uses Pydantic for request/response schemas.
- **React + Vite**: SPA for user interaction; components split into pages and shared UI pieces. Uses `services/api.js` to call backend endpoints.
- **AWS S3**: Primary object store for uploaded files and analytics outputs. Backend creates pre-signed URLs for secure upload/download.
- **PySpark (Glue)**: Aggregation and analytics implemented in a stateless batch job; grouped by subject, month, and file type then exported as JSON.
- **SQLite/Postgres**: Relational metadata like users and file records; SQLite used in dev for simplicity, app is ready for PostgreSQL in prod.
- **SQLAlchemy**: ORM for DB models and migrations if added.

**Running Locally (summary)**
- Backend: `cd backend` → create virtual env → `pip install -r requirements.txt` → create `.env` from `.env.example` → `uvicorn app.main:app --reload`.
- Frontend: `cd frontend` → `npm install` → `npm run dev`.
- Analytics: run the PySpark script locally with a Spark environment or submit to AWS Glue using provided args (`input_path`, `output_path`, `user_id`). See [aws/glue/smart_notes_analytics_job.py](aws/glue/smart_notes_analytics_job.py).

**Deployment Notes**
- AWS: Use S3 for storage, Glue for scheduled analytics, and an EC2 or container host (scripts like `deploy_ec2.sh`) for backend if not using managed services. See `docs/AWS_SETUP.md` and `docs/DEPLOYMENT.md` for step-by-step instructions.

## Quick Start (Local Development)

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env based on .env.example
cp .env.example .env

# Run FastAPI server
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.
