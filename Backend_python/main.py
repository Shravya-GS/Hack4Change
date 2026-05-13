"""
FinTech & Behavioral Intelligence Backend
==========================================
FastAPI backend with GPS tracking, risk detection, and smart alerts.
"""

# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, BackgroundTasks
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime

from location_service import LocationService
from risk_engine import RiskEngine
from alert_service import AlertService
from transaction_analyzer import TransactionAnalyzer
from database import Database

app = FastAPI(title="FinTech Behavioral Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database()
location_service = LocationService()
risk_engine = RiskEngine()
alert_service = AlertService()
transaction_analyzer = TransactionAnalyzer()

# ─── Models ───────────────────────────────────────────────────────────────────

class UserLocation(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    timestamp: Optional[str] = None

class Transaction(BaseModel):
    user_id: str
    amount: float
    category: str          # e.g. "restaurant", "mall", "entertainment"
    merchant_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    name: str
    monthly_income: float
    monthly_budget: float
    risk_tolerance: str    # "low" | "medium" | "high"

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/api/user/register")
async def register_user(profile: UserProfile):
    """Register a new user with their financial profile."""
    db.save_user(profile.dict())
    return {"status": "success", "message": f"User {profile.name} registered."}


@app.post("/api/location/update")
async def update_location(loc: UserLocation, background_tasks: BackgroundTasks):
    """
    Receive live GPS coordinates from the user's device.
    Checks if they're at a risky spending location and schedules a 5-min alert.
    """
    loc.timestamp = loc.timestamp or datetime.utcnow().isoformat()

    # Classify the place type from coordinates
    place_info = await location_service.classify_location(loc.latitude, loc.longitude)

    db.save_location(loc.user_id, loc.latitude, loc.longitude, place_info)

    if place_info["is_risky_zone"]:
        # Schedule alert after 5 minutes (non-blocking)
        background_tasks.add_task(
            alert_service.schedule_location_alert,
            user_id=loc.user_id,
            place_info=place_info,
            delay_seconds=300  # 5 minutes
        )
        return {
            "status": "risky_zone_detected",
            "place": place_info["place_name"],
            "category": place_info["category"],
            "alert_scheduled_in": "5 minutes"
        }

    return {"status": "ok", "place": place_info.get("place_name", "Unknown")}


@app.post("/api/transaction/add")
async def add_transaction(txn: Transaction):
    """
    Log a new transaction and get instant risk analysis.
    """
    txn.timestamp = txn.timestamp or datetime.utcnow().isoformat()

    # Get user profile and spending history
    user = db.get_user(txn.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = db.get_transactions(txn.user_id, last_n=50)

    # Run risk analysis
    risk_result = risk_engine.analyze_transaction(txn.dict(), user, history)

    db.save_transaction(txn.dict())

    # Fire alert if risk is HIGH
    if risk_result["risk_level"] == "HIGH":
        await alert_service.send_instant_alert(txn.user_id, risk_result)

    return {
        "status": "logged",
        "risk_level": risk_result["risk_level"],
        "risk_score": risk_result["risk_score"],
        "insights": risk_result["insights"],
        "recommendation": risk_result["recommendation"]
    }


@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """
    Returns full financial health dashboard for a user.
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = db.get_transactions(user_id, last_n=100)
    summary = transaction_analyzer.generate_summary(user, transactions)
    patterns = transaction_analyzer.detect_patterns(transactions)
    risk_profile = risk_engine.compute_overall_risk(user, transactions)

    return {
        "user": user,
        "summary": summary,
        "spending_patterns": patterns,
        "overall_risk": risk_profile,
        "recent_transactions": transactions[-10:]
    }


@app.get("/api/alerts/{user_id}")
async def get_alerts(user_id: str):
    """Fetch all alerts for a user."""
    alerts = db.get_alerts(user_id)
    return {"alerts": alerts, "count": len(alerts)}


@app.get("/api/health")
async def health_check():
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}
