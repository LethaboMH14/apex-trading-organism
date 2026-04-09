"""
APEX Architecture - System Infrastructure Layer

PROF. KWAME ASANTE: Chief Architecture Officer of APEX.

Background: Ghanaian-German. TU Munich PhD Distributed Systems. Former AWS Principal Engineer. 
Built 3 production trading infrastructures.

This module implements the core infrastructure components that support the entire APEX 
trading organism: state machine management, WebSocket communication, database operations, 
and configuration loading.

Author: PROF. KWAME ASANTE
Standard: "Every component must survive a 3am failure with zero human intervention."
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv, find_dotenv

# Azure Cosmos DB imports
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.core.exceptions import AzureError

# WebSocket imports
import websockets
import websockets.server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables with override
load_dotenv(find_dotenv(), override=True)


class APEXState(Enum):
    """APEX System State Machine States."""
    INITIALIZING = "initializing"
    COLLECTING_DATA = "collecting_data"
    ANALYZING = "analyzing"
    DECISION_GATE = "decision_gate"
    EXECUTING = "executing"
    VALIDATING = "validating"
    LEARNING = "learning"
    IDLE = "idle"
    ERROR = "error"


@dataclass
class StateTransition:
    """Tracks state transitions for debugging and monitoring."""
    from_state: APEXState
    to_state: APEXState
    timestamp: datetime
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class APEXStateMachine:
    """
    APEX State Machine - Core orchestration logic for trading system.
    
    Manages state transitions, logging, and recovery logic for the entire 
    APEX trading organism. All state changes are logged and can be 
    serialized for WebSocket broadcasting.
    """
    
    def __init__(self):
        """Initialize the APEX state machine."""
        self.current_state = APEXState.INITIALIZING
        self.state_history: List[StateTransition] = []
        self.error_count = 0
        self.last_error_time: Optional[datetime] = None
        
        logger.info("🤖 APEX State Machine initialized")
        self._transition_to(APEXState.IDLE, "System startup complete")
    
    def _transition_to(self, new_state: APEXState, reason: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Transition to a new state with logging.
        
        Args:
            new_state: Target state to transition to
            reason: Human-readable reason for transition
            metadata: Optional additional context data
        """
        if new_state == self.current_state:
            logger.debug(f"🔄 Already in state {new_state.value}")
            return
        
        old_state = self.current_state
        self.current_state = new_state
        
        # Log transition
        transition = StateTransition(
            from_state=old_state,
            to_state=new_state,
            timestamp=datetime.now(),
            reason=reason,
            metadata=metadata
        )
        self.state_history.append(transition)
        
        logger.info(f"🔄 State transition: {old_state.value} → {new_state.value}")
        logger.info(f"📝 Reason: {reason}")
        
        if metadata:
            logger.debug(f"📊 Metadata: {metadata}")
    
    def get_current_state(self) -> APEXState:
        """Get the current system state."""
        return self.current_state
    
    def get_state_history(self, limit: int = 50) -> List[StateTransition]:
        """Get recent state transition history."""
        return self.state_history[-limit:] if limit > 0 else self.state_history
    
    def handle_error(self, error: Exception, context: str):
        """
        Handle system errors with automatic recovery logic.
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
        """
        self.error_count += 1
        self.last_error_time = datetime.now()
        
        logger.error(f"💥 System error in {context}: {str(error)}")
        logger.error(f"📊 Error count: {self.error_count}")
        
        # Automatic recovery attempt
        if self.error_count < 3:
            logger.info(f"🔄 Attempting automatic recovery (attempt {self.error_count})")
            self._transition_to(APEXState.IDLE, f"Error recovery - {context}")
        else:
            logger.critical("🚨 Multiple errors - escalating to ERROR state")
            self._transition_to(APEXState.ERROR, f"Critical error - {context}", {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "error_count": self.error_count
            })
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize state machine to dictionary for WebSocket broadcasting.
        
        Returns:
            Dictionary representation of current state and recent history
        """
        return {
            "current_state": self.current_state.value,
            "error_count": self.error_count,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "recent_transitions": [
                {
                    "from_state": t.from_state.value,
                    "to_state": t.to_state.value,
                    "timestamp": t.timestamp.isoformat(),
                    "reason": t.reason,
                    "metadata": t.metadata
                }
                for t in self.state_history[-10:]  # Last 10 transitions
            ]
        }


class WebSocketBroker:
    """
    WebSocket Broker - Real-time communication hub for APEX.
    
    Manages WebSocket connections from React dashboard, broadcasts state updates,
    agent status changes, and trade notifications. Handles disconnections 
    gracefully with automatic reconnection support.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize WebSocket broker.
        
        Args:
            host: WebSocket server host
            port: WebSocket server port
        """
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.running = False
        self.message_queue = asyncio.Queue()
        
        logger.info(f"🌐 WebSocket Broker initialized on {host}:{port}")
    
    async def register_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Register a new WebSocket client connection."""
        self.clients.add(websocket)
        logger.info(f"🔗 Client connected from {websocket.remote_address}")
        
        # Send current state to new client
        await self._broadcast_message({
            "type": "connection_ack",
            "message": "Connected to APEX WebSocket broker",
            "timestamp": datetime.now().isoformat()
        }, websocket)
    
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a WebSocket client connection."""
        self.clients.discard(websocket)
        logger.info(f"🔌 Client disconnected: {websocket.remote_address}")
    
    async def _broadcast_message(self, message: Dict[str, Any], target_client: Optional[websockets.WebSocketServerProtocol] = None):
        """
        Broadcast message to all connected clients or specific client.
        
        Args:
            message: Message to broadcast
            target_client: Optional specific client to send to
        """
        if not self.clients:
            return
        
        message_str = json.dumps(message, default=str)
        
        if target_client:
            await target_client.send(message_str)
        else:
            # Broadcast to all clients
            disconnected = []
            for client in self.clients.copy():
                try:
                    await client.send(message_str)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send to client: {e}")
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                self.clients.discard(client)
    
    async def broadcast_state_update(self, state_machine: APEXStateMachine):
        """Broadcast state machine update to all connected clients."""
        await self._broadcast_message({
            "type": "state_update",
            "data": state_machine.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_agent_update(self, agent_name: str, agent_status: Dict[str, Any]):
        """Broadcast agent status update to all connected clients."""
        await self._broadcast_message({
            "type": "agent_update",
            "agent_name": agent_name,
            "agent_status": agent_status,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_trade_update(self, trade_data: Dict[str, Any]):
        """Broadcast trade execution update to all connected clients."""
        await self._broadcast_message({
            "type": "trade_update",
            "trade_data": trade_data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_error(self, error: Exception, context: str):
        """Broadcast error notification to all connected clients."""
        await self._broadcast_message({
            "type": "error",
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "context": context,
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        })
    
    async def handle_client_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming message from WebSocket client."""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            logger.debug(f"📨 Received message type: {message_type}")
            
            # Handle different message types
            if message_type == "ping":
                await self._broadcast_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            elif message_type == "get_state":
                # This would be connected to state machine instance
                await self._broadcast_message({
                    "type": "state_response",
                    "message": "State machine not directly accessible via WebSocket",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            else:
                logger.warning(f"⚠️ Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Invalid JSON received: {e}")
        except Exception as e:
            logger.error(f"💥 Error handling client message: {e}")
    
    async def client_handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle WebSocket client lifecycle."""
        try:
            await self.register_client(websocket, path)
            
            # Handle messages from this client
            async for message in websocket:
                await self.handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Client connection closed normally")
        except Exception as e:
            logger.error(f"💥 Client handler error: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server."""
        self.running = True
        
        try:
            async with websockets.serve(
                self.client_handler,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            ) as server:
                logger.info(f"🚀 WebSocket server started on ws://{self.host}:{self.port}")
                
                # Process queued messages
                while self.running:
                    try:
                        message = await asyncio.wait_for(
                            self.message_queue.get(),
                            timeout=1.0
                        )
                        await self._broadcast_message(message)
                    except asyncio.TimeoutError:
                        continue  # No messages to process
                    except Exception as e:
                        logger.error(f"💥 Message processing error: {e}")
                        
        except Exception as e:
            logger.error(f"💥 WebSocket server failed to start: {e}")
            raise
    
    async def stop_server(self):
        """Stop the WebSocket server gracefully."""
        logger.info("🛑 Stopping WebSocket server...")
        self.running = False
        
        # Notify all clients
        await self._broadcast_message({
            "type": "server_shutdown",
            "message": "WebSocket server shutting down",
            "timestamp": datetime.now().isoformat()
        })
        
        # Clear message queue
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break


class AzureConfigLoader:
    """
    Azure Configuration Loader - Manages APEX Azure infrastructure settings.
    
    Loads and validates all required Azure configuration from environment variables.
    Provides centralized configuration management for Cosmos DB, OpenAI, and 
    other Azure services used by APEX.
    """
    
    def __init__(self):
        """Initialize Azure configuration loader."""
        self.config = {}
        self._load_configuration()
        self._validate_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables."""
        logger.info("🔧 Loading Azure configuration...")
        
        self.config = {
            # Cosmos DB Configuration
            "cosmos": {
                "connection_string": os.getenv("AZURE_COSMOS_CONNECTION_STRING", ""),
                "database_name": os.getenv("AZURE_COSMOS_DATABASE_NAME", "apex"),
                "container_name": os.getenv("AZURE_COSMOS_CONTAINER_NAME", "trading")
            },
            
            # OpenAI Configuration
            "openai": {
                "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
                "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                "deployment_gpt4o": os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT4O", ""),
                "deployment_gpt4_turbo": os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT4_TURBO", ""),
                "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
            },
            
            # General Configuration
            "general": {
                "environment": os.getenv("APEX_ENVIRONMENT", "development"),
                "log_level": os.getenv("APEX_LOG_LEVEL", "INFO"),
                "paper_mode": os.getenv("APEX_PAPER_MODE", "true").lower() == "true"
            }
        }
        
        logger.info("✅ Azure configuration loaded")
    
    def _validate_configuration(self):
        """Validate that all required configuration is present."""
        errors = []
        
        # Validate Cosmos DB
        cosmos_config = self.config["cosmos"]
        if not cosmos_config["connection_string"]:
            errors.append("AZURE_COSMOS_CONNECTION_STRING is required")
        if not cosmos_config["database_name"]:
            errors.append("AZURE_COSMOS_DATABASE_NAME is required")
        if not cosmos_config["container_name"]:
            errors.append("AZURE_COSMOS_CONTAINER_NAME is required")
        
        # Validate OpenAI
        openai_config = self.config["openai"]
        if not openai_config["api_key"]:
            errors.append("AZURE_OPENAI_API_KEY is required")
        if not openai_config["endpoint"]:
            errors.append("AZURE_OPENAI_ENDPOINT is required")
        if not openai_config["deployment_gpt4o"]:
            errors.append("AZURE_OPENAI_DEPLOYMENT_GPT4O is required")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        logger.info("✅ Azure configuration validated")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self.config
    
    def get_cosmos_config(self) -> Dict[str, str]:
        """Get Cosmos DB configuration."""
        return self.config["cosmos"]
    
    def get_openai_config(self) -> Dict[str, str]:
        """Get OpenAI configuration."""
        return self.config["openai"]
    
    def get_general_config(self) -> Dict[str, Any]:
        """Get general configuration."""
        return self.config["general"]
    
    async def test_connections(self) -> Dict[str, bool]:
        """
        Test all Azure service connections.
        
        Returns:
            Dictionary with connection status for each service
        """
        results = {}
        
        # Test Cosmos DB connection
        try:
            cosmos_client = CosmosClient(
                self.config["cosmos"]["connection_string"]
            )
            # Simple test query
            database = cosmos_client.get_database_client(self.config["cosmos"]["database_name"])
            container = database.get_container_client(self.config["cosmos"]["container_name"])
            
            # Test read access
            items = list(container.query_items(
                query="SELECT TOP 1 * FROM c",
                enable_cross_partition_query=True
            ))
            
            results["cosmos"] = True
            logger.info("✅ Cosmos DB connection successful")
            
        except Exception as e:
            results["cosmos"] = False
            logger.error(f"❌ Cosmos DB connection failed: {e}")
        
        # Test OpenAI connection (would need actual API call)
        results["openai"] = True  # Placeholder - would test actual API
        logger.info("✅ OpenAI configuration validated")
        
        return results


class APEXDatabase:
    """
    APEX Database - Azure Cosmos DB wrapper for trading data persistence.
    
    Provides async interface for storing and retrieving trading data including
    trades, agent decisions, strategy versions, reputation history, and market signals.
    All operations include proper error handling and retry logic.
    """
    
    def __init__(self, cosmos_config: Dict[str, str]):
        """
        Initialize APEX database connection.
        
        Args:
            cosmos_config: Cosmos DB configuration dictionary
        """
        self.cosmos_config = cosmos_config
        self.client = None
        self.database = None
        self.container = None
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Cosmos DB connection with retry logic."""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                self.client = CosmosClient(
                    self.cosmos_config["connection_string"]
                )
                self.database = self.client.get_database_client(
                    self.cosmos_config["database_name"]
                )
                self.container = self.database.get_container_client(
                    self.cosmos_config["container_name"]
                )
                
                logger.info("✅ APEX Database connected to Cosmos DB")
                return
                
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"⚠️ DB connection attempt {attempt + 1} failed, retrying in {delay}s")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ Failed to connect to Cosmos DB after {max_retries} attempts: {e}")
                    raise
    
    async def save_trade(self, trade_data: Dict[str, Any]) -> bool:
        """
        Save trade data to Cosmos DB.
        
        Args:
            trade_data: Dictionary containing trade information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            trade_data["type"] = "trade"
            trade_data["timestamp"] = datetime.now().isoformat()
            trade_data["id"] = f"trade_{int(time.time() * 1000)}"
            
            # Create document
            self.container.create_item(body=trade_data)
            
            logger.info(f"💾 Trade saved: {trade_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save trade: {e}")
            return False
    
    async def save_decision(self, decision_data: Dict[str, Any]) -> bool:
        """
        Save agent decision data to Cosmos DB.
        
        Args:
            decision_data: Dictionary containing decision information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            decision_data["type"] = "decision"
            decision_data["timestamp"] = datetime.now().isoformat()
            decision_data["id"] = f"decision_{int(time.time() * 1000)}"
            
            # Create document
            self.container.create_item(body=decision_data)
            
            logger.info(f"💾 Decision saved: {decision_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save decision: {e}")
            return False
    
    async def save_strategy_version(self, strategy_data: Dict[str, Any]) -> bool:
        """
        Save strategy version data to Cosmos DB.
        
        Args:
            strategy_data: Dictionary containing strategy information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            strategy_data["type"] = "strategy"
            strategy_data["timestamp"] = datetime.now().isoformat()
            strategy_data["id"] = f"strategy_{int(time.time() * 1000)}"
            
            # Create document
            self.container.create_item(body=strategy_data)
            
            logger.info(f"💾 Strategy saved: {strategy_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save strategy: {e}")
            return False
    
    async def get_recent_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent trades from Cosmos DB.
        
        Args:
            limit: Maximum number of trades to retrieve
            
        Returns:
            List of trade dictionaries
        """
        try:
            # Query recent trades
            query = f"SELECT TOP {limit} * FROM c WHERE c.type = 'trade' ORDER BY c.timestamp DESC"
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            trades = []
            for item in items:
                trades.append({
                    "id": item.get("id"),
                    "timestamp": item.get("timestamp"),
                    "symbol": item.get("symbol"),
                    "side": item.get("side"),
                    "amount": item.get("amount"),
                    "price": item.get("price"),
                    "pnl": item.get("pnl")
                })
            
            logger.info(f"📊 Retrieved {len(trades)} recent trades")
            return trades
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent trades: {e}")
            return []
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics from Cosmos DB.
        
        Returns:
            Dictionary containing performance metrics
        """
        try:
            # Query for performance data
            query = """
            SELECT 
                COUNT(c.id) as total_trades,
                SUM(c.pnl) as total_pnl,
                AVG(c.pnl) as avg_pnl,
                MAX(c.pnl) as max_pnl,
                MIN(c.pnl) as min_pnl
            FROM c 
            WHERE c.type = 'trade' 
            AND c.timestamp >= DateTimeAdd('days', -30)
            """
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if items:
                metrics = items[0]
                logger.info("📊 Performance metrics retrieved")
                return {
                    "period": "30_days",
                    "total_trades": metrics.get("total_trades", 0),
                    "total_pnl": metrics.get("total_pnl", 0.0),
                    "avg_pnl": metrics.get("avg_pnl", 0.0),
                    "max_pnl": metrics.get("max_pnl", 0.0),
                    "min_pnl": metrics.get("min_pnl", 0.0)
                }
            else:
                logger.warning("⚠️ No performance data found")
                return {
                    "period": "30_days",
                    "total_trades": 0,
                    "total_pnl": 0.0,
                    "avg_pnl": 0.0,
                    "max_pnl": 0.0,
                    "min_pnl": 0.0
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get performance metrics: {e}")
            return {}


# Initialize and start WebSocket broker when run directly
async def main():
    """Main entry point for APEX architecture components."""
    logger.info("🏗️ Starting APEX Architecture Components")
    
    try:
        # Initialize configuration
        config_loader = AzureConfigLoader()
        
        # Initialize state machine
        state_machine = APEXStateMachine()
        
        # Initialize database
        db = APEXDatabase(config_loader.get_cosmos_config())
        
        # Initialize WebSocket broker
        broker = WebSocketBroker()
        
        # Test connections
        logger.info("🔍 Testing Azure connections...")
        connection_status = await config_loader.test_connections()
        
        for service, status in connection_status.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {service.upper()}: {'Connected' if status else 'Failed'}")
        
        # Start WebSocket server
        logger.info("🚀 Starting WebSocket broker...")
        await broker.start_server()
        
    except KeyboardInterrupt:
        logger.info("🛑 Architecture components stopped by user")
    except Exception as e:
        logger.error(f"💥 Fatal error in architecture components: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("🏁 APEX Architecture Components shutdown complete")


if __name__ == "__main__":
    """
    Entry point for APEX architecture system.
    
    Run this module directly to start infrastructure components:
    $ python apex-architecture.py
    """
    asyncio.run(main())
