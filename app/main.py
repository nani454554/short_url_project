import os
import time
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import SessionLocal, engine, Base
from app.models import URL
from app.schemas import URLCreate
from app.crud import create_short_url, get_original_url, get_url_stats

# Initialize Database
Base.metadata.create_all(bind=engine)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Logs to a file
        logging.StreamHandler()  # Logs to console
    ]
)

app = FastAPI()

# Dynamically determine the static files directory
BASE_DIR = Path(__file__).resolve().parent.parent  # Move up one directory
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Middleware for Logging & Performance Tracking
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()  # Track time
        response = await call_next(request)
        process_time = time.time() - start_time  # Calculate execution time

        log_message = (
            f"{request.client.host} - {request.method} {request.url.path} "
            f"Status: {response.status_code} - Time: {process_time:.4f}s"
        )
        
        if response.status_code >= 400:
            logging.error(log_message)
        else:
            logging.info(log_message)

        return response

app.add_middleware(LoggingMiddleware)

@app.get("/")
def home():
    logging.info("Homepage accessed")
    return RedirectResponse(url="/static/index.html")

@app.post("/shorten")
def shorten_url(url: URLCreate):
    db = SessionLocal()
    short_url = create_short_url(db, url.url)
    db.close()
    logging.info(f"Shortened URL: {url.url} -> {short_url}")
    return {"short_url": f"http://localhost:8000/{short_url}"}

@app.get("/{short_id}")
def redirect(short_id: str):
    db = SessionLocal()
    original_url = get_original_url(db, short_id)
    db.close()
    if not original_url:
        logging.warning(f"Short ID not found: {short_id}")
        raise HTTPException(status_code=404, detail="URL not found")
    
    logging.info(f"Redirecting {short_id} to {original_url}")
    return RedirectResponse(url=original_url)

@app.get("/stats/{short_id}")
def stats(short_id: str):
    db = SessionLocal()
    stats = get_url_stats(db, short_id)
    db.close()
    logging.info(f"Stats requested for {short_id}: {stats}")
    return stats
