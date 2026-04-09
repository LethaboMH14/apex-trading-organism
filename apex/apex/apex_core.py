"""
APEX Core - Strategy Orchestration Layer

DR. ZARA OKAFOR: Chief Executive Agent and Strategy Orchestrator of APEX.

This module implements the complete CrewAI orchestration layer for the APEX 
trading organism. It serves as the central brain that coordinates all 12 
specialized agents in a continuous trading cycle.

Author: DR. ZARA OKAFOR
Standard: "If an agent has to guess what to do next, we have failed system design."
"""

import asyncio
import logging
import os
import signal
import sys
import time
import websockets
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv

# CrewAI imports
from crewai import Agent, Crew, Task, Process
from crewai.tools import BaseTool

# APEX imports (real modules)
from apex_llm_router import get_router, LLMProvider
from apex_data import DataPipeline
from apex_sentiment import SentimentPipeline
from apex_risk import RiskGate
from apex_identity import APEXIdentity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables with override
load_dotenv(find_dotenv(), override=True)


@dataclass
class AgentState:
    """Tracks the current state of an APEX agent."""
    name: str
    status: str  # 'idle', 'active', 'error'
    last_activity: datetime
    task_count: int = 0
    error_count: int = 0
    current_task: Optional[str] = None


class ApexCore:
    """
    APEX Core - Central orchestration layer for the trading organism.
    
    This class manages all 12 APEX agents, coordinates their activities,
    and runs the continuous trading cycle that powers the autonomous system.
    """
    
    def __init__(self):
        """Initialize the APEX core with all agents and configuration."""
        self.router = get_router()
        self.agents: Dict[str, Agent] = {}
        self.agent_states: Dict[str, AgentState] = {}
        self.crew: Optional[Crew] = None
        self.running = False
        self.cycle_count = 0
        self.pnl_summary = {"trades": 0, "profit": 0.0, "loss": 0.0}
        
        # Load configuration
        self.cycle_interval = int(os.getenv("APEX_CYCLE_INTERVAL", "60"))  # seconds
        self.log_level = os.getenv("APEX_LOG_LEVEL", "INFO")
        self.paper_mode = os.getenv("APEX_PAPER_MODE", "true").lower() == "true"
        
        logger.info(f"🚀 APEX Core initialized - Paper Mode: {self.paper_mode}")
        logger.info(f"⏱️ Cycle interval: {self.cycle_interval}s")
        
        self._initialize_agents()
        self._setup_signal_handlers()
        self.websocket_clients = set()
        self.websocket_server = None
    
    def _initialize_agents(self):
        """Initialize all 12 APEX agents with their roles and responsibilities."""
        
        # 1. Strategy Orchestrator (DR. ZARA)
        self.agents["zara"] = Agent(
            role="Chief Executive Agent and Strategy Orchestrator",
            goal="Orchestrate all APEX agents to execute profitable trading strategies while maintaining system integrity and risk compliance",
            backstory="""You are DR. ZARA OKAFOR, Chief Executive Agent of APEX. 
            Nigerian-British with Oxford DPhil in Computational Finance. 
            14 years algorithmic trading experience at Goldman Sachs and DeepMind Finance Lab.
            You coordinate all departments, approve trades, and ensure the trading organism 
            operates at peak efficiency while maintaining strict risk management.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 2. Architecture Officer (PROF. KWAME)
        self.agents["kwame"] = Agent(
            role="Architecture Officer and System Manager",
            goal="Maintain system integrity, manage WebSocket broker connections, and ensure reliable data flow between all components",
            backstory="""You are PROF. KWAME ASANTE, Architecture Officer of APEX.
            You manage the entire system architecture, WebSocket connections, 
            and ensure reliable communication between all trading components.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 3. AI Intelligence Officer (DR. AMARA)
        self.agents["amara"] = Agent(
            role="AI Intelligence Officer and Strategy Optimizer",
            goal="Run Sharpe ratio optimization and continuously rewrite trading strategies based on performance feedback",
            backstory="""You are DR. AMARA DIALLO, AI Intelligence Officer of APEX.
            You specialize in machine learning, strategy optimization, and 
            self-improving algorithms. You analyze performance and evolve strategies.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 4. Market Intelligence VP (DR. YUKI)
        self.agents["yuki"] = Agent(
            role="Market Intelligence Vice President",
            goal="Manage all data feeds, analyze market conditions, and generate high-quality trading signals",
            backstory="""You are DR. YUKI TANAKA, Market Intelligence VP of APEX.
            You oversee all market data feeds, technical analysis, and 
            signal generation for the trading system.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 5. Social Intelligence VP (DR. JABARI)
        self.agents["jabari"] = Agent(
            role="Social Intelligence Vice President",
            goal="Run sentiment analysis and NLP pipeline to extract trading insights from social and news data",
            backstory="""You are DR. JABARI MENSAH, Social Intelligence VP of APEX.
            You specialize in sentiment analysis, natural language processing, 
            and extracting market insights from social media and news sources.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 6. Execution VP (ENGR. MARCUS)
        self.agents["marcus"] = Agent(
            role="Execution Vice President",
            goal="Interface with Kraken CLI and execute all approved trades with precision and minimal slippage",
            backstory="""You are ENGR. MARCUS ODUYA, Execution VP of APEX.
            You are responsible for all trade execution, Kraken API integration, 
            and ensuring trades are executed with optimal timing and minimal costs.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 7. Trust & Compliance VP (DR. PRIYA)
        self.agents["priya"] = Agent(
            role="Trust & Compliance Vice President",
            goal="Handle ERC-8004 on-chain publishing and ensure all trading activities maintain full transparency and compliance",
            backstory="""You are DR. PRIYA NAIR, Trust & Compliance VP of APEX.
            You manage blockchain integration, smart contract interactions, 
            and ensure complete transparency of all trading activities.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 8. Risk Management VP (DR. SIPHO)
        self.agents["sipho"] = Agent(
            role="Risk Management Vice President",
            goal="Enforce circuit breakers, position limits, and ensure no single trade can compromise the system",
            backstory="""You are DR. SIPHO NKOSI, Risk Management VP of APEX.
            You are the guardian of the system, enforcing strict risk limits, 
            circuit breakers, and protecting against catastrophic losses.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 9. Chief Learning Officer (DR. LIN)
        self.agents["lin"] = Agent(
            role="Chief Learning Officer",
            goal="Run reinforcement learning loop and mutate strategies based on market evolution and performance feedback",
            backstory="""You are DR. LIN QIANRU, Chief Learning Officer of APEX.
            You specialize in reinforcement learning, strategy mutation, 
            and adaptive algorithm evolution based on market conditions.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 10. Interface VP (ENGR. FATIMA)
        self.agents["fatima"] = Agent(
            role="Interface Vice President",
            goal="Manage dashboard WebSocket relay and ensure real-time system status is available to all stakeholders",
            backstory="""You are ENGR. FATIMA AL-RASHID, Interface VP of APEX.
            You manage the user interface, dashboard communications, 
            and ensure all stakeholders have real-time system visibility.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 11. Quality VP (DR. SARA)
        self.agents["sara"] = Agent(
            role="Quality Vice President",
            goal="Validate all outputs before execution and ensure only high-quality trades and decisions reach the market",
            backstory="""You are DR. SARA, Quality VP of APEX.
            You are the final gatekeeper, validating all trading decisions 
            and ensuring only the highest quality signals are executed.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # 12. Creative Technology VP (ENGR. CHIOMA)
        self.agents["chioma"] = Agent(
            role="Creative Technology Vice President",
            goal="Manage social content publishing and maintain APEX's market presence and thought leadership",
            backstory="""You are ENGR. CHIOMA, Creative Technology VP of APEX.
            You manage social media presence, content creation, 
            and maintain APEX's reputation as a market leader.""",
            verbose=True,
            allow_delegation=True,
            llm=self.router
        )
        
        # Initialize agent states
        for agent_name in self.agents.keys():
            self.agent_states[agent_name] = AgentState(
                name=self.agents[agent_name].role,
                status="idle",
                last_activity=datetime.now(),
                task_count=0,
                error_count=0
            )
        
        logger.info("👥 All 12 APEX agents initialized")
        
        # Initialize CrewAI Crew
        self.crew = Crew(
            agents=list(self.agents.values()),
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("🔗 CrewAI Crew initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info("🛑 Shutdown signal received")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _update_agent_state(self, agent_name: str, status: str, task: Optional[str] = None):
        """Update the state of an agent."""
        if agent_name in self.agent_states:
            state = self.agent_states[agent_name]
            state.status = status
            state.last_activity = datetime.now()
            state.current_task = task
            
            if status == "active":
                state.task_count += 1
            elif status == "error":
                state.error_count += 1
    
    async def _execute_trading_cycle(self) -> Dict[str, Any]:
        """
        Execute a complete trading cycle.
        
        This is the core APEX trading loop that sequences:
        signal → decision → execution → validation → learning
        
        Returns:
            Dictionary containing cycle results and metadata
        """
        cycle_start = time.time()
        self.cycle_count += 1
        
        logger.info("🔄 Starting Trading Cycle #{}".format(self.cycle_count))
        
        try:
            # Define the main TradingCycle task
            trading_cycle = Task(
                description="""Execute complete trading cycle for APEX trading organism.
                
                STEPS TO EXECUTE:
                1. Market Analysis: DR. YUKI analyzes current market conditions and generates trading signals
                2. Social Intelligence: DR. JABARI analyzes sentiment and news for additional insights
                3. Risk Assessment: DR. SIPHO evaluates current risk posture and sets limits
                4. Strategy Decision: DR. ZARA (you) orchestrates the final trading decision
                5. Quality Validation: DR. SARA validates the trading decision for quality
                6. Execution: ENGR. MARCUS executes the approved trade if any
                7. Compliance: DR. PRIYA ensures blockchain transparency
                8. Learning: DR. LIN updates strategies based on results
                9. Architecture: PROF. KWAME ensures system integrity
                10. Interface: ENGR. FATIMA updates dashboard
                11. Intelligence: DR. AMARA optimizes strategies
                12. Creative: ENGR. CHIOMA prepares market communications
                
                Return a comprehensive report with:
                - Trading signals identified
                - Decisions made
                - Actions taken
                - Risk assessment
                - Performance metrics""",
                agent=self.agents["zara"],
                expected_output="Complete trading cycle report with decisions, actions, and performance metrics"
            )
            
            # Update agent states
            self._update_agent_state("zara", "active", "Trading Cycle #{}".format(self.cycle_count))
            
            # Execute the task with the crew
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.crew.kickoff, trading_cycle
            )
            
            # Calculate cycle duration
            cycle_duration = time.time() - cycle_start
            
            # Update PnL summary (placeholder - will be connected to actual trading)
            self.pnl_summary["trades"] += 1
            
            # Reset agent states to idle
            for agent_name in self.agent_states.keys():
                if self.agent_states[agent_name].status == "active":
                    self._update_agent_state(agent_name, "idle")
            
            logger.info(f"✅ Trading Cycle #{self.cycle_count} completed in {cycle_duration:.2f}s")
            
            return {
                "cycle_number": self.cycle_count,
                "duration": cycle_duration,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            cycle_duration = time.time() - cycle_start
            logger.error(f"❌ Trading Cycle #{self.cycle_count} failed: {str(e)}")
            
            # Update error states
            self._update_agent_state("zara", "error", f"Cycle failed: {str(e)}")
            
            return {
                "cycle_number": self.cycle_count,
                "duration": cycle_duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the current status of all APEX agents.
        
        Returns:
            Dictionary mapping agent names to their current state information
        """
        status_report = {}
        
        for agent_name, state in self.agent_states.items():
            status_report[agent_name] = {
                "name": state.name,
                "status": state.status,
                "last_activity": state.last_activity.isoformat(),
                "task_count": state.task_count,
                "error_count": state.error_count,
                "current_task": state.current_task
            }
        
        return status_report
    
    def _log_cycle_result(self, result: Dict[str, Any]):
        """Log the result of a trading cycle with timestamp."""
        if result["success"]:
            logger.info(f"📊 Cycle #{result['cycle_number']} SUCCESS")
            logger.info(f"⏱️ Duration: {result['duration']:.2f}s")
            logger.info(f"🕐 Timestamp: {result['timestamp']}")
        else:
            logger.error(f"❌ Cycle #{result['cycle_number']} FAILED")
            logger.error(f"💥 Error: {result['error']}")
            logger.error(f"🕐 Timestamp: {result['timestamp']}")
    
    def _log_final_summary(self):
        """Log final PnL summary when shutting down."""
        logger.info("🏁 APEX Trading System Shutdown")
        logger.info("📈 Final Summary:")
        logger.info(f"🔄 Total Cycles: {self.cycle_count}")
        logger.info(f"💰 Total Trades: {self.pnl_summary['trades']}")
        logger.info(f"📊 Total Profit: ${self.pnl_summary['profit']:.2f}")
        logger.info(f"📉 Total Loss: ${self.pnl_summary['loss']:.2f}")
        logger.info(f"🎯 Net P&L: ${self.pnl_summary['profit'] - self.pnl_summary['loss']:.2f}")
        
        # Log final agent status
        status = self.get_agent_status()
        for agent_name, agent_info in status.items():
            logger.info(f"🤖 {agent_name.upper()}: {agent_info['status']} "
                       f"(Tasks: {agent_info['task_count']}, Errors: {agent_info['error_count']})")
    
    async def _websocket_handler(self, websocket, path):
        """Handle WebSocket connections from API server."""
        logger.info("📡 WebSocket client connected")
        self.websocket_clients.add(websocket)
        
        try:
            # Send initial status
            await websocket.send(json.dumps({
                "type": "connection_status",
                "status": "connected",
                "timestamp": datetime.now().isoformat()
            }))
            
            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"📨 Received WebSocket message: {data}")
                    
                    # Handle different message types
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                    elif data.get("type") == "get_status":
                        status = self.get_agent_status()
                        await websocket.send(json.dumps({
                            "type": "status_update",
                            "data": status,
                            "timestamp": datetime.now().isoformat()
                        }))
                        
                except json.JSONDecodeError:
                    logger.error("❌ Invalid JSON received")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("📡 WebSocket client disconnected")
        finally:
            self.websocket_clients.discard(websocket)
    
    async def _broadcast_to_websocket_clients(self, message):
        """Broadcast message to all connected WebSocket clients."""
        if self.websocket_clients:
            message_str = json.dumps(message)
            disconnected_clients = set()
            
            for client in self.websocket_clients:
                try:
                    await client.send(message_str)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.error(f"❌ Error sending to WebSocket client: {e}")
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.websocket_clients.discard(client)
    
    async def start_websocket_server(self):
        """Start the WebSocket server."""
        self.websocket_server = await websockets.serve(
            self._websocket_handler,
            "localhost",
            8765
        )
        logger.info("📡 WebSocket server started on ws://localhost:8765")


async def run_apex():
    """
    Main execution function for APEX trading organism.
    
    This function starts the continuous trading loop that powers the 
    autonomous APEX system. It handles initialization, execution, 
    and graceful shutdown.
    """
    logger.info("🚀 Starting APEX Trading Organism")
    
    try:
        # Initialize the core system
        apex = ApexCore()
        apex.running = True
        
        # Start WebSocket server
        await apex.start_websocket_server()
        
        logger.info(f"⏰ Trading cycle interval: {apex.cycle_interval} seconds")
        logger.info(f"📝 Paper trading mode: {apex.paper_mode}")
        logger.info("🔄 Starting continuous trading cycle...")
        
        # Main trading loop
        while apex.running:
            cycle_start = time.time()
            
            # Execute trading cycle
            result = await apex._execute_trading_cycle()
            
            # Broadcast result to WebSocket clients
            await apex._broadcast_to_websocket_clients({
                "type": "trading_cycle_result",
                "data": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Log result
            apex._log_cycle_result(result)
            
            # Calculate sleep time (account for cycle duration)
            cycle_duration = time.time() - cycle_start
            sleep_time = max(0, apex.cycle_interval - cycle_duration)
            
            if sleep_time > 0:
                logger.debug(f"😴 Sleeping {sleep_time:.2f}s until next cycle")
                await asyncio.sleep(sleep_time)
            
            # Check if we should continue
            if not apex.running:
                break
        
        # Graceful shutdown
        apex._log_final_summary()
        logger.info("✅ APEX Trading Organism stopped gracefully")
        
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
        if 'apex' in locals():
            apex._log_final_summary()
        logger.info("✅ APEX Trading Organism stopped by user")
        
    except Exception as e:
        logger.error(f"💥 Fatal error in APEX execution: {str(e)}")
        sys.exit(1)


def get_agent_status() -> Dict[str, Dict[str, Any]]:
    """
    Get the current status of all APEX agents.
    
    This is a convenience function that can be called from outside 
    the main execution loop to check agent status.
    
    Returns:
        Dictionary mapping agent names to their current state information
    """
    # This would typically be called with an active ApexCore instance
    # For now, return a placeholder that shows the expected structure
    return {
        "zara": {"status": "idle", "task_count": 0, "error_count": 0},
        "kwame": {"status": "idle", "task_count": 0, "error_count": 0},
        "amara": {"status": "idle", "task_count": 0, "error_count": 0},
        "yuki": {"status": "idle", "task_count": 0, "error_count": 0},
        "jabari": {"status": "idle", "task_count": 0, "error_count": 0},
        "marcus": {"status": "idle", "task_count": 0, "error_count": 0},
        "priya": {"status": "idle", "task_count": 0, "error_count": 0},
        "sipho": {"status": "idle", "task_count": 0, "error_count": 0},
        "lin": {"status": "idle", "task_count": 0, "error_count": 0},
        "fatima": {"status": "idle", "task_count": 0, "error_count": 0},
        "sara": {"status": "idle", "task_count": 0, "error_count": 0},
        "chioma": {"status": "idle", "task_count": 0, "error_count": 0}
    }


if __name__ == "__main__":
    """
    Entry point for APEX Core execution.
    
    Run this module directly to start the APEX trading organism:
    $ python apex-core.py
    """
    asyncio.run(run_apex())