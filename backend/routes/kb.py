"""Knowledge Base routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.kb_article import KBArticle
from agents.resolver import KB_DATA

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])


@router.get("/")
def get_articles(search: str = Query(""), db: Session = Depends(get_db)):
    # Try DB first, fall back to hardcoded KB_DATA
    db_articles = db.query(KBArticle).filter(KBArticle.is_active == True).all()
    if db_articles:
        articles = [
            {"id": a.id, "title": a.title, "description": a.description,
             "category": a.category, "tags": a.tags.split(",") if a.tags else [],
             "resolution": a.resolution_steps, "icon": a.icon,
             "success_count": a.success_count}
            for a in db_articles
            if not search or search.lower() in a.title.lower() or search.lower() in (a.tags or "")
        ]
    else:
        articles = [
            {"id": str(i), "title": a["title"], "description": a["description"],
             "category": a["category"], "tags": a["tags"],
             "resolution": a["resolution"], "icon": a["icon"],
             "success_count": a["similar_count"]}
            for i, a in enumerate(KB_DATA)
            if not search or search.lower() in a["title"].lower()
               or any(search.lower() in t for t in a["tags"])
        ]
    return {"articles": articles, "total": len(articles)}
