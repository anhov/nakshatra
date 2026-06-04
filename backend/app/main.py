from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    calendar_sync,
    chart,
    content,
    dasha,
    find_best_day,
    month,
    muhurta,
    notifications,
    panchanga,
    subscriptions,
    today,
    transits,
    users,
)

app = FastAPI(
    title="Nakshatra API",
    description="Vedic astrology calculations for the Nakshatra app.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(panchanga.router,      prefix=PREFIX)
app.include_router(chart.router,          prefix=PREFIX)
app.include_router(dasha.router,          prefix=PREFIX)
app.include_router(transits.router,       prefix=PREFIX)
app.include_router(muhurta.router,        prefix=PREFIX)
app.include_router(today.router,          prefix=PREFIX)
app.include_router(month.router,          prefix=PREFIX)
app.include_router(find_best_day.router,  prefix=PREFIX)
app.include_router(content.router,        prefix=PREFIX)
app.include_router(calendar_sync.router,  prefix=PREFIX)
app.include_router(notifications.router,  prefix=PREFIX)
app.include_router(subscriptions.router,  prefix=PREFIX)
app.include_router(users.router,          prefix=PREFIX)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.2.0"}
