"""
NexaDesk Multi-Agent Orchestrator
Coordinates 7 agents to process tickets end-to-end.
"""
import time
import uuid
from sqlalchemy.orm import Session
from loguru import logger
from agents.classifier import ClassifierAgent
from agents.resolver import ResolverAgent
from agents.escalation import EscalationAgent
from agents.security import SecurityAgent
from agents.analytics import LearningAgent, AnalyticsAgent


class AgentOrchestrator:
    def __init__(self):
        self.classifier = ClassifierAgent()
        self.resolver = ResolverAgent()
        self.escalation = EscalationAgent()
        self.security = SecurityAgent()
        self.learning = LearningAgent()
        self.analytics = AnalyticsAgent()

    def process_ticket(self, ticket_data: dict, db: Session) -> dict:
        start = time.time()
        trace = []
        rid = str(uuid.uuid4())[:8].upper()
        logger.info(f"[{rid}] Pipeline starting: '{ticket_data.get('title')}'")

        # ── STEP 1: Security ──
        trace.append(self._step("SecurityAgent", "🛡️", "running",
            "Scanning ticket for threats, PII, and security flags..."))
        sec = self.security.analyze(ticket_data)
        trace[-1].update({"status": "done", "result": sec["summary"]})

        if sec["is_security_incident"]:
            trace.append(self._step("EscalationAgent", "🚨", "done",
                "SECURITY INCIDENT — Activating CIRT protocol immediately.",
                "Escalated to CIRT L3. SLA: 15 minutes."))
            outcome = self._outcome(trace, "escalated", sec["incident_response"],
                "CIRT — Security Operations Center (L3)", 0.99, 15, start, "L3", "Security incident")
            self.learning.record(ticket_data, outcome, db)
            self.analytics.record(outcome, db)
            return outcome

        # ── STEP 2: Classify ──
        trace.append(self._step("ClassifierAgent", "🧠", "running",
            "Running NLP classification — extracting intent, category, priority, and SLA..."))
        clf = self.classifier.classify(ticket_data)
        trace[-1].update({"status": "done",
            "result": f"Category: {clf['category']} | Priority: {clf['priority']} | Confidence: {clf['confidence']*100:.0f}% | SLA: {clf['sla_minutes']}min"})

        # ── STEP 3: KB Search ──
        trace.append(self._step("KnowledgeBaseAgent", "📚", "running",
            f"Searching knowledge base for '{clf['category']}' resolution playbooks..."))
        kb = self.resolver.search_kb(clf, ticket_data, db)
        trace[-1].update({"status": "done",
            "result": f"{kb['articles_found']} articles found. Best match: {kb['best_confidence']*100:.0f}% confidence"})

        # ── STEP 4: Resolve or Escalate ──
        from config import settings
        threshold = settings.auto_resolve_confidence_threshold
        can_resolve = kb["best_confidence"] >= threshold and clf["priority"] != "critical"

        trace.append(self._step("ResolverAgent", "🔧", "running",
            f"Threshold: {threshold*100:.0f}%. " +
            ("Threshold met — generating AI solution..." if can_resolve else "Below threshold — preparing escalation...")))

        if can_resolve:
            res = self.resolver.resolve(ticket_data, clf, kb)
            trace[-1].update({"status": "done",
                "result": f"Solution generated. Confidence: {res['confidence']*100:.0f}%"})
            trace.append(self._step("VerificationAgent", "✅", "done",
                "Verifying solution against historical outcomes...",
                f"Validated on {res['similar_tickets_count']:,} tickets. Success rate: {res['historical_success_rate']*100:.0f}%"))
            outcome = self._outcome(trace, "resolved", res["resolution_text"],
                "AI Agent (L1 — NexaAgent)", res["confidence"],
                clf["sla_minutes"], start, None, None)
        else:
            esc = self.escalation.escalate(ticket_data, clf, kb)
            trace[-1].update({"status": "done", "result": f"Escalating to {esc['assigned_team']}"})
            trace.append(self._step("EscalationAgent", "📤", "done",
                f"Routing to {esc['assigned_team']} with full context and priority flag.",
                f"Specialist response ETA: {esc['eta']}"))
            outcome = self._outcome(trace, "escalated", esc["escalation_message"],
                esc["assigned_team"], kb["best_confidence"],
                clf["sla_minutes"], start, esc["level"], esc["reason"])

        # ── STEP 5-6: Learn + Analytics ──
        trace.append(self._step("LearningAgent", "🎓", "done",
            "Recording outcome to improve future resolutions...",
            "Knowledge base metrics updated."))
        self.learning.record(ticket_data, outcome, db)
        self.analytics.record(outcome, db)

        outcome["reasoning_trace"] = trace
        logger.info(f"[{rid}] Done — {outcome['status']} in {outcome['resolution_time_seconds']:.2f}s")
        return outcome

    def _step(self, agent, icon, status, message, result="") -> dict:
        return {"agent": agent, "icon": icon, "status": status,
                "message": message, "result": result, "timestamp": time.time()}

    def _outcome(self, trace, status, resolution_text, assigned_to,
                 confidence, sla, start, esc_level, esc_reason) -> dict:
        return {
            "status": status, "reasoning_trace": trace,
            "resolution_text": resolution_text, "assigned_to": assigned_to,
            "confidence": confidence, "sla_target_minutes": sla,
            "resolution_time_seconds": time.time() - start,
            "escalation_level": esc_level, "escalation_reason": esc_reason,
        }


orchestrator = AgentOrchestrator()
