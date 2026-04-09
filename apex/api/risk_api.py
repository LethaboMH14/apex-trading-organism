from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI(title="APEX Risk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

circuit_breaker_tripped = False
trip_count = 0
approval_history = []

class TradeRequest(BaseModel):
    symbol: str
    side: str
    confidence: float
    size: float
    signal_strength: float

@app.post("/risk/approve")
def approve_trade(trade: TradeRequest):
    global approval_history
    approved = not circuit_breaker_tripped and trade.confidence > 0.6 and trade.size <= 1.0
    result = {
        "approved": approved,
        "symbol": trade.symbol,
        "side": trade.side,
        "confidence": trade.confidence,
        "reason": "approved" if approved else "circuit breaker tripped or low confidence",
        "timestamp": datetime.utcnow().isoformat()
    }
    approval_history.append(result)
    return result

@app.get("/risk/status")
def get_status():
    return {
        "circuit_breaker_open": circuit_breaker_tripped,
        "trip_count": trip_count,
        "max_drawdown_pct": 2.3,
        "approval_history_count": len(approval_history)
    }

@app.post("/risk/trip")
def trip_breaker(reason: str = "manual"):
    global circuit_breaker_tripped, trip_count
    circuit_breaker_tripped = True
    trip_count += 1
    return {"tripped": True, "reason": reason, "trip_count": trip_count}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3002)
