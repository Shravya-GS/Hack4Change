"""
database.py
===========
In-memory store for demo purposes.
Swap with SQLite (dev) or PostgreSQL/Supabase (production).
"""

from typing import Dict, List, Optional
from collections import defaultdict


class Database:
    """
    Simple in-memory database.
    Replace with:
      - SQLite:     sqlite3 / SQLAlchemy for local dev
      - PostgreSQL: asyncpg + SQLAlchemy for production
      - Firebase:   Firestore for mobile-first deployments
    """

    def __init__(self):
        self._users: Dict[str, Dict] = {}
        self._transactions: Dict[str, List] = defaultdict(list)
        self._locations: Dict[str, List] = defaultdict(list)
        self._alerts: Dict[str, List] = defaultdict(list)

    # ── Users ──────────────────────────────────────────────────────────────

    def save_user(self, user: Dict):
        self._users[user["user_id"]] = user

    def get_user(self, user_id: str) -> Optional[Dict]:
        return self._users.get(user_id)

    # ── Transactions ────────────────────────────────────────────────────────

    def save_transaction(self, txn: Dict):
        self._transactions[txn["user_id"]].append(txn)

    def get_transactions(self, user_id: str, last_n: int = 50) -> List[Dict]:
        return self._transactions[user_id][-last_n:]

    # ── Locations ───────────────────────────────────────────────────────────

    def save_location(self, user_id: str, lat: float, lon: float, place_info: Dict):
        entry = {"lat": lat, "lon": lon, **place_info}
        self._locations[user_id].append(entry)

    def get_last_location(self, user_id: str) -> Optional[Dict]:
        locs = self._locations[user_id]
        return locs[-1] if locs else None

    # ── Alerts ──────────────────────────────────────────────────────────────

    def save_alert(self, user_id: str, alert: Dict):
        self._alerts[user_id].append(alert)

    def get_alerts(self, user_id: str) -> List[Dict]:
        return self._alerts[user_id]
