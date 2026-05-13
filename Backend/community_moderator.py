"""
community_moderator.py
======================
AI moderation layer for community posts.
Detects harmful content, escalates crisis posts,
and scores sentiment to surface posts needing support.
"""

from typing import Dict


# Words/phrases that trigger blocking
BLOCK_KEYWORDS = [
    "how to get drugs", "where to buy", "dealer", "score drugs",
    "how to use safely for the first time", "best way to use",
]

# Crisis signals that escalate to a counselor
CRISIS_KEYWORDS = [
    "want to die", "end it all", "give up on everything",
    "no point anymore", "relapsed and feel hopeless",
    "can't stop", "going to use tonight", "last post",
]

# Positive/milestone signals
MILESTONE_KEYWORDS = [
    "days sober", "weeks clean", "months free", "milestone",
    "proud of myself", "made it", "thank you", "it gets better",
]


class CommunityModerator:

    def moderate(self, content: str, post_type: str) -> Dict:
        """
        Analyzes a post for:
          - Harmful/drug-enabling content → block
          - Crisis signals → escalate to counselor
          - Sentiment → tag for UI (hopeful / struggling / milestone)

        Returns a moderation result dict.
        """
        content_lower = content.lower()

        # 1. Hard block — drug-enabling content
        for kw in BLOCK_KEYWORDS:
            if kw in content_lower:
                return {
                    "blocked": True,
                    "reason": "Post contains content that may enable drug use.",
                    "support_message": (
                        "We understand things can feel overwhelming. "
                        "If you're struggling, please talk to Nova or call iCall: 9152987821."
                    ),
                    "sentiment": "harmful",
                    "escalate": False,
                }

        # 2. Crisis escalation
        is_crisis = (
            post_type == "cry_for_help" or
            any(kw in content_lower for kw in CRISIS_KEYWORDS)
        )

        # 3. Sentiment scoring
        sentiment = self._score_sentiment(content_lower)

        encouragement = self._get_encouragement(sentiment, post_type)

        return {
            "blocked": False,
            "reason": None,
            "sentiment": sentiment,
            "escalate": is_crisis,
            "encouragement": encouragement,
            "support_message": None,
        }

    def _score_sentiment(self, content: str) -> str:
        """Simple keyword-based sentiment classification."""
        if any(kw in content for kw in MILESTONE_KEYWORDS):
            return "milestone"
        crisis_count = sum(1 for kw in CRISIS_KEYWORDS if kw in content)
        if crisis_count >= 2:
            return "crisis"
        negative_words = ["hopeless", "failed", "relapsed", "can't", "worst", "hate myself", "ashamed"]
        positive_words = ["hope", "better", "grateful", "strength", "proud", "progress", "thank"]
        neg_score = sum(1 for w in negative_words if w in content)
        pos_score = sum(1 for w in positive_words if w in content)
        if pos_score > neg_score:
            return "hopeful"
        elif neg_score > pos_score:
            return "struggling"
        return "neutral"

    def _get_encouragement(self, sentiment: str, post_type: str) -> str:
        messages = {
            "milestone": "🎉 What an achievement! Your story gives others hope.",
            "hopeful":   "💚 Thank you for sharing your strength with this community.",
            "struggling": "💙 You're not alone in this. This community is here for you.",
            "crisis":    "💚 We hear you. Please reach out to Nova or call iCall: 9152987821.",
            "neutral":   "Thank you for sharing. Every voice in this community matters.",
        }
        return messages.get(sentiment, "Thank you for being part of this community. 💚")
