"""
risk_engine.py
==============
Core AI/rule-based engine that computes risk scores for transactions
and overall spending profiles.
"""

from typing import Dict, List
from datetime import datetime, timedelta


# Risk thresholds (tunable)
CATEGORY_RISK_WEIGHTS = {
    "restaurant": 1.5,
    "mall": 2.0,
    "entertainment": 1.8,
    "fast_food": 1.3,
    "casino": 3.0,
    "bar": 1.7,
    "grocery": 0.8,
    "utility": 0.3,
    "transport": 0.5,
    "medical": 0.2,
    "education": 0.1,
}


class RiskEngine:
    """
    Analyzes individual transactions AND overall spending behavior
    to generate a risk score (0–100) and actionable recommendations.
    """

    def analyze_transaction(
        self, txn: Dict, user: Dict, history: List[Dict]
    ) -> Dict:
        """
        Scores a single transaction considering:
          - Amount vs monthly budget
          - Category risk weight
          - Frequency of similar transactions
          - Time-of-day (late-night = higher risk)
          - Velocity (multiple txns in short window)
        """
        score = 0
        insights = []

        budget = user.get("monthly_budget", 1)
        amount = txn["amount"]
        category = txn.get("category", "unknown").lower()

        # 1. Amount relative to budget
        budget_ratio = amount / budget
        if budget_ratio > 0.3:
            score += 40
            insights.append(
                f"This single transaction is {budget_ratio:.0%} of your monthly budget."
            )
        elif budget_ratio > 0.1:
            score += 20
            insights.append("Transaction is 10–30% of your monthly budget.")

        # 2. Category risk
        cat_weight = CATEGORY_RISK_WEIGHTS.get(category, 1.0)
        score += int(cat_weight * 10)
        if cat_weight >= 1.5:
            insights.append(
                f"'{category.capitalize()}' spending is flagged as a high-risk category."
            )

        # 3. Frequency in last 7 days
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        same_cat_recent = [
            t for t in history
            if t.get("category") == category and t.get("timestamp", "") >= week_ago
        ]
        if len(same_cat_recent) >= 5:
            score += 20
            insights.append(
                f"You've made {len(same_cat_recent)} '{category}' transactions this week — "
                "high frequency pattern detected."
            )

        # 4. Time-of-day risk (10 PM – 2 AM = impulsive window)
        hour = datetime.utcnow().hour
        if 22 <= hour or hour <= 2:
            score += 10
            insights.append("Late-night transactions have higher impulse-spending risk.")

        # 5. Velocity — multiple txns in last 30 minutes
        thirty_min_ago = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        recent_any = [
            t for t in history if t.get("timestamp", "") >= thirty_min_ago
        ]
        if len(recent_any) >= 3:
            score += 15
            insights.append(
                "Multiple transactions detected in the last 30 minutes — spending spike alert."
            )

        score = min(score, 100)

        return {
            "risk_score": score,
            "risk_level": self._level(score),
            "insights": insights,
            "recommendation": self._recommend(score, category, amount),
        }

    def compute_overall_risk(self, user: Dict, transactions: List[Dict]) -> Dict:
        """
        Computes a monthly risk profile from all transactions.
        """
        if not transactions:
            return {"overall_risk": "LOW", "score": 0, "summary": "No transactions yet."}

        total_spent = sum(t["amount"] for t in transactions)
        budget = user.get("monthly_budget", 1)
        budget_utilization = total_spent / budget

        risky_categories = [
            t for t in transactions
            if CATEGORY_RISK_WEIGHTS.get(t.get("category", ""), 1.0) >= 1.5
        ]
        risky_ratio = len(risky_categories) / len(transactions)

        score = 0
        if budget_utilization > 1.0:
            score += 50
        elif budget_utilization > 0.8:
            score += 30
        elif budget_utilization > 0.6:
            score += 15

        score += int(risky_ratio * 50)
        score = min(score, 100)

        return {
            "overall_risk": self._level(score),
            "score": score,
            "budget_utilization": f"{budget_utilization:.0%}",
            "risky_transaction_ratio": f"{risky_ratio:.0%}",
            "total_spent": total_spent,
            "budget": budget,
        }

    def _level(self, score: int) -> str:
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        return "LOW"

    def _recommend(self, score: int, category: str, amount: float) -> str:
        if score >= 70:
            return (
                f"⚠️ High risk detected. Consider delaying this {category} purchase "
                f"of ₹{amount:.0f} and reviewing your monthly budget."
            )
        elif score >= 40:
            return (
                f"Consider setting a {category} spending limit. "
                "Small cutbacks add up over the month."
            )
        return "Transaction looks within healthy spending bounds. Keep it up! ✅"
