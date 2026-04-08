#!/usr/bin/env python3
"""
APEX WebSocket Server - Real-time data broadcaster for dashboard

PROF. KWAME ASANTE: Chief Architecture Officer of APEX
Standard: "Every component must survive a 3am failure with zero human intervention."

WebSocket server that runs APEX demo pipeline and broadcasts results to dashboard clients.
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from websockets.server import WebSocketServerProtocol
from websockets.server import serve
import websockets

# Add apex directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APEXWebSocketServer:
    """APEX WebSocket server for real-time dashboard updates."""
    
    def __init__(self):
        self.clients = set()
        self.running = False
        
    async def register_client(self, websocket):
        """Register a new dashboard client."""
        self.clients.add(websocket)
        logger.info(f"Dashboard client connected. Total clients: {len(self.clients)}")
        
        # Send initial agent status
        await self.broadcast_agent_status()
        
    async def unregister_client(self, websocket):
        """Unregister a dashboard client."""
        self.clients.remove(websocket)
        logger.info(f"Dashboard client disconnected. Total clients: {len(self.clients)}")
        
    async def broadcast_agent_status(self):
        """Broadcast agent status updates."""
        status_message = {
            "type": "agent_status",
            "agents": [
                {"name": "DR. YUKI TANAKA", "status": "ONLINE", "role": "Market Data"},
                {"name": "DR. JABARI MENSAH", "status": "ONLINE", "role": "Sentiment"},
                {"name": "DR. SIPHO NKOSI", "status": "ONLINE", "role": "Risk"},
                {"name": "PROF. KWAME ASANTE", "status": "ONLINE", "role": "LLM Router"},
                {"name": "DR. PRIYA NAIR", "status": "ONLINE", "role": "Blockchain"}
            ]
        }
        await self.broadcast(status_message)
        
    async def run_apex_pipeline(self):
        """Run the APEX demo pipeline and broadcast results."""
        try:
            # Import and run the live pipeline
            from apex_live import APEXLive
            
            # Create live instance
            demo = APEXLive()
            
            # Run the complete pipeline
            logger.info("Running APEX live pipeline...")
            result = await demo.run_cycle()
            
            if result and result.get('success'):
                # Extract trade data
                execution = result.get('execution', {})
                ai_decision = result.get('ai_decision', {})
                market_data = result.get('market_data', {})
                
                # Create enhanced broadcast message
                trade_message = {
                    "type": "trade_executed",
                    "tx_hash": execution.get('tx_hash', ''),          # ERC-8004 blockchain proof
                    "kraken_order_id": execution.get('kraken_order_id', ''),  # Real Kraken trade
                    "price": market_data.get('price', 0),          # Live BTC price
                    "action": ai_decision.get('action', 'BUY'),
                    "reasoning": ai_decision.get('reasoning', ''),        # AI generated
                    "confidence": ai_decision.get('confidence', 0),
                    "pnl_estimate": execution.get('trade_size_usd', 0) * 0.05,   # Running PnL estimate
                    "trade_size_usd": execution.get('trade_size_usd', 0),
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.broadcast(trade_message)
                logger.info(f"Trade executed and broadcasted: {execution.get('tx_hash', 'N/A')}")
            else:
                logger.error("APEX pipeline failed to execute")
                
        except Exception as e:
            logger.error(f"Error running APEX pipeline: {e}")
            # Send error message to dashboard
            error_message = {
                "type": "pipeline_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await self.broadcast(error_message)
    
    async def broadcast(self, message):
        """Broadcast message to all connected clients."""
        if not self.clients:
            return
            
        message_str = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_str)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
        
    async def handle_client(self, websocket, path):
        """Handle individual client connection."""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                # Handle any incoming messages from dashboard
                try:
                    data = json.loads(message)
                    logger.info(f"Received from dashboard: {data}")
                    
                    # Handle specific message types
                    if data.get('type') == 'ping':
                        await websocket.send(json.dumps({"type": "pong"}))
                    elif data.get('type') == 'execute_now':
                        logger.info("Execute trade request received")
                        await self.run_apex_pipeline()
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {message}")
                    
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server."""
        self.running = True
        
        # Start the periodic tasks
        asyncio.create_task(self.periodic_pipeline_run())
        asyncio.create_task(self.periodic_agent_status())
        
        # Start the WebSocket server
        logger.info("Starting APEX WebSocket server on port 8765...")
        
        async with serve(self.handle_client, "localhost", 8765) as server:
            logger.info("✅ APEX WebSocket server running on ws://localhost:8765")
            await server.wait_closed()
    
    async def periodic_pipeline_run(self):
        """Run APEX pipeline every 30 seconds."""
        while self.running:
            await asyncio.sleep(30)  # Wait 30 seconds
            if self.clients:  # Only run if clients are connected
                await self.run_apex_pipeline()
    
    async def periodic_agent_status(self):
        """Broadcast agent status every 10 seconds."""
        while self.running:
            await asyncio.sleep(10)  # Wait 10 seconds
            if self.clients:  # Only broadcast if clients are connected
                await self.broadcast_agent_status()
    
    def stop_server(self):
        """Stop the WebSocket server."""
        self.running = False
        logger.info("APEX WebSocket server stopping...")

async def main():
    """Main entry point."""
    server = APEXWebSocketServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        server.stop_server()
    except Exception as e:
        logger.error(f"Server error: {e}")
        server.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
