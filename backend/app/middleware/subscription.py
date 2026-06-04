"""
Subscription tier enforcement.

The mobile app passes the tier via the X-Subscription-Tier header.
In production this header would be validated against a signed JWT;
for MVP it is trusted on the honour system and will be replaced by
proper IAP receipt verification.

Tiers:
  free     — limited today screen, no calendar sync, no muhurta detail
  premium  — $7.99/mo — full features + calendar + notifications
  pro      — $19.99/mo — everything + raw chart data + multiple profiles
"""

from enum import Enum

from fastapi import Header, HTTPException


class Tier(str, Enum):
    FREE    = "free"
    PREMIUM = "premium"
    PRO     = "pro"


# Feature matrix ─────────────────────────────────────────────────────────────

FEATURE_TIERS: dict[str, Tier] = {
    # Today screen
    "today:full_activities":   Tier.PREMIUM,   # 4 activities (free gets 2)
    "today:timing_windows":    Tier.PREMIUM,   # best/avoid times
    "today:affirmation":       Tier.PREMIUM,
    # Dasha
    "dasha:antardasha":        Tier.PREMIUM,   # free sees MD only
    # Muhurta
    "muhurta:full":            Tier.PREMIUM,   # free sees Rahu Kala only
    # Calendar
    "calendar:sync":           Tier.PREMIUM,
    # Find Best Day
    "find_best_day:all_cats":  Tier.PREMIUM,   # free: 3 categories, 1 result
    "find_best_day:full":      Tier.PREMIUM,
    # Month view
    "month:scores":            Tier.PREMIUM,   # free: colours only, no scores
    # Mantras
    "content:mantras":         Tier.PREMIUM,
    # Notifications
    "notifications":           Tier.PREMIUM,
    # Raw chart data
    "chart:raw_data":          Tier.PRO,
    "multiple_profiles":       Tier.PRO,
}

TIER_RANK: dict[Tier, int] = {Tier.FREE: 0, Tier.PREMIUM: 1, Tier.PRO: 2}

UPGRADE_URL = "https://nakshatra.app/upgrade"


def get_tier(x_subscription_tier: str = Header(default="free")) -> Tier:
    """FastAPI dependency — reads tier from X-Subscription-Tier header."""
    try:
        return Tier(x_subscription_tier.lower())
    except ValueError:
        return Tier.FREE


def check_feature(tier: Tier, feature: str) -> bool:
    """Return True if the tier unlocks the feature."""
    required = FEATURE_TIERS.get(feature, Tier.FREE)
    return TIER_RANK[tier] >= TIER_RANK[required]


def require_premium(tier: Tier = None):
    """Raises 402 if tier is FREE."""
    if tier == Tier.FREE:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "premium_required",
                "message": "Upgrade to Premium to unlock this feature.",
                "upgrade_url": UPGRADE_URL,
            },
        )


def require_pro(tier: Tier = None):
    """Raises 402 if tier is not PRO."""
    if TIER_RANK.get(tier, 0) < TIER_RANK[Tier.PRO]:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "pro_required",
                "message": "Upgrade to Jyotishi Pro to unlock this feature.",
                "upgrade_url": UPGRADE_URL,
            },
        )


# Subscription metadata shown to clients ─────────────────────────────────────

PLANS = [
    {
        "id": "free",
        "name": "Free",
        "price": "$0",
        "period": None,
        "features": [
            "Daily score + tagline",
            "Basic panchanga",
            "Current life period (major only)",
            "Rahu Kala timing",
            "2 favourable activities per day",
        ],
        "limits": [
            "No calendar sync",
            "No full timing windows",
            "No affirmations or mantras",
            "Find Best Day: 3 categories, 1 result only",
        ],
    },
    {
        "id": "premium",
        "name": "Premium",
        "price": "$7.99",
        "period": "month",
        "features": [
            "Everything in Free",
            "All 4 favourable activities",
            "Full timing windows (Choghadiya, Hora, Abhijit)",
            "Full Dasha detail (MD + AD + progress)",
            "Month calendar with colour-coded scores",
            "Find Best Day — all 15 categories, top 3 results",
            "Google & Apple Calendar sync + event labelling",
            "Daily affirmation tied to your life period",
            "Planetary & nakshatra mantras with pronunciation",
            "Ekadashi notifications + morning daily reading",
        ],
        "limits": [],
    },
    {
        "id": "pro",
        "name": "Jyotishi Pro",
        "price": "$19.99",
        "period": "month",
        "features": [
            "Everything in Premium",
            "Raw astrological data (degrees, speeds, navamsha)",
            "Multiple birth profiles (family, clients)",
            "API access for practitioners",
        ],
        "limits": [],
    },
]
