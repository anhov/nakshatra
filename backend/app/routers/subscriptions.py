from fastapi import APIRouter, Depends
from app.middleware.subscription import PLANS, Tier, get_tier

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans")
def list_plans():
    """Return all subscription plans with feature descriptions."""
    return {"plans": PLANS}


@router.get("/my-tier")
def my_tier(tier: Tier = Depends(get_tier)):
    """Echo back the tier detected from the request header."""
    plan = next((p for p in PLANS if p["id"] == tier.value), PLANS[0])
    return {"tier": tier.value, "plan": plan}
