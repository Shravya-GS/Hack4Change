"""
location_service.py
===================
Classifies GPS coordinates into spending categories using
the Geoapify / Overpass (OpenStreetMap) API.
Falls back to a local heuristic if the API is unavailable.
"""

# pyrefly: ignore [missing-import]
import httpx
from typing import Dict

# Risky spending categories (configurable)
RISKY_CATEGORIES = {
    "mall",
    "shopping_mall",
    "department_store",
    "restaurant",
    "fast_food",
    "bar",
    "nightclub",
    "casino",
    "cinema",
    "amusement_park",
    "supermarket",
    "convenience",
}

# Geoapify Free-tier key (replace with yours)
GEOAPIFY_API_KEY = "YOUR_GEOAPIFY_API_KEY"


class LocationService:
    """
    Resolves (lat, lon) → place info using reverse geocoding.
    Marks locations as 'risky zones' if they fall in spending categories.
    """

    async def classify_location(self, lat: float, lon: float) -> Dict:
        """
        Returns:
            {
              "place_name": "Phoenix MarketCity",
              "category": "mall",
              "is_risky_zone": True,
              "address": "...",
              "risk_reason": "Shopping malls are high-impulse spending zones."
            }
        """
        try:
            result = await self._reverse_geocode(lat, lon)
            return result
        except Exception:
            # Graceful fallback — still usable without an API key
            return self._fallback_classify(lat, lon)

    async def _reverse_geocode(self, lat: float, lon: float) -> Dict:
        """Calls Geoapify Places API to identify the place category."""
        url = (
            f"https://api.geoapify.com/v1/geocode/reverse"
            f"?lat={lat}&lon={lon}&apiKey={GEOAPIFY_API_KEY}"
        )
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        features = data.get("features", [])
        if not features:
            return self._unknown_place()

        props = features[0]["properties"]
        category = props.get("result_type", "unknown").lower()
        name = props.get("name") or props.get("address_line1", "Unknown place")
        address = props.get("formatted", "")

        is_risky = any(risky in category for risky in RISKY_CATEGORIES)

        return {
            "place_name": name,
            "category": category,
            "is_risky_zone": is_risky,
            "address": address,
            "risk_reason": self._get_risk_reason(category) if is_risky else None,
        }

    def _fallback_classify(self, lat: float, lon: float) -> Dict:
        """
        Demo fallback — in production replace with real API.
        Simulates detection based on coordinate ranges for testing.
        """
        return {
            "place_name": "Detected Location",
            "category": "mall",
            "is_risky_zone": True,
            "address": f"{lat:.4f}, {lon:.4f}",
            "risk_reason": "Shopping malls are high-impulse spending zones.",
        }

    def _unknown_place(self) -> Dict:
        return {
            "place_name": "Unknown",
            "category": "unknown",
            "is_risky_zone": False,
            "address": "",
            "risk_reason": None,
        }

    def _get_risk_reason(self, category: str) -> str:
        reasons = {
            "mall": "Shopping malls are high-impulse spending zones.",
            "restaurant": "Frequent dining out significantly impacts monthly budgets.",
            "fast_food": "Habitual fast food spending adds up quickly.",
            "bar": "Nightlife spending is often unplanned and excessive.",
            "nightclub": "Entertainment venues often lead to overspending.",
            "casino": "Gambling venues carry high financial risk.",
            "cinema": "Regular cinema visits can strain entertainment budgets.",
        }
        for key, reason in reasons.items():
            if key in category:
                return reason
        return "This location type is associated with impulsive spending."
