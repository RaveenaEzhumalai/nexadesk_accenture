"""Escalation Agent — smart routing to human specialists"""

ESCALATION_MATRIX = {
    "Network / VPN":          {"team": "L2 Network Engineering",        "level": "L2", "eta": "30 minutes"},
    "Email / Outlook":        {"team": "L2 Exchange / M365 Team",        "level": "L2", "eta": "45 minutes"},
    "Laptop / Hardware":      {"team": "L2 Desktop Support",             "level": "L2", "eta": "2 hours"},
    "Software / Application": {"team": "L2 Application Support",         "level": "L2", "eta": "1 hour"},
    "Access / Permissions":   {"team": "L2 Identity & Access Management","level": "L2", "eta": "30 minutes"},
    "Security / Phishing":    {"team": "CIRT — Security Operations (L3)","level": "L3", "eta": "15 minutes"},
    "Data Loss":              {"team": "L3 Data Recovery Specialist",    "level": "L3", "eta": "20 minutes"},
    "Server / Infrastructure":{"team": "L3 Infrastructure / SRE Team",  "level": "L3", "eta": "15 minutes"},
    "Other":                  {"team": "L1 General IT Support",          "level": "L1", "eta": "4 hours"},
}


class EscalationAgent:
    def escalate(self, ticket_data: dict, classification: dict, kb_result: dict) -> dict:
        category = classification.get("category", "Other")
        priority = classification.get("priority", "medium")
        name = ticket_data.get("submitter_name", "there")

        routing = ESCALATION_MATRIX.get(category, ESCALATION_MATRIX["Other"])

        # Upgrade SLA for critical
        eta = routing["eta"]
        if priority == "critical":
            eta = "15 minutes"

        message = (
            f"Hello {name},\n\n"
            f"Your ticket requires specialist expertise and has been escalated to: "
            f"**{routing['team']}**\n\n"
            f"Priority: {priority.upper()} | Estimated Response: {eta}\n\n"
            f"WHAT HAPPENS NEXT:\n"
            f"• A specialist from {routing['team']} will contact you directly\n"
            f"• You will receive an email confirmation with your ticket number\n"
            f"• Track progress at: https://nexadesk.company.com/tickets\n\n"
            f"TO HELP US RESOLVE FASTER — Please have ready:\n"
            f"• Exact error messages (screenshots help)\n"
            f"• When the issue started\n"
            f"• What you tried already\n"
            f"• How many people are affected\n\n"
            f"— NexaDesk AI Escalation Agent"
        )

        return {
            "assigned_team": routing["team"],
            "level": routing["level"],
            "eta": eta,
            "escalation_message": message,
            "reason": f"Confidence below threshold or critical priority for {category}",
        }
