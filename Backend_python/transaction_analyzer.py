"""
transaction_analyzer.py
========================
Generates spending summaries and detects behavioral patterns.
"""

from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta


class TransactionAnalyzer:

    def generate_summary(self, user: Dict, transactions: List[Dict]) -> Dict:
        """Monthly spending summary by category."""
        if not transactions:
            return {"total_spent": 0, "by_category": {}, "top_category": None}

        total = sum(t["amount"] for t in transactions)
        by_category = defaultdict(float)
        for t in transactions:
            by_category[t.get("category", "other")] += t["amount"]

        top = max(by_category, key=by_category.get)
        budget = user.get("monthly_budget", 1)

        return {
            "total_spent": round(total, 2),
            "budget": budget,
            "remaining": round(budget - total, 2),
            "budget_used_pct": round(total / budget * 100, 1),
            "by_category": dict(by_category),
            "top_spending_category": top,
            "transaction_count": len(transactions),
        }

    def detect_patterns(self, transactions: List[Dict]) -> List[Dict]:
        """
        Detects behavioral patterns like:
        - Weekend splurge spikes
        - Late-night spending habits
        - Repeated same-merchant visits
        - Gradual budget creep
        """
        patterns = []
        if not transactions:
            return patterns

        # Pattern 1: Weekend overspending
        weekend_total = sum(
            t["amount"] for t in transactions
            if self._is_weekend(t.get("timestamp"))
        )
        weekday_total = sum(
            t["amount"] for t in transactions
            if not self._is_weekend(t.get("timestamp"))
        )
        if weekend_total > weekday_total * 1.5:
            patterns.append({
                "pattern": "Weekend Splurge",
                "description": "You spend significantly more on weekends.",
                "weekend_total": round(weekend_total, 2),
                "weekday_total": round(weekday_total, 2),
                "severity": "MEDIUM",
            })

        # Pattern 2: Late-night spending
        late_night = [
            t for t in transactions
            if self._is_late_night(t.get("timestamp"))
        ]
        if len(late_night) / max(len(transactions), 1) > 0.2:
            patterns.append({
                "pattern": "Late-Night Spending",
                "description": f"{len(late_night)} transactions made between 10 PM–2 AM.",
                "count": len(late_night),
                "severity": "HIGH",
            })

        # Pattern 3: Repeat merchant visits
        merchants = defaultdict(int)
        for t in transactions:
            merchants[t.get("merchant_name", "unknown")] += 1
        frequent = {m: c for m, c in merchants.items() if c >= 5}
        if frequent:
            top_merchant = max(frequent, key=frequent.get)
            patterns.append({
                "pattern": "Repeat Merchant Habit",
                "description": f"You've visited '{top_merchant}' {frequent[top_merchant]} times.",
                "merchant": top_merchant,
                "visits": frequent[top_merchant],
                "severity": "MEDIUM",
            })

        return patterns

    def _is_weekend(self, timestamp_str: str) -> bool:
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.weekday() >= 5  # Saturday=5, Sunday=6
        except Exception:
            return False

    def _is_late_night(self, timestamp_str: str) -> bool:
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.hour >= 22 or dt.hour <= 2
        except Exception:
            return False
