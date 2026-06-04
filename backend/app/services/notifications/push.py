"""
Push notification sender via Expo Push API.

Expo's service handles both APNs (iOS) and FCM (Android) so we only need
one endpoint. For production, swap this for direct APNs/FCM if needed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


@dataclass
class PushMessage:
    to: str                        # Expo push token "ExponentPushToken[...]"
    title: str
    body: str
    data: dict = field(default_factory=dict)
    sound: str = "default"
    badge: int | None = None


async def send_push(msg: PushMessage) -> bool:
    """Send a single push notification. Returns True on success."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(
                EXPO_PUSH_URL,
                json={
                    "to":    msg.to,
                    "title": msg.title,
                    "body":  msg.body,
                    "data":  msg.data,
                    "sound": msg.sound,
                    **({"badge": msg.badge} if msg.badge is not None else {}),
                },
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
            if res.status_code == 200:
                result = res.json()
                status = result.get("data", {}).get("status")
                if status == "error":
                    logger.warning("Push delivery error: %s", result)
                    return False
                return True
            logger.error("Push API HTTP %s: %s", res.status_code, res.text[:200])
            return False
    except Exception as exc:
        logger.error("Push send failed: %s", exc)
        return False


async def send_morning_reading(token: str, score: float, quality: str, nakshatra: str) -> bool:
    """Send the daily morning reading notification."""
    return await send_push(PushMessage(
        to=token,
        title=f"Your day: {score}/10 · {quality}",
        body=f"Moon in {nakshatra}. Tap to see your full reading.",
        data={"screen": "Today"},
    ))


async def send_ekadashi_eve(token: str, ekadashi_name: str, meaning: str) -> bool:
    """Send an eve-of-Ekadashi notification."""
    return await send_push(PushMessage(
        to=token,
        title=f"Tomorrow is {ekadashi_name}",
        body=f"{meaning[:80]}… Tap to prepare.",
        data={"screen": "Today"},
    ))


async def send_dasha_change(token: str, new_dasha: str, end_date: str) -> bool:
    """Notify when a Maha Dasha period changes."""
    return await send_push(PushMessage(
        to=token,
        title=f"{new_dasha} period has begun",
        body=f"A new chapter in your life journey. This period runs until {end_date}.",
        data={"screen": "MyChart"},
    ))
