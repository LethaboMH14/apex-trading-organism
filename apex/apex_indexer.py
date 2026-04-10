"""
APEX On-Chain Indexer - Off-chain event indexing for APEX contracts.

This module indexes events from APEX smart contracts on Sepolia testnet
and stores them locally for API access. Polls for new events every 30 seconds.

Contracts Indexed:
- ValidationRegistry: 0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1
- ReputationRegistry: 0x423a9904e39537a9997fbaF0f220d79D7d545763
- AgentRegistry: 0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv, find_dotenv
from web3 import Web3
from web3.contract import Contract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(find_dotenv(), override=True)


class APEXIndexer:
    """Off-chain indexer for APEX smart contract events."""
    
    def __init__(self):
        """Initialize the indexer."""
        # Connect to Sepolia
        self.rpc_url = os.getenv("SEPOLIA_RPC_URL", "https://rpc.sepolia.org")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Contract addresses
        self.validation_registry = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"
        self.reputation_registry = "0x423a9904e39537a9997fbaF0f220d79D7d545763"
        self.agent_registry = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
        
        # File paths
        self.events_file = Path("apex/indexed_events.jsonl")
        self.state_file = Path("apex/indexer_state.json")
        
        # Ensure directories exist
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load indexer state
        self.state = self._load_state()
        
        # ABI for event filtering (minimal ABI for event signatures)
        self.validation_abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": False, "name": "checkpointHash", "type": "bytes32"},
                    {"indexed": False, "name": "score", "type": "uint8"},
                    {"indexed": False, "name": "validator", "type": "address"}
                ],
                "name": "ValidationPosted",
                "type": "event"
            }
        ]
        
        self.reputation_abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": False, "name": "newScore", "type": "uint8"},
                    {"indexed": False, "name": "previousScore", "type": "uint8"}
                ],
                "name": "ReputationUpdated",
                "type": "event"
            }
        ]
        
        self.agent_abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": True, "name": "agentWallet", "type": "address"},
                    {"indexed": False, "name": "metadata", "type": "string"}
                ],
                "name": "AgentRegistered",
                "type": "event"
            }
        ]
        
        # Contract instances
        self.validation_contract = self.w3.eth.contract(
            address=self.validation_registry,
            abi=self.validation_abi
        )
        self.reputation_contract = self.w3.eth.contract(
            address=self.reputation_registry,
            abi=self.reputation_abi
        )
        self.agent_contract = self.w3.eth.contract(
            address=self.agent_registry,
            abi=self.agent_abi
        )
        
        # Initialize CosmosDB client (optional - graceful fallback if unavailable)
        self.cosmos_client = None
        self.cosmos_container = None
        try:
            from azure.cosmos import CosmosClient
            cosmos_url = os.getenv("COSMOS_URL", "")
            cosmos_key = os.getenv("COSMOS_KEY", "")
            if cosmos_url and cosmos_key:
                self.cosmos_client = CosmosClient(cosmos_url, credential=cosmos_key)
                db = self.cosmos_client.get_database_client("apex")
                self.cosmos_container = db.get_container_client("events")
                logger.info("CosmosDB initialized successfully")
            else:
                raise ValueError("COSMOS_URL or COSMOS_KEY not set")
        except Exception as e:
            logger.info(f"CosmosDB not configured — using local file storage")
            self.cosmos_client = None
            self.cosmos_container = None
        
        logger.info("APEX Indexer initialized")
        logger.info(f"Connected to Sepolia: {self.w3.is_connected()}")
        logger.info(f"Last indexed block: {self.state.get('last_block', 0)}")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load indexer state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        
        return {
            "last_block": 0,
            "total_events": 0,
            "started_at": datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Save indexer state to file."""
        self.state["updated_at"] = datetime.now().isoformat()
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _append_event(self, event_data: Dict[str, Any]):
        """Append event to indexed events file and CosmosDB."""
        try:
            # Append to local file
            with open(self.events_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_data) + "\n")
            self.state["total_events"] += 1
            
            # Upsert to CosmosDB if available
            if self.cosmos_container:
                try:
                    # Use event_type + timestamp as partition key
                    partition_key = f"{event_data.get('event_type', 'unknown')}_{event_data.get('timestamp', '')}"
                    self.cosmos_container.upsert_item(
                        body=event_data,
                        partition_key=partition_key
                    )
                    logger.debug(f"Event upserted to CosmosDB: {event_data.get('event_type')}")
                except exceptions.CosmosHttpResponseError as e:
                    logger.warning(f"CosmosDB upsert failed: {e} - local file persists")
                except Exception as e:
                    logger.warning(f"CosmosDB connection error: {e} - local file persists")
        except Exception as e:
            logger.error(f"Failed to append event: {e}")
    
    def _index_validation_events(self, from_block: int, to_block: int) -> List[Dict[str, Any]]:
        """Index ValidationPosted events."""
        try:
            events = self.validation_contract.events.ValidationPosted.get_logs(
                from_block=from_block,
                to_block=to_block
            )
            
            indexed = []
            for event in events:
                block = self.w3.eth.get_block(event.blockNumber)
                event_data = {
                    "event_type": "ValidationPosted",
                    "block_number": event.blockNumber,
                    "tx_hash": event.transactionHash.hex(),
                    "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
                    "agent_id": event.args.agentId,
                    "score": event.args.score,
                    "validator": event.args.validator,
                    "checkpoint_hash": event.args.checkpointHash.hex(),
                    "raw_data": {
                        "agentId": str(event.args.agentId),
                        "checkpointHash": event.args.checkpointHash.hex(),
                        "score": event.args.score,
                        "validator": event.args.validator
                    }
                }
                indexed.append(event_data)
                self._append_event(event_data)
                logger.info(f"Indexed ValidationPosted for agent {event.args.agentId} (score: {event.args.score})")
            
            return indexed
        except Exception as e:
            logger.error(f"Failed to index validation events: {e}")
            return []
    
    def _index_reputation_events(self, from_block: int, to_block: int) -> List[Dict[str, Any]]:
        """Index ReputationUpdated events."""
        try:
            events = self.reputation_contract.events.ReputationUpdated.get_logs(
                from_block=from_block,
                to_block=to_block
            )
            
            indexed = []
            for event in events:
                block = self.w3.eth.get_block(event.blockNumber)
                event_data = {
                    "event_type": "ReputationUpdated",
                    "block_number": event.blockNumber,
                    "tx_hash": event.transactionHash.hex(),
                    "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
                    "agent_id": event.args.agentId,
                    "new_score": event.args.newScore,
                    "previous_score": event.args.previousScore,
                    "raw_data": {
                        "agentId": str(event.args.agentId),
                        "newScore": event.args.newScore,
                        "previousScore": event.args.previousScore
                    }
                }
                indexed.append(event_data)
                self._append_event(event_data)
                logger.info(f"Indexed ReputationUpdated for agent {event.args.agentId} (score: {event.args.newScore})")
            
            return indexed
        except Exception as e:
            logger.error(f"Failed to index reputation events: {e}")
            return []
    
    def _index_agent_events(self, from_block: int, to_block: int) -> List[Dict[str, Any]]:
        """Index AgentRegistered events."""
        try:
            events = self.agent_contract.events.AgentRegistered.get_logs(
                from_block=from_block,
                to_block=to_block
            )
            
            indexed = []
            for event in events:
                block = self.w3.eth.get_block(event.blockNumber)
                event_data = {
                    "event_type": "AgentRegistered",
                    "block_number": event.blockNumber,
                    "tx_hash": event.transactionHash.hex(),
                    "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
                    "agent_id": event.args.agentId,
                    "agent_wallet": event.args.agentWallet,
                    "metadata": event.args.metadata,
                    "raw_data": {
                        "agentId": str(event.args.agentId),
                        "agentWallet": event.args.agentWallet,
                        "metadata": event.args.metadata
                    }
                }
                indexed.append(event_data)
                self._append_event(event_data)
                logger.info(f"Indexed AgentRegistered for agent {event.args.agentId}")
            
            return indexed
        except Exception as e:
            logger.error(f"Failed to index agent events: {e}")
            return []
    
    def index_block_range(self, from_block: int, to_block: int) -> Dict[str, int]:
        """Index all events in a block range."""
        logger.info(f"Indexing blocks {from_block} to {to_block}")
        
        counts = {
            "validation": 0,
            "reputation": 0,
            "agent": 0
        }
        
        # Index each contract's events
        counts["validation"] = len(self._index_validation_events(from_block, to_block))
        counts["reputation"] = len(self._index_reputation_events(from_block, to_block))
        counts["agent"] = len(self._index_agent_events(from_block, to_block))
        
        # Update state
        self.state["last_block"] = to_block
        self._save_state()
        
        total_indexed = sum(counts.values())
        logger.info(f"Indexed {total_indexed} events in block range {from_block}-{to_block}")
        
        return counts
    
    def get_latest_block(self) -> int:
        """Get the latest block number."""
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Failed to get latest block: {e}")
            return self.state.get("last_block", 0)
    
    def poll(self):
        """Poll for new events since last indexed block."""
        try:
            latest_block = self.get_latest_block()
            last_indexed = self.state.get("last_block", 0)
            
            if latest_block <= last_indexed:
                logger.debug("No new blocks to index")
                return
            
            # Index in chunks of 1000 blocks to avoid RPC limits
            chunk_size = 1000
            from_block = last_indexed + 1
            
            while from_block <= latest_block:
                to_block = min(from_block + chunk_size - 1, latest_block)
                self.index_block_range(from_block, to_block)
                from_block = to_block + 1
            
        except Exception as e:
            logger.error(f"Polling error: {e}")
    
    def start(self):
        """Start the indexer polling loop."""
        logger.info("Starting APEX indexer polling loop...")
        
        while True:
            try:
                self.poll()
                time.sleep(30)  # Poll every 30 seconds
            except KeyboardInterrupt:
                logger.info("Indexer stopped by user")
                break
            except Exception as e:
                logger.error(f"Indexer loop error: {e}")
                time.sleep(30)
    
    def get_status(self) -> Dict[str, Any]:
        """Get indexer status."""
        uptime = datetime.now() - datetime.fromisoformat(self.state.get("started_at", datetime.now().isoformat()))
        return {
            "last_block_indexed": self.state.get("last_block", 0),
            "total_events_indexed": self.state.get("total_events", 0),
            "uptime_seconds": int(uptime.total_seconds()),
            "connected": self.w3.is_connected(),
            "latest_block": self.get_latest_block()
        }
    
    def get_events(self, limit: int = 50, agent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get indexed events from file."""
        if not self.events_file.exists():
            return []
        
        try:
            with open(self.events_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            events = []
            for line in lines:
                event = json.loads(line)
                
                # Filter by agent_id if specified
                if agent_id is not None and event.get("agent_id") != agent_id:
                    continue
                
                events.append(event)
            
            # Return last N events (most recent first)
            return events[-limit:][::-1]
        except Exception as e:
            logger.error(f"Failed to read events: {e}")
            return []


def main():
    """Main execution function."""
    logger.info("Starting APEX Indexer")
    
    try:
        indexer = APEXIndexer()
        
        # Initial sync from genesis or last block
        latest_block = indexer.get_latest_block()
        last_indexed = indexer.state.get("last_block", 0)
        
        if last_indexed == 0:
            logger.info("Initial sync - starting from block 0")
            indexer.index_block_range(0, latest_block)
        else:
            logger.info(f"Resuming from block {last_indexed}")
            indexer.poll()
        
        # Start polling loop
        indexer.start()
        
    except KeyboardInterrupt:
        logger.info("Indexer stopped by user")
    except Exception as e:
        logger.error(f"Indexer error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
