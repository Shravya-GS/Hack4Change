"""
alert_service.py
================
Handles all alert logic:
  - 5-minute delayed GPS-based spending warnings
  - Instant transaction risk alerts
  - (Optional) Push notification / FCM integration stub
"""

import asyncio
from datetime import datetime
from typing import Dict
from database import Database

db = Database()


class AlertService:
    """
    Sends alerts to users via in-app notifications.
    Plug in Firebase FCM / Twilio SMS / email for production.
    """

    async def schedule_location_alert(
        self, user_id: str, place_info: Dict, delay_seconds: int = 300
    ):
        """
        Waits `delay_seconds` (default: 5 mins), then checks if user
        is still at the risky location before firing the alert.
        This avoids alerting someone who just passed through.
        """
        await asyncio.sleep(delay_seconds)

        # Re-check: is the user still at this location type?
        last_location = db.get_last_location(user_id)
        if last_location and last_location.get("category") == place_info.get("category"):
            alert = self._build_location_alert(user_id, place_info)
            db.save_alert(user_id, alert)
            await self._dispatch(user_id, alert)
        # If they've left, no alert needed.

    async def send_instant_alert(self, user_id: str, risk_result: Dict):
        """Fires immediately for HIGH-risk transactions."""
        alert = {
            "type": "TRANSACTION_RISK",
            "severity": risk_result["risk_level"],
            "title": "⚠️ High-Risk Transaction Detected",
            "message": risk_result["recommendation"],
            "insights": risk_result["insights"],
            "timestamp": datetime.utcnow().isoformat(),
        }
        db.save_alert(user_id, alert)
        await self._dispatch(user_id, alert)

    def _build_location_alert(self, user_id: str, place_info: Dict) -> Dict:
        place = place_info.get("place_name", "this location")
        reason = place_info.get("risk_reason", "This is a high-spending zone.")
        return {
            "type": "LOCATION_RISK",
            "severity": "HIGH",
            "title": f"📍 You've been at {place} for 5 minutes",
            "message": (
                f"{reason} "
                "Check your budget before spending here."
            ),
            "place_info": place_info,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _dispatch(self, user_id: str, alert: Dict):
        """
        Dispatch layer — swap in real push notifications here.

        Options:
          - Firebase FCM:  send via google-auth + FCM REST API
          - Twilio SMS:    client.messages.create(...)
          - WebSocket:     broadcast to connected frontend clients
        """
        # For now: prints to server log (replace with real dispatch)
        print(
            f"\n[ALERT → {user_id}] {alert['title']}\n"
            f"  {alert['message']}\n"
            f"  Severity: {alert['severity']} | Time: {alert['timestamp']}\n"
        )
        # TODO: await fcm_client.send(user_id, alert)
