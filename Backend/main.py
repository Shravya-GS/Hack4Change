"""
AI Drug-Free — Backend
=======================
FastAPI backend powering:
  1. De-addiction support & recovery tracking
  2. AI behavior-based risk detection
  3. Youth awareness & education
  4. AI chatbot for cravings & emotional support
  5. Personalized recovery plan generator
  6. Community + peer support with AI moderation
"""

# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, BackgroundTasks
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import Database
from ai_chatbot import AIChatbot
from risk_detector import RiskDetector
from recovery_planner import RecoveryPlanner
from community_moderator import CommunityModerator
from awareness_engine import AwarenessEngine

app = FastAPI(
    title="AI Drug-Free API",
    description="AI-powered de-addiction, risk detection, and recovery support platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Service Initialization ────────────────────────────────────────────────────
db = Database()
chatbot = AIChatbot()
risk_detector = RiskDetector()
recovery_planner = RecoveryPlanner()
moderator = CommunityModerator()
awareness = AwarenessEngine()


# ── Request / Response Models ─────────────────────────────────────────────────

class UserRegister(BaseModel):
    user_id: str
    name: str
    age: int
    substance_type: str          # e.g. "alcohol", "cannabis", "opioids", "tobacco"
    usage_duration_months: int
    motivation: str              # e.g. "family", "health", "career"
    support_network: bool        # Does the user have people around them?

class CheckIn(BaseModel):
    user_id: str
    mood: str                    # "good" | "neutral" | "stressed" | "depressed" | "craving"
    craving_level: int           # 1–10
    sleep_hours: float
    social_isolation: bool
    physical_activity: bool
    notes: Optional[str] = None

class ChatMessage(BaseModel):
    user_id: str
    message: str
    conversation_history: Optional[List[dict]] = []

class CommunityPost(BaseModel):
    user_id: str
    username: str                # anonymous alias encouraged
    content: str
    post_type: str               # "story" | "question" | "milestone" | "cry_for_help"

class AwarenessRequest(BaseModel):
    topic: str                   # "effects", "withdrawal", "stories", "quiz"
    age_group: str               # "teen" | "young_adult" | "adult"
    substance: Optional[str] = None


# ── 1. USER REGISTRATION & PROFILE ───────────────────────────────────────────

@app.post("/api/user/register", tags=["User"])
async def register_user(user: UserRegister):
    """Register a new user and generate their initial recovery plan."""
    db.save_user(user.dict())
    plan = recovery_planner.generate_plan(user.dict())
    db.save_recovery_plan(user.user_id, plan)
    return {
        "status": "registered",
        "message": f"Welcome, {user.name}. Your recovery journey starts today. 💚",
        "recovery_plan": plan,
    }


@app.get("/api/user/{user_id}/dashboard", tags=["User"])
async def get_dashboard(user_id: str):
    """Full recovery dashboard — streak, risk level, plan progress, recent alerts."""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    checkins = db.get_checkins(user_id, last_n=30)
    plan = db.get_recovery_plan(user_id)
    alerts = db.get_alerts(user_id)
    streak = db.get_streak(user_id)
    risk = risk_detector.compute_overall_risk(checkins)

    return {
        "user": user,
        "sober_streak_days": streak,
        "overall_risk": risk,
        "recovery_plan": plan,
        "recent_alerts": alerts[-5:],
        "checkin_count": len(checkins),
    }


# ── 2. DAILY CHECK-IN & RISK DETECTION ───────────────────────────────────────

@app.post("/api/checkin", tags=["Risk Detection"])
async def daily_checkin(checkin: CheckIn, background_tasks: BackgroundTasks):
    """
    Daily mood/behavior check-in.
    AI detects relapse risk from patterns and triggers alerts if needed.
    """
    checkin_data = checkin.dict()
    checkin_data["timestamp"] = datetime.utcnow().isoformat()
    db.save_checkin(checkin.user_id, checkin_data)

    # Update sober streak
    db.update_streak(checkin.user_id, checkin.mood)

    # Run risk detection
    history = db.get_checkins(checkin.user_id, last_n=14)
    risk_result = risk_detector.analyze(checkin_data, history)

    # If high risk — fire background alert + suggest professional help
    if risk_result["risk_level"] in ("HIGH", "CRITICAL"):
        background_tasks.add_task(
            _handle_high_risk, checkin.user_id, risk_result
        )

    return {
        "status": "logged",
        "risk_level": risk_result["risk_level"],
        "risk_score": risk_result["risk_score"],
        "triggers_detected": risk_result["triggers"],
        "recommendation": risk_result["recommendation"],
        "motivational_message": risk_result["motivational_message"],
    }


async def _handle_high_risk(user_id: str, risk_result: dict):
    """Background task: save alert + notify support contact if configured."""
    alert = {
        "type": "RELAPSE_RISK",
        "severity": risk_result["risk_level"],
        "title": "⚠️ High relapse risk detected",
        "message": risk_result["recommendation"],
        "timestamp": datetime.utcnow().isoformat(),
    }
    db.save_alert(user_id, alert)
    # TODO: send push notification / SMS via Twilio to emergency contact
    print(f"[HIGH RISK ALERT → {user_id}] {alert['message']}")


# ── 4. RECOVERY PLAN ──────────────────────────────────────────────────────────

@app.get("/api/recovery-plan/{user_id}", tags=["Recovery Plan"])
async def get_recovery_plan(user_id: str):
    """Fetch the user's personalized recovery plan."""
    plan = db.get_recovery_plan(user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No plan found. Please register first.")
    return {"plan": plan}


@app.post("/api/recovery-plan/{user_id}/regenerate", tags=["Recovery Plan"])
async def regenerate_plan(user_id: str):
    """Re-generate recovery plan based on latest check-in data."""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    checkins = db.get_checkins(user_id, last_n=30)
    plan = recovery_planner.generate_plan(user, checkins)
    db.save_recovery_plan(user_id, plan)
    return {"status": "updated", "plan": plan}


# ── 5. COMMUNITY & PEER SUPPORT ───────────────────────────────────────────────

@app.post("/api/community/post", tags=["Community"])
async def create_post(post: CommunityPost):
    """
    Submit a community post. AI moderates for harmful content
    and escalates 'cry_for_help' posts to counselors.
    """
    moderation = moderator.moderate(post.content, post.post_type)

    if moderation["blocked"]:
        return {
            "status": "blocked",
            "reason": moderation["reason"],
            "support_message": moderation["support_message"],
        }

    post_data = post.dict()
    post_data["timestamp"] = datetime.utcnow().isoformat()
    post_data["sentiment"] = moderation["sentiment"]
    post_data["flagged_for_counselor"] = moderation["escalate"]

    db.save_post(post_data)

    if moderation["escalate"]:
        # TODO: notify on-call counselor
        print(f"[COUNSELOR ESCALATION] Post by {post.user_id} flagged.")

    return {
        "status": "posted",
        "post_id": post_data.get("post_id", "new"),
        "sentiment": moderation["sentiment"],
        "message": moderation.get("encouragement", "Your story matters. 💚"),
    }


@app.get("/api/community/feed", tags=["Community"])
async def get_feed(limit: int = 20):
    """Fetch recent community posts (non-blocked, anonymized)."""
    posts = db.get_posts(limit=limit)
    return {"posts": posts, "count": len(posts)}


# ── 6. AWARENESS & EDUCATION ──────────────────────────────────────────────────

@app.post("/api/awareness", tags=["Awareness"])
async def get_awareness_content(req: AwarenessRequest):
    """
    Returns age-appropriate awareness content:
    drug effects, withdrawal timelines, real stories, or quizzes.
    """
    content = awareness.get_content(req.topic, req.age_group, req.substance)
    return {"content": content}


@app.get("/api/awareness/quiz/{age_group}", tags=["Awareness"])
async def get_quiz(age_group: str):
    """Returns an age-appropriate anti-drug awareness quiz."""
    quiz = awareness.get_quiz(age_group)
    return {"quiz": quiz}


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}
