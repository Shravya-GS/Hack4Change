"""
risk_detector.py
================
Behavioral risk detector for relapse prediction.
Analyzes daily check-in patterns to compute a risk score
and identify warning signs before relapse occurs.
"""

from typing import Dict, List
from datetime import datetime


# Risk weights for each behavioral signal
RISK_WEIGHTS = {
    "craving_level": 3.5,       # 1–10 scale, strongest predictor
    "social_isolation": 20,     # being alone is a major trigger
    "sleep_deprivation": 15,    # <6 hours sleep increases relapse risk
    "no_physical_activity": 10, # inactivity correlates with low mood
    "mood_depressed": 25,       # depression is the #1 relapse trigger
    "mood_stressed": 15,
    "mood_craving": 30,         # explicit craving state
    "streak_broken": 20,        # recent use detected
    "worsening_trend": 20,      # 3+ days of worsening mood
}

MOTIVATIONAL_MESSAGES = {
    "LOW": [
        "You're doing amazing! Every day sober is a victory. 💚",
        "Keep going — your future self is proud of you.",
        "Small steps every day lead to big changes.",
    ],
    "MEDIUM": [
        "You're facing challenges, but you've overcome harder things before. 💪",
        "Reach out to someone you trust today. You don't have to do this alone.",
        "Remember why you started. Your motivation — {motivation} — is real and worth it.",
    ],
    "HIGH": [
        "This is a tough moment, but it WILL pass. Call someone right now. 📞",
        "You've come too far to give up today. Reach out — help is always available.",
        "Crisis helpline: iCall — 9152987821. Please call. 💚",
    ],
    "CRITICAL": [
        "You are not alone. Please call iCall India: 9152987821 right now. 💚",
        "This feeling is temporary. Please reach out to a counselor immediately.",
    ],
}


class RiskDetector:

    def analyze(self, checkin: Dict, history: List[Dict]) -> Dict:
        """
        Analyzes a single check-in against recent history.
        Returns risk score, level, detected triggers, and recommendations.
        """
        score = 0
        triggers = []

        # 1. Craving level (strongest signal)
        craving = checkin.get("craving_level", 0)
        craving_score = craving * RISK_WEIGHTS["craving_level"]
        score += craving_score
        if craving >= 7:
            triggers.append(f"High craving level reported: {craving}/10")
        elif craving >= 4:
            triggers.append(f"Moderate craving detected: {craving}/10")

        # 2. Mood signals
        mood = checkin.get("mood", "neutral").lower()
        if mood == "depressed":
            score += RISK_WEIGHTS["mood_depressed"]
            triggers.append("Depressed mood detected — highest relapse risk state")
        elif mood == "craving":
            score += RISK_WEIGHTS["mood_craving"]
            triggers.append("User explicitly reporting craving state")
        elif mood == "stressed":
            score += RISK_WEIGHTS["mood_stressed"]
            triggers.append("Stress detected — common relapse trigger")

        # 3. Social isolation
        if checkin.get("social_isolation"):
            score += RISK_WEIGHTS["social_isolation"]
            triggers.append("Social isolation detected — reach out to support network")

        # 4. Sleep deprivation
        sleep = checkin.get("sleep_hours", 7)
        if sleep < 5:
            score += RISK_WEIGHTS["sleep_deprivation"]
            triggers.append(f"Severe sleep deprivation: only {sleep:.1f} hours")
        elif sleep < 6:
            score += RISK_WEIGHTS["sleep_deprivation"] // 2
            triggers.append(f"Low sleep hours: {sleep:.1f} hours")

        # 5. Physical inactivity
        if not checkin.get("physical_activity"):
            score += RISK_WEIGHTS["no_physical_activity"]
            triggers.append("No physical activity today — exercise is a key protective factor")

        # 6. Worsening trend (last 3 days of history)
        if len(history) >= 3:
            recent_moods = [h.get("mood", "neutral") for h in history[-3:]]
            bad_moods = {"depressed", "stressed", "craving"}
            if all(m in bad_moods for m in recent_moods):
                score += RISK_WEIGHTS["worsening_trend"]
                triggers.append("3-day worsening mood trend — intervention recommended")

        score = min(int(score), 100)
        level = self._level(score)

        return {
            "risk_score": score,
            "risk_level": level,
            "triggers": triggers,
            "recommendation": self._recommend(level, triggers),
            "motivational_message": self._motivate(level),
        }

    def compute_overall_risk(self, checkins: List[Dict]) -> Dict:
        """Monthly risk profile based on all check-ins."""
        if not checkins:
            return {"level": "LOW", "score": 0, "summary": "No check-ins yet."}

        scores = []
        for i, c in enumerate(checkins):
            history = checkins[:i]
            r = self.analyze(c, history)
            scores.append(r["risk_score"])

        avg_score = sum(scores) / len(scores)
        peak_score = max(scores)

        return {
            "level": self._level(int(avg_score)),
            "average_score": round(avg_score, 1),
            "peak_score": peak_score,
            "checkin_count": len(checkins),
            "high_risk_days": sum(1 for s in scores if s >= 70),
        }

    def _level(self, score: int) -> str:
        if score >= 85:
            return "CRITICAL"
        elif score >= 65:
            return "HIGH"
        elif score >= 35:
            return "MEDIUM"
        return "LOW"

    def _recommend(self, level: str, triggers: List[str]) -> str:
        if level == "CRITICAL":
            return (
                "🚨 Immediate support needed. Please call iCall India: 9152987821 "
                "or ask a trusted person to stay with you right now."
            )
        elif level == "HIGH":
            return (
                "⚠️ High relapse risk detected. Contact your support person, attend a meeting, "
                "or use the chat with Nova right now. You're not alone."
            )
        elif level == "MEDIUM":
            return (
                "Your signals suggest a challenging period. Try a coping technique, "
                "go for a walk, or talk to someone today."
            )
        return "You're doing well. Keep up your daily check-ins and healthy habits. 💚"

    def _motivate(self, level: str) -> str:
        import random
        messages = MOTIVATIONAL_MESSAGES.get(level, MOTIVATIONAL_MESSAGES["LOW"])
        return random.choice(messages)
