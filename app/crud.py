from sqlalchemy.orm import Session
from app.models import URL
import app.utils as utils

def create_short_url(db: Session, original_url: str):
    short_id = utils.generate_short_id()
    db_url = URL(short_id=short_id, original_url=original_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return short_id

def get_original_url(db: Session, short_id: str):
    url_entry = db.query(URL).filter(URL.short_id == short_id).first()
    if url_entry:
        url_entry.clicks += 1
        db.commit()
        return url_entry.original_url
    return None

def get_url_stats(db: Session, short_id: str):
    url_entry = db.query(URL).filter(URL.short_id == short_id).first()
    if url_entry:
        return {"original_url": url_entry.original_url, "clicks": url_entry.clicks}
    return None
