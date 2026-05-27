from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .config import get_settings
from .database import create_tables
from .auth.router import router as auth_router
from .notes.router import router as notes_router
from .analytics.router import router as analytics_router

settings = get_settings()
# Resolve absolute path for the uploads folder (project root /uploads)
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
if not os.path.isdir(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB tables
create_tables()

# Routers
app.include_router(auth_router)
app.include_router(notes_router)
app.include_router(analytics_router)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "Smart Notes API is running"}
