"""
APEX Risk API - FastAPI endpoints for risk management.

Exposes RiskGate, CircuitBreaker, and RiskParameters via REST API.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import apex modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from apex_risk import RiskGate, RiskParameters, CircuitBreaker

# Initialize FastAPI app
app = FastAPI(title="APEX Risk API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize risk components
risk_params = RiskParameters()
circuit_breaker = CircuitBreaker(risk_params)
risk_gate = RiskGate(risk_params, circuit_breaker)

# Pydantic models for request/response
class ApproveRequest(BaseModel):
    symbol: str
    side: str  # "buy" or "sell"
    confidence: float
    size: float
    signal_strength: float

class TripRequest(BaseModel):
    reason: str

class ApproveResponse(BaseModel):
    approved: bool
    reason: str
    adjusted_size: float
    risk_checks: Dict[str, Any]
    timestamp: str

class StatusResponse(BaseModel):
    circuit_breaker_open: bool
    trip_count: int
    max_drawdown_pct: float
    approval_history_count: int
    current_drawdown_pct: Optional[float] = None

@app.post("/risk/approve", response_model=ApproveResponse)
async def approve_trade(request: ApproveRequest):
    """
    Approve or reject a trading signal using RiskGate.
    
    Args:
        request: Trading signal with symbol, side, confidence, size, signal_strength
        
    Returns:
        Full risk_gate.approve() result with approval decision and reasoning
    """
    try:
        # Build signal dict for risk gate
        signal = {
            "symbol": request.symbol,
            "side": request.side,
            "confidence": request.confidence,
            "signal_strength": request.signal_strength,
            "timestamp": risk_params.__dict__.get("timestamp", "")
        }
        
        # Current exposure (simplified - in production would track actual positions)
        current_exposure = {
            request.symbol: 0.0,  # Would be actual exposure in production
            "total": 0.0
        }
        
        # Get approval from risk gate
        result = risk_gate.approve(signal, request.size, current_exposure)
        
        return ApproveResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk approval failed: {str(e)}")

@app.get("/risk/status", response_model=StatusResponse)
async def get_risk_status():
    """
    Get current risk status including circuit breaker state.
    
    Returns:
        Circuit breaker status, trip count, max drawdown, approval history count
    """
    try:
        current_drawdown = getattr(circuit_breaker, 'current_drawdown', None)
        if current_drawdown is not None:
            current_drawdown = float(current_drawdown)
        
        return StatusResponse(
            circuit_breaker_open=circuit_breaker.is_open,
            trip_count=len(circuit_breaker.trip_history),
            max_drawdown_pct=risk_params.max_drawdown_pct * 100,
            approval_history_count=len(risk_gate.approval_history),
            current_drawdown_pct=current_drawdown * 100 if current_drawdown is not None else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk status: {str(e)}")

@app.post("/risk/trip")
async def trip_circuit_breaker(request: TripRequest):
    """
    Manually trip the circuit breaker with a reason.
    
    Args:
        request: Reason for tripping the circuit breaker
        
    Returns:
        Success message
    """
    try:
        circuit_breaker.trip(request.reason)
        return {"success": True, "message": f"Circuit breaker tripped: {request.reason}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trip circuit breaker: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "APEX Risk API",
        "version": "1.0.0",
        "endpoints": {
            "POST /risk/approve": "Approve or reject trading signals",
            "GET /risk/status": "Get current risk status",
            "POST /risk/trip": "Manually trip circuit breaker"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
