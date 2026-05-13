"""
database.py
===========
In-memory store for the AI Drug-Free backend.
Replace with PostgreSQL + SQLAlchemy for production.
"""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import uuid


class Database:

    def __init__(self):
        self._users: Dict[str, Dict] = {}
        self._checkins: Dict[str, List] = defaultdict(list)
        self._recovery_plans: Dict[str, Dict] = {}
        self._alerts: Dict[str, List] = defaultdict(list)
        self._chats: Dict[str, List] = defaultdict(list)
        self._posts: List[Dict] = []
        self._streaks: Dict[str, int] = defaultdict(int)

    # ── Users ──────────────────────────────────────────────────────────────

    def save_user(self, user: Dict):
        self._users[user["user_id"]] = user

    def get_user(self, user_id: str) -> Optional[Dict]:
        return self._users.get(user_id)

    # ── Check-ins ──────────────────────────────────────────────────────────

    def save_checkin(self, user_id: str, checkin: Dict):
        self._checkins[user_id].append(checkin)

    def get_checkins(self, user_id: str, last_n: int = 30) -> List[Dict]:
        return self._checkins[user_id][-last_n:]

    # ── Streak Tracking ────────────────────────────────────────────────────

    def update_streak(self, user_id: str, mood: str):
        """
        Increment streak for a clean day.
        Reset if mood signals relapse ('used_today').
        """
        if mood == "used_today":
            self._streaks[user_id] = 0
        else:
            self._streaks[user_id] += 1

    def get_streak(self, user_id: str) -> int:
        return self._streaks.get(user_id, 0)

    # ── Recovery Plans ─────────────────────────────────────────────────────

    def save_recovery_plan(self, user_id: str, plan: Dict):
        self._recovery_plans[user_id] = plan

    def get_recovery_plan(self, user_id: str) -> Optional[Dict]:
        return self._recovery_plans.get(user_id)

    # ── Alerts ─────────────────────────────────────────────────────────────

    def save_alert(self, user_id: str, alert: Dict):
        self._alerts[user_id].append(alert)

    def get_alerts(self, user_id: str) -> List[Dict]:
        return self._alerts[user_id]

    # ── Chat History ────────────────────────────────────────────────────────

    def save_chat(self, user_id: str, message: Dict):
        self._chats[user_id].append(message)

    def get_chat_history(self, user_id: str, last_n: int = 20) -> List[Dict]:
        return self._chats[user_id][-last_n:]

    # ── Community Posts ─────────────────────────────────────────────────────

    def save_post(self, post: Dict):
        post["post_id"] = str(uuid.uuid4())[:8]
        self._posts.append(post)

    def get_posts(self, limit: int = 20) -> List[Dict]:
        # Return only non-blocked, reverse chron
        visible = [p for p in self._posts if not p.get("blocked")]
        return visible[-limit:][::-1]
