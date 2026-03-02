"""Classifier Agent — NLP-based ticket categorization"""

CATEGORY_KEYWORDS = {
    "Network / VPN": ["vpn", "network", "wifi", "internet", "connection", "remote", "ping", "dns", "firewall", "proxy", "ssl", "certificate", "bandwidth"],
    "Email / Outlook": ["email", "outlook", "mail", "inbox", "calendar", "teams", "exchange", "ost", "pst", "smtp", "attachment", "sync"],
    "Laptop / Hardware": ["laptop", "slow", "freeze", "crash", "blue screen", "bsod", "keyboard", "mouse", "screen", "battery", "ram", "disk", "hardware", "printer", "monitor"],
    "Software / Application": ["software", "install", "application", "app", "license", "error", "update", "crash", "dll", "missing", "sap", "teams", "chrome", "office"],
    "Access / Permissions": ["password", "login", "locked", "access", "permission", "mfa", "2fa", "sso", "sharepoint", "active directory", "account", "reset", "unauthorized"],
    "Security / Phishing": ["phishing", "suspicious", "malware", "virus", "hack", "breach", "strange email", "clicked", "ransomware", "security alert"],
    "Data Loss": ["deleted", "lost", "missing file", "recover", "restore", "backup", "ransomware", "corrupted", "overwritten"],
    "Server / Infrastructure": ["server", "down", "outage", "cloud", "azure", "aws", "production", "database", "api", "website", "deploy", "kubernetes"],
}

PRIORITY_KEYWORDS = {
    "critical": ["down", "outage", "production", "all users", "company-wide", "data loss", "ransomware", "breach", "emergency", "critical"],
    "high": ["urgent", "important", "multiple users", "team", "department", "deadline", "today"],
    "low": ["minor", "low priority", "when possible", "not urgent", "cosmetic", "nice to have"],
}

SLA_MAP = {"critical": 15, "high": 60, "medium": 240, "low": 480}


class ClassifierAgent:
    def classify(self, ticket_data: dict) -> dict:
        title = ticket_data.get("title", "").lower()
        desc = ticket_data.get("description", "").lower()
        text = f"{title} {desc}"
        submitted_cat = ticket_data.get("category", "")
        submitted_pri = ticket_data.get("priority", "medium")

        # Score categories
        scores = {cat: sum(1 for kw in kws if kw in text) for cat, kws in CATEGORY_KEYWORDS.items()}
        best_cat = max(scores, key=scores.get)
        cat_confidence = min(0.99, 0.60 + scores[best_cat] * 0.08)

        # Use submitted category if provided and has score
        final_cat = submitted_cat if submitted_cat and scores.get(submitted_cat, 0) > 0 else best_cat
        if submitted_cat and not scores.get(submitted_cat, 0):
            final_cat = submitted_cat  # trust user

        # Priority detection
        final_pri = submitted_pri
        for pri, kws in PRIORITY_KEYWORDS.items():
            if any(kw in text for kw in kws):
                final_pri = pri
                break
        # Critical always wins if user said critical
        if submitted_pri == "critical":
            final_pri = "critical"

        return {
            "category": final_cat,
            "priority": final_pri,
            "confidence": round(cat_confidence, 2),
            "sla_minutes": SLA_MAP.get(final_pri, 240),
            "keywords_matched": [kw for kw in CATEGORY_KEYWORDS.get(final_cat, []) if kw in text],
        }
