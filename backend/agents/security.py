"""Security Agent — scans tickets for threats and PII"""
import re


THREAT_KEYWORDS = [
    "phishing", "malware", "ransomware", "hack", "breach", "suspicious",
    "virus", "trojan", "keylogger", "clicked link", "strange email",
    "unknown attachment", "password stolen", "account compromised",
]

DATA_LOSS_KEYWORDS = ["deleted", "lost files", "missing data", "ransomware", "encrypted files"]

PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",        # SSN
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
]


class SecurityAgent:
    def analyze(self, ticket_data: dict) -> dict:
        text = f"{ticket_data.get('title','')} {ticket_data.get('description','')}".lower()
        category = ticket_data.get("category", "")
        priority = ticket_data.get("priority", "medium")

        threat_hits = [kw for kw in THREAT_KEYWORDS if kw in text]
        data_loss_hits = [kw for kw in DATA_LOSS_KEYWORDS if kw in text]
        pii_found = any(re.search(p, text) for p in PII_PATTERNS)

        is_security = (
            category == "Security / Phishing"
            or len(threat_hits) >= 2
            or priority == "critical" and len(threat_hits) >= 1
        )
        is_data_loss = category == "Data Loss" or len(data_loss_hits) >= 2

        flags = []
        if threat_hits:
            flags.append(f"Threat keywords: {', '.join(threat_hits[:3])}")
        if pii_found:
            flags.append("PII detected — handle with care")
        if is_data_loss:
            flags.append("Data loss pattern detected")

        if is_security:
            summary = f"SECURITY INCIDENT — {len(threat_hits)} threat signals detected. CIRT protocol activated."
            incident_response = (
                f"SECURITY INCIDENT RESPONSE\n\n"
                f"IMMEDIATE ACTIONS — DO THESE NOW:\n"
                f"1. DO NOT click any links or open attachments\n"
                f"2. Forward suspicious email as ATTACHMENT to: security-incidents@company.com\n"
                f"3. Click Report Phishing in Outlook ribbon\n\n"
                f"IF YOU ALREADY CLICKED A LINK:\n"
                f"• DISCONNECT from ALL networks immediately (WiFi, Ethernet, Bluetooth)\n"
                f"• Call Security Hotline: Ext. 1-SEC (1-732) — available 24/7\n"
                f"• Change ALL passwords from a DIFFERENT device\n"
                f"• DO NOT restart your computer — preserves forensic evidence\n\n"
                f"WHAT WE ARE DOING:\n"
                f"✓ CIRT analyst assigned and notified\n"
                f"✓ Threat indicators being analyzed in SIEM\n"
                f"✓ Network monitoring enhanced for your device\n"
                f"Response ETA: 15 minutes"
            )
        elif is_data_loss:
            summary = "Data loss pattern detected. Emergency recovery protocol initiated."
            incident_response = (
                f"DATA RECOVERY EMERGENCY\n\n"
                f"STOP — DO NOT restart computer or save new files to affected drive!\n\n"
                f"RECOVERY STEPS:\n"
                f"1. Right-click parent folder → Properties → Previous Versions → Restore\n"
                f"2. Check Recycle Bin\n"
                f"3. OneDrive: Go to onedrive.com → Recycle Bin (30-day history)\n"
                f"4. Network drive: Auto-versioned every 4 hours\n\n"
                f"IF RANSOMWARE:\n"
                f"• Disconnect from ALL networks NOW\n"
                f"• Call Data Recovery Hotline: Ext. 1-DATA\n"
                f"• DO NOT pay any ransom\n\n"
                f"Data Recovery Specialist will contact you within 20 minutes."
            )
        else:
            summary = f"Clear. {len(flags)} minor flags noted." if flags else "Clear. No threats detected."
            incident_response = ""

        return {
            "is_security_incident": is_security or is_data_loss,
            "summary": summary,
            "flags": flags,
            "incident_response": incident_response,
            "pii_detected": pii_found,
        }
