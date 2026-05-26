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
