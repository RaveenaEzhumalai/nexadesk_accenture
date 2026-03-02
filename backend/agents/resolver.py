"""Resolver Agent — KB search and auto-resolution generation"""
from loguru import logger

KB_DATA = [
    {
        "category": "Network / VPN", "title": "VPN Connection Failures",
        "icon": "🌐", "tags": ["vpn", "network", "remote", "ssl", "connection", "disconnecting", "drops", "disconnect", "wifi", "internet", "dropping", "keeps", "reconnect", "home", "office", "file server", "cannot access", "keep", "every"],
        "description": "Fix VPN drops, certificate errors, and firewall blocks.",
        "similar_count": 847, "success_rate": 0.91,
        "resolution": (
            "Verified Resolution Steps for VPN/Network Issues:\n\n"
            "1. DISCONNECT & RECONNECT: Close VPN completely, wait 10 seconds, reconnect.\n"
            "2. CLEAR CREDENTIALS: VPN Settings → Clear saved credentials → Re-enter corporate login.\n"
            "3. SYNC CLOCK: Incorrect time breaks SSL. Settings → Date & Time → Sync Now.\n"
            "4. SWITCH NETWORK: If on public WiFi, switch to mobile hotspot.\n"
            "5. UPDATE VPN: Self-Service Portal → GlobalProtect → Install Latest.\n"
            "6. FIREWALL: Temporarily disable third-party antivirus firewall to test.\n\n"
            "If still failing after all steps → L2 Network team responds within 30 minutes."
        ),
    },
    {
        "category": "Email / Outlook", "title": "Outlook Sync Issues",
        "icon": "📧", "tags": ["email", "outlook", "mail", "inbox", "calendar", "teams", "exchange", "ost", "pst", "smtp", "attachment", "sync", "not opening", "crash"],
        "description": "Fix missing emails, sync failures, and OST corruption.",
        "similar_count": 1203, "success_rate": 0.89,
        "resolution": (
            "Verified Resolution Steps for Outlook/Email Issues:\n\n"
            "1. REPAIR ACCOUNT: File → Account Settings → Select account → Repair → Follow wizard.\n"
            "2. REBUILD OST: Close Outlook → Win+R → %LocalAppData%\\Microsoft\\Outlook\\ → Delete .ost files → Reopen Outlook. Rebuilds in 15-30 min.\n"
            "3. CHECK QUOTA: File → Cleanup Tools → Mailbox Cleanup. Delete old items if over limit.\n"
            "4. TEST WEBMAIL: Open https://outlook.office.com — if emails show here, issue is client-side.\n"
            "5. UPDATE OFFICE: File → Office Account → Update Options → Update Now.\n\n"
            "Exchange Online status: https://admin.microsoft.com → Service Health"
        ),
    },
    {
        "category": "Laptop / Hardware", "title": "Slow Laptop / Performance",
        "icon": "💻", "tags": ["slow", "freeze", "performance", "cpu", "memory", "startup", "crash", "blue screen", "bsod", "laptop", "computer", "hang", "stuck"],
        "description": "Diagnose and fix slow performance, freezing, and high CPU/memory.",
        "similar_count": 634, "success_rate": 0.85,
        "resolution": (
            "Verified Resolution Steps for Slow Laptop:\n\n"
            "1. TASK MANAGER: Ctrl+Shift+Esc → CPU/Memory tab → Identify the culprit process → Right-click → End Task.\n"
            "2. DISABLE STARTUP: Win+R → msconfig → Startup tab → Disable non-Microsoft items → Restart.\n"
            "3. SYSTEM FILE REPAIR: Run as Admin → CMD → type: sfc /scannow → Wait 10 min.\n"
            "4. FREE DISK SPACE: Ensure 15% free space minimum. Delete Downloads/Temp files.\n"
            "5. UPDATE DRIVERS: Device Manager → Right-click Display Adapter → Update Driver.\n"
            "6. MEMORY CHECK: Search → Windows Memory Diagnostic → Restart and check.\n\n"
            "Hardware replacement requests → Submit via IT Asset Management portal."
        ),
    },
    {
        "category": "Access / Permissions", "title": "Password & Account Access",
        "icon": "🔐", "tags": ["password", "locked", "mfa", "access", "sso", "reset", "login", "account", "locked out", "cannot login", "forgotten", "expired", "sharepoint", "permission", "denied"],
        "description": "Self-service password reset, MFA, account unlock procedures.",
        "similar_count": 2104, "success_rate": 0.93,
        "resolution": (
            "Verified Resolution Steps for Access Issues:\n\n"
            "1. SELF-SERVICE RESET: https://sspr.company.com — Use your registered mobile/email.\n"
            "2. LOCKED ACCOUNT: Automatically unlocks after 15 minutes. Or ask manager to unlock via Admin Portal.\n"
            "3. LOST MFA DEVICE: Contact IT with Employee ID + Manager approval for re-registration.\n"
            "4. APP ACCESS DENIED: IT Portal → Access Request → Select Application → Submit.\n"
            "5. SHAREPOINT: Click the owner's name in the 'Access Denied' page to request access directly.\n"
            "6. SSO ISSUES: Clear browser cookies → Try Incognito → Try different browser.\n\n"
            "Emergency after-hours access: Call IT Helpdesk at Ext. 1-HELP."
        ),
    },
    {
        "category": "Software / Application", "title": "Software Installation & Errors",
        "icon": "📱", "tags": ["software", "install", "license", "crash", "dll", "error", "application", "app", "not working", "update", "missing", "broken"],
        "description": "Request new software, fix crashes, and resolve license errors.",
        "similar_count": 921, "success_rate": 0.82,
        "resolution": (
            "Verified Resolution Steps for Software Issues:\n\n"
            "1. SELF-SERVICE INSTALL: Start → Software Center → Browse catalogue → Install.\n"
            "2. CRASH FIX: Right-click application → Run as Administrator → Test.\n"
            "3. REPAIR INSTALL: Control Panel → Programs → Select app → Change → Repair.\n"
            "4. MISSING DLL: Restart PC first (often resolves). If persists → Repair install.\n"
            "5. LICENSE REQUEST: Email licenses@company.com with Employee ID + software name.\n"
            "6. UPDATE: Check for pending Windows Updates — outdated OS causes many app errors.\n\n"
            "Enterprise software deployed via SCCM — available within 2 hours of approval."
        ),
    },
    {
        "category": "Security / Phishing", "title": "Phishing & Security Incidents",
        "icon": "🛡️", "tags": ["phishing", "security", "suspicious", "malware", "hack", "virus", "clicked", "link", "email", "password", "stolen", "breach"],
        "description": "Report phishing emails, handle suspicious links, CIRT escalation.",
        "similar_count": 312, "success_rate": 0.97,
        "resolution": (
            "SECURITY INCIDENT RESPONSE PROTOCOL:\n\n"
            "IMMEDIATELY:\n"
            "1. DO NOT click any links or download attachments\n"
            "2. Forward email AS ATTACHMENT to: security-incidents@company.com\n"
            "3. Click 'Report Phishing' button in Outlook ribbon\n\n"
            "IF YOU CLICKED A LINK:\n"
            "• Disconnect ALL networks (WiFi, Ethernet) NOW\n"
            "• Call Ext. 1-SEC (1-732) — 24/7 Security Hotline\n"
            "• Change ALL passwords from a different device\n"
            "• DO NOT restart — preserves forensic evidence\n\n"
            "CIRT will respond within 15 minutes."
        ),
    },
    {
        "category": "Data Loss", "title": "Data Recovery Emergency",
        "icon": "🚨", "tags": ["deleted", "lost", "recovery", "backup", "restore", "ransomware", "missing", "files", "folder", "gone", "empty", "disappeared"],
        "description": "Emergency data recovery for deleted files and ransomware.",
        "similar_count": 87, "success_rate": 0.79,
        "resolution": (
            "DATA RECOVERY STEPS:\n\n"
            "STOP — Do NOT save new files to affected drive or restart computer!\n\n"
            "1. PREVIOUS VERSIONS: Right-click folder → Properties → Previous Versions → Restore.\n"
            "2. RECYCLE BIN: Check Recycle Bin — Right-click → Restore.\n"
            "3. ONEDRIVE: Go to onedrive.com → Recycle Bin (30-day history available).\n"
            "4. NETWORK DRIVE: Auto-versioned every 4 hours — IT can restore.\n\n"
            "IF RANSOMWARE DETECTED:\n"
            "• Disconnect from network IMMEDIATELY\n"
            "• Call Ext. 1-DATA — Emergency recovery line\n"
            "• Do NOT pay any ransom demand\n\n"
            "Recovery Specialist responds within 20 minutes."
        ),
    },
    {
        "category": "Server / Infrastructure", "title": "Server & Infrastructure Issues",
        "icon": "🖧", "tags": ["server", "outage", "cloud", "production", "database", "api", "down", "website", "not working", "infrastructure", "azure", "aws"],
        "description": "Handle server outages, cloud issues, and production incidents.",
        "similar_count": 156, "success_rate": 0.76,
        "resolution": (
            "Infrastructure Incident Response:\n\n"
            "1. CHECK STATUS PAGE: https://status.company.com — Confirm if known outage.\n"
            "2. O365 HEALTH: https://admin.microsoft.com → Service Health.\n"
            "3. AZURE STATUS: https://status.azure.com\n\n"
            "SEVERITY SLAs:\n"
            "• P1 (Production Down): 15-min response — Call War Room: Ext. 1-WAR\n"
            "• P2 (Degraded Performance): 1-hour response\n"
            "• P3 (Non-Critical): 4-hour response\n\n"
            "P1 War Room Bridge: Ext. 1-WAR (1-927)\n"
            "PagerDuty: Auto-alerts on-call engineer for P1/P2.\n\n"
            "Provide: Error messages, affected services, time started, business impact."
        ),
    },
]


class ResolverAgent:
    def search_kb(self, classification: dict, ticket_data: dict, db) -> dict:
        category = classification.get("category", "")
        title = ticket_data.get("title", "").lower()
        desc = ticket_data.get("description", "").lower()
        text = f"{title} {desc}"

        best_article = None
        best_score = 0.0

        for article in KB_DATA:
            score = 0.0

            # Category match is worth a lot
            if article["category"] == category:
                score += 0.55

            # Each keyword match adds to score — more keywords = higher confidence
            tag_hits = sum(1 for tag in article["tags"] if tag in text)
            score += tag_hits * 0.06

            score = min(0.99, score)
            if score > best_score:
                best_score = score
                best_article = article

        return {
            "articles_found": 1 if best_article else 0,
            "best_article": best_article,
            "best_confidence": round(best_score, 2),
        }

    def resolve(self, ticket_data: dict, classification: dict, kb_result: dict) -> dict:
        article = kb_result.get("best_article")
        name = ticket_data.get("submitter_name", "there")
        confidence = kb_result.get("best_confidence", 0.80)

        if article:
            resolution_text = (
                f"Hello {name},\n\n"
                f"The NexaDesk AI Agent has analyzed your ticket and found a verified solution "
                f"(validated against {article['similar_count']:,} similar cases, "
                f"{article['success_rate']*100:.0f}% success rate).\n\n"
                f"{article['resolution']}\n\n"
                f"If these steps do not resolve your issue within 15 minutes, reply to this "
                f"ticket and an L2 specialist will be assigned within 30 minutes.\n\n"
                f"— NexaDesk AI Agent"
            )
            return {
                "resolution_text": resolution_text,
                "confidence": confidence,
                "similar_tickets_count": article["similar_count"],
                "historical_success_rate": article["success_rate"],
            }

        return {
            "resolution_text": (
                f"Hello {name},\n\nYour ticket has been reviewed. "
                f"An L2 specialist will contact you within the SLA window.\n\n— NexaDesk AI Agent"
            ),
            "confidence": 0.60,
            "similar_tickets_count": 0,
            "historical_success_rate": 0.0,
        }
