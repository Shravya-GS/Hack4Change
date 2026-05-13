"""
recovery_planner.py
===================
Generates personalized, phased recovery plans based on:
  - Substance type and usage duration
  - User motivation and support network
  - Behavioral check-in history
"""

from typing import Dict, List, Optional


# Evidence-based recovery phases
RECOVERY_PHASES = {
    "week1_2": "Stabilization — managing withdrawal, building safety",
    "week3_4": "Early Recovery — establishing new routines",
    "month2_3": "Active Recovery — behavioral change & coping skills",
    "month4_6": "Consolidation — strengthening identity & relationships",
    "month6+":  "Maintenance — sustaining long-term sobriety",
}

# Substance-specific guidance
SUBSTANCE_TIPS = {
    "alcohol": {
        "withdrawal_warning": "Alcohol withdrawal can be medically dangerous. Please consult a doctor before stopping.",
        "key_triggers": ["social events", "stress", "loneliness", "sleep issues"],
        "coping_strategies": ["HALT check (Hungry/Angry/Lonely/Tired)", "alcohol-free social alternatives", "AA meetings"],
    },
    "cannabis": {
        "withdrawal_warning": "Cannabis withdrawal includes irritability and sleep issues — these are temporary.",
        "key_triggers": ["boredom", "social settings", "stress", "habit cues"],
        "coping_strategies": ["exercise", "new hobbies", "mindfulness", "journaling"],
    },
    "opioids": {
        "withdrawal_warning": "Opioid withdrawal is intensely uncomfortable. Medical supervision (MAT) is strongly recommended.",
        "key_triggers": ["pain", "cravings", "emotional distress", "old contacts"],
        "coping_strategies": ["MAT (methadone/buprenorphine)", "NA meetings", "therapy", "removing old triggers"],
    },
    "tobacco": {
        "withdrawal_warning": "Nicotine withdrawal peaks at 2–3 days. NRT (patches/gum) can help significantly.",
        "key_triggers": ["stress", "after meals", "coffee", "social smoking"],
        "coping_strategies": ["NRT", "deep breathing", "delay tactic (wait 10 mins)", "hydration"],
    },
    "stimulants": {
        "withdrawal_warning": "Stimulant withdrawal causes fatigue and depression — this improves with time.",
        "key_triggers": ["energy crashes", "social environments", "work stress"],
        "coping_strategies": ["sleep regulation", "nutrition", "therapy", "exercise"],
    },
}

DEFAULT_SUBSTANCE = {
    "withdrawal_warning": "Please consult a healthcare professional for withdrawal guidance.",
    "key_triggers": ["stress", "social pressure", "emotional pain"],
    "coping_strategies": ["mindfulness", "support groups", "therapy", "exercise"],
}


class RecoveryPlanner:

    def generate_plan(
        self,
        user: Dict,
        checkin_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generates a full personalized recovery plan.
        """
        substance = user.get("substance_type", "unknown").lower()
        duration = user.get("usage_duration_months", 6)
        motivation = user.get("motivation", "a better life")
        has_support = user.get("support_network", False)
        name = user.get("name", "Friend")

        substance_info = SUBSTANCE_TIPS.get(substance, DEFAULT_SUBSTANCE)

        # Determine intensity based on usage duration
        intensity = self._get_intensity(duration)

        weekly_goals = self._build_weekly_goals(substance, intensity, has_support)
        daily_habits = self._build_daily_habits(substance)
        milestones = self._build_milestones()

        return {
            "plan_title": f"{name}'s Personalized Recovery Plan",
            "substance": substance,
            "intensity": intensity,
            "motivation_anchor": motivation,
            "medical_advisory": substance_info["withdrawal_warning"],
            "key_triggers_to_watch": substance_info["key_triggers"],
            "recommended_coping_strategies": substance_info["coping_strategies"],
            "phases": RECOVERY_PHASES,
            "weekly_goals": weekly_goals,
            "daily_habits": daily_habits,
            "milestones": milestones,
            "support_resources": self._get_resources(has_support),
            "emergency_contacts": [
                {"name": "iCall India", "number": "9152987821"},
                {"name": "Vandrevala Foundation", "number": "1860-2662-345"},
                {"name": "NIMHANS", "number": "080-46110007"},
            ],
        }

    def _get_intensity(self, duration_months: int) -> str:
        if duration_months <= 3:
            return "mild"
        elif duration_months <= 12:
            return "moderate"
        return "intensive"

    def _build_weekly_goals(self, substance: str, intensity: str, has_support: bool) -> List[Dict]:
        base_goals = [
            {"week": 1, "goal": "Complete daily check-ins. Identify your top 3 personal triggers.", "focus": "Awareness"},
            {"week": 2, "goal": "Practice one coping technique daily. Avoid high-risk situations.", "focus": "Coping Skills"},
            {"week": 3, "goal": "Establish a healthy morning routine (sleep, nutrition, movement).", "focus": "Lifestyle"},
            {"week": 4, "goal": "Connect with one supportive person this week. Share your goal.", "focus": "Social Support"},
        ]
        if not has_support:
            base_goals[3]["goal"] = "Join an online support group or community forum this week."
        return base_goals

    def _build_daily_habits(self, substance: str) -> List[str]:
        return [
            "☀️ Morning: Set a daily intention — 'Today I choose my future.'",
            "🏃 Exercise: 20–30 mins of any physical activity (walk, yoga, gym)",
            "🥗 Nutrition: Eat regular meals — blood sugar affects cravings",
            "💧 Hydration: Drink 8+ glasses of water — helps with withdrawal symptoms",
            "📓 Journal: Write 3 things you're grateful for each evening",
            "😴 Sleep: Aim for 7–8 hours — poor sleep is a top relapse trigger",
            "📱 Check-in: Open the app and log your daily mood",
            "🧘 Wind-down: 5 mins of deep breathing before bed",
        ]

    def _build_milestones(self) -> List[Dict]:
        return [
            {"days": 1,   "badge": "🌱 First Step",      "message": "Day 1 done. That took real courage."},
            {"days": 3,   "badge": "🔥 Three Days",       "message": "The hardest part is often the first 3 days. You made it!"},
            {"days": 7,   "badge": "⭐ One Week",         "message": "One full week! Your brain is already beginning to heal."},
            {"days": 14,  "badge": "💪 Two Weeks",        "message": "Two weeks of fighting for yourself. Incredible."},
            {"days": 30,  "badge": "🥇 One Month",        "message": "30 days! This is where real change takes root."},
            {"days": 90,  "badge": "💎 Three Months",     "message": "90 days — the foundation of lasting recovery."},
            {"days": 180, "badge": "🚀 Six Months",       "message": "Half a year of choosing yourself every single day."},
            {"days": 365, "badge": "👑 One Full Year",    "message": "365 days. You rebuilt your life. Never forget this day."},
        ]

    def _get_resources(self, has_support: bool) -> List[Dict]:
        resources = [
            {"type": "App Feature", "name": "Nova AI Chat", "description": "Talk to your AI companion anytime"},
            {"type": "App Feature", "name": "Daily Check-In", "description": "Track mood and get risk alerts"},
            {"type": "App Feature", "name": "Community", "description": "Peer stories and support"},
            {"type": "External", "name": "iCall India", "description": "Free counseling: 9152987821"},
            {"type": "External", "name": "NA India", "description": "Narcotics Anonymous: na-india.org"},
            {"type": "External", "name": "AA India", "description": "Alcoholics Anonymous: alcoholics-anonymous.in"},
        ]
        if not has_support:
            resources.append({
                "type": "External",
                "name": "Online Community",
                "description": "r/StopDrinking, r/Drugs (harm reduction) — peer support 24/7"
            })
        return resources
