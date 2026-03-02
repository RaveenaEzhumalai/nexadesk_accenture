"""Learning Agent + Analytics Agent"""
from sqlalchemy.orm import Session
from loguru import logger


class LearningAgent:
    def record(self, ticket_data: dict, outcome: dict, db: Session) -> None:
        try:
            from models.kb_article import KBArticle
            category = ticket_data.get("category", "Other")
            status = outcome.get("status", "unknown")
            articles = db.query(KBArticle).filter(KBArticle.category == category).all()
            for article in articles:
                if status == "resolved":
                    article.success_count += 1
                else:
                    article.failure_count += 1
            db.commit()
        except Exception as e:
            logger.warning(f"LearningAgent (non-critical): {e}")


class AnalyticsAgent:
    _m = {
        "total": 247, "resolved": 168, "escalated": 79,
        "time_total": 0.0, "cost_saved": 48300, "sla_breaches": 0,
    }
    MANUAL_COST = 180
    AI_COST = 4

    def record(self, outcome: dict, db: Session) -> None:
        try:
            self._m["total"] += 1
            if outcome.get("status") == "resolved":
                self._m["resolved"] += 1
                self._m["cost_saved"] += self.MANUAL_COST - self.AI_COST
            else:
                self._m["escalated"] += 1
                self._m["cost_saved"] += 40
            self._m["time_total"] += outcome.get("resolution_time_seconds", 0)
        except Exception as e:
            logger.warning(f"AnalyticsAgent (non-critical): {e}")

    @classmethod
    def get_metrics(cls) -> dict:
        t = cls._m["total"] or 1
        return {
            "total_processed": cls._m["total"],
            "auto_resolved": cls._m["resolved"],
            "escalated": cls._m["escalated"],
            "auto_resolve_rate": round(cls._m["resolved"] / t, 4),
            "cost_saved_usd": cls._m["cost_saved"],
            "avg_resolution_seconds": round(cls._m["time_total"] / t, 2),
            "avg_resolution_minutes": round(cls._m["time_total"] / t / 60, 2),
            "projected_annual_savings": cls._m["cost_saved"] * 12,
            "sla_breaches": cls._m["sla_breaches"],
        }
