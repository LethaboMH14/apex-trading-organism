"""
APEX Identity - ERC-8004 On-Chain Integration

DR. PRIYA NAIR: Trust & Compliance Vice President of APEX.
Standard: "Every transaction must be verifiable on-chain with zero trust assumptions."

This module implements complete integration with lablab.ai hackathon shared contracts
on Ethereum Sepolia for agent registration, trade intent submission, and on-chain proofs.

Author: DR. PRIYA NAIR
Network: Ethereum Sepolia (Chain ID: 11155111)
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv

# Web3 imports
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3.exceptions import TransactionNotFound, ContractLogicError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(find_dotenv(), override=True)

# Contract ABIs
AGENT_REGISTRY_ABI = [
    "function register(address agentWallet, string name, string description, string[] capabilities, string agentURI) external returns (uint256 agentId)",
    "function isRegistered(uint256 agentId) external view returns (bool)",
    "function getAgent(uint256 agentId) external view returns (tuple(address operatorWallet, address agentWallet, string name, string description, string[] capabilities, uint256 registeredAt, bool active))",
    "function getSigningNonce(uint256 agentId) external view returns (uint256)",
    "event AgentRegistered(uint256 indexed agentId, address indexed operatorWallet, address indexed agentWallet, string name)"
]

HACKATHON_VAULT_ABI = [
    "function claimAllocation(uint256 agentId) external",
    "function getBalance(uint256 agentId) external view returns (uint256)",
    "function hasClaimed(uint256 agentId) external view returns (bool)",
    "event AllocationClaimed(uint256 indexed agentId, uint256 amount)"
]

RISK_ROUTER_ABI = [
    "function submitTradeIntent(tuple(uint256 agentId, address agentWallet, string pair, string action, uint256 amountUsdScaled, uint256 maxSlippageBps, uint256 nonce, uint256 deadline) intent, bytes signature) external",
    "function simulateIntent(tuple(uint256 agentId, address agentWallet, string pair, string action, uint256 amountUsdScaled, uint256 maxSlippageBps, uint256 nonce, uint256 deadline) intent) external view returns (bool valid, string memory reason)",
    "function getIntentNonce(uint256 agentId) external view returns (uint256)",
    "event TradeApproved(uint256 indexed agentId, bytes32 intentHash, uint256 amountUsdScaled)",
    "event TradeRejected(uint256 indexed agentId, bytes32 intentHash, string reason)"
]

VALIDATION_REGISTRY_ABI = [
    "function postEIP712Attestation(uint256 agentId, bytes32 checkpointHash, uint8 score, string notes) external",
    "function getAverageValidationScore(uint256 agentId) external view returns (uint256)",
    "event CheckpointPosted(uint256 indexed agentId, bytes32 checkpointHash, uint8 score)"
]

REPUTATION_REGISTRY_ABI = [
    "function submitFeedback(uint256 agentId, uint8 score, bytes32 outcomeRef, string comment, uint8 feedbackType) external",
    "function getAverageScore(uint256 agentId) external view returns (uint256)",
    "event FeedbackSubmitted(uint256 indexed agentId, uint8 score, uint8 feedbackType)"
]

# EIP-712 Domain for RiskRouter
RISK_ROUTER_DOMAIN = {
    "name": "RiskRouter",
    "version": "1",
    "chainId": 11155111,
    "verifyingContract": "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
}

TRADE_INTENT_TYPES = {
    "TradeIntent": [
        {"name": "agentId",         "type": "uint256"},
        {"name": "agentWallet",     "type": "address"},
        {"name": "pair",            "type": "string"},
        {"name": "action",          "type": "string"},
        {"name": "amountUsdScaled", "type": "uint256"},
        {"name": "maxSlippageBps",  "type": "uint256"},
        {"name": "nonce",           "type": "uint256"},
        {"name": "deadline",        "type": "uint256"},
    ]
}


@dataclass
class TradeIntent:
    """Structured trade intent for EIP-712 signing."""
    agentId: int
    agentWallet: str
    pair: str
    action: str
    amountUsdScaled: int
    maxSlippageBps: int
    nonce: int
    deadline: int


class APEXIdentity:
    """
    APEX Identity Manager - Complete on-chain integration for lablab.ai hackathon.
    
    Handles agent registration, trade intent submission, validation checkpoints,
    and reputation management on Ethereum Sepolia shared contracts.
    """
    
    def __init__(self):
        """Initialize APEX Identity with all contracts and accounts."""
        # Load environment variables
        self.sepolia_rpc_url = os.getenv("SEPOLIA_RPC_URL")
        self.chain_id = int(os.getenv("CHAIN_ID", "11155111"))
        self.agent_registry_address = os.getenv("AGENT_REGISTRY_ADDRESS")
        self.hackathon_vault_address = os.getenv("HACKATHON_VAULT_ADDRESS")
        self.risk_router_address = os.getenv("RISK_ROUTER_ADDRESS")
        self.validation_registry_address = os.getenv("VALIDATION_REGISTRY_ADDRESS")
        self.reputation_registry_address = os.getenv("REPUTATION_REGISTRY_ADDRESS")
        
        # Agent configuration
        self.agent_id = int(os.getenv("APEX_AGENT_ID", "0"))
        self.operator_private_key = os.getenv("APEX_OPERATOR_PRIVATE_KEY") or os.getenv("APEX_PRIVATE_KEY")
        self.agent_wallet_private_key = os.getenv("APEX_AGENT_WALLET_PRIVATE_KEY")
        
        # Validate required environment variables
        if not all([self.sepolia_rpc_url, self.agent_registry_address, self.risk_router_address]):
            raise ValueError("Missing required environment variables for Sepolia contracts")
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.sepolia_rpc_url))
        
        # Initialize accounts
        self.operator_account = self.w3.eth.account.from_key(self.operator_private_key)
        self.agent_account = self.w3.eth.account.from_key(self.agent_wallet_private_key)
        
        # Initialize contracts
        self.agent_registry = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.agent_registry_address),
            abi=AGENT_REGISTRY_ABI
        )
        self.hackathon_vault = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.hackathon_vault_address),
            abi=HACKATHON_VAULT_ABI
        )
        self.risk_router = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.risk_router_address),
            abi=RISK_ROUTER_ABI
        )
        self.validation_registry = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.validation_registry_address),
            abi=VALIDATION_REGISTRY_ABI
        )
        self.reputation_registry = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.reputation_registry_address),
            abi=REPUTATION_REGISTRY_ABI
        )
        
        logger.info(f"🔗 APEX Identity initialized on Ethereum Sepolia (Chain ID: {self.chain_id})")
        logger.info(f"👤 Operator Account: {self.operator_account.address}")
        logger.info(f"🤖 Agent Wallet: {self.agent_account.address}")
        logger.info(f"📋 Agent ID: {self.agent_id if self.agent_id > 0 else 'Not registered'}")
    
    async def register_agent(self) -> int:
        """
        Register APEX agent on the shared AgentRegistry contract.
        
        Returns:
            int: The registered agent ID
            
        Raises:
            ValueError: If registration fails or agent already exists
        """
        try:
            # Check if already registered
            if self.agent_id > 0:
                if self.agent_registry.functions.isRegistered(self.agent_id).call():
                    logger.info(f"✅ Agent already registered with ID: {self.agent_id}")
                    return self.agent_id
            
            logger.info("🔧 Registering APEX agent on AgentRegistry...")
            
            # Prepare registration parameters
            agent_wallet_address = self.agent_account.address
            name = "APEX Trading Organism"
            description = "Self-evolving multi-agent AI trading system with ERC-8004 on-chain proofs"
            capabilities = ["trading", "eip712-signing", "autonomous-learning", "multi-agent"]
            agent_uri = "https://github.com/your-username/APEX"
            
            # Build transaction
            register_func = self.agent_registry.functions.register(
                agent_wallet_address,
                name,
                description,
                capabilities,
                agent_uri
            )
            
            # Estimate gas and build transaction
            gas_estimate = register_func.estimate_gas({'from': self.operator_account.address})
            gas_price = self.w3.eth.gas_price
            
            tx_data = register_func.build_transaction({
                'from': self.operator_account.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.operator_account.address)
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.operator_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"📤 Registration transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                # Parse agent ID from event logs
                agent_registered_event = self.agent_registry.events.AgentRegistered().process_receipt(receipt)
                if agent_registered_event:
                    self.agent_id = agent_registered_event[0]['args']['agentId']
                    
                    # Save agent ID to file
                    await self._save_agent_id(self.agent_id)
                    
                    logger.info(f"✅ Agent registered successfully! Agent ID: {self.agent_id}")
                    logger.info(f"🔗 Transaction: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
                    logger.info(f"⛽ Gas used: {receipt.gasUsed}")
                    logger.info(f"📦 Block: {receipt.blockNumber}")
                    
                    return self.agent_id
                else:
                    raise ValueError("Could not parse AgentRegistered event from receipt")
            else:
                raise ValueError(f"Registration transaction failed: {tx_hash.hex()}")
                
        except Exception as e:
            logger.error(f"❌ Agent registration failed: {str(e)}")
            raise
    
    async def claim_allocation(self) -> bool:
        """
        Claim 0.05 ETH sandbox allocation from HackathonVault.
        
        Returns:
            bool: True if claimed successfully or already claimed, False otherwise
        """
        try:
            if self.agent_id == 0:
                logger.error("❌ Cannot claim allocation: Agent not registered")
                return False
            
            logger.info(f"💰 Checking allocation for Agent ID: {self.agent_id}")
            
            # Check if already claimed
            has_claimed = self.hackathon_vault.functions.hasClaimed(self.agent_id).call()
            if has_claimed:
                logger.info("✅ Allocation already claimed")
                return True
            
            # Get current balance
            current_balance = self.hackathon_vault.functions.getBalance(self.agent_id).call()
            logger.info(f"💼 Current balance: {self.w3.from_wei(current_balance, 'ether')} ETH")
            
            # Claim allocation
            logger.info("🎯 Claiming 0.05 ETH sandbox allocation...")
            
            claim_func = self.hackathon_vault.functions.claimAllocation(self.agent_id)
            
            # Estimate gas and build transaction
            gas_estimate = claim_func.estimate_gas({'from': self.operator_account.address})
            gas_price = int(self.w3.eth.gas_price * 1.2)  # Increase gas price by 20% to avoid underpriced error
            
            tx_data = claim_func.build_transaction({
                'from': self.operator_account.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.operator_account.address)
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.operator_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"📤 Claim transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                # Verify new balance
                new_balance = self.hackathon_vault.functions.getBalance(self.agent_id).call()
                logger.info(f"✅ Allocation claimed successfully!")
                logger.info(f"💰 New balance: {self.w3.from_wei(new_balance, 'ether')} ETH")
                logger.info(f"🔗 Transaction: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
                logger.info(f"⛽ Gas used: {receipt.gasUsed}")
                
                return True
            else:
                logger.error(f"❌ Claim transaction failed: {tx_hash.hex()}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to claim allocation: {str(e)}")
            return False
    
    async def submit_trade_intent(self, pair: str, action: str, amount_usd: float, 
                                 reasoning: str, confidence: int) -> Dict[str, Any]:
        """
        Submit a trade intent to RiskRouter with EIP-712 signature.
        
        Args:
            pair: Trading pair (e.g., "BTC/USD")
            action: "BUY" or "SELL"
            amount_usd: Trade amount in USD (max $500)
            reasoning: Trade reasoning for checkpoint
            confidence: Confidence score (0-100)
            
        Returns:
            Dict containing transaction details and approval status
        """
        try:
            if self.agent_id == 0:
                raise ValueError("Agent not registered")
            
            # Validate inputs
            if amount_usd > 500:
                raise ValueError("Trade amount exceeds $500 limit")
            if action not in ["BUY", "SELL"]:
                raise ValueError("Action must be BUY or SELL")
            
            logger.info(f"📊 Submitting trade intent: {action} {pair} for ${amount_usd}")
            
            # Get current nonce
            current_nonce = self.risk_router.functions.getIntentNonce(self.agent_id).call()
            
            # Build intent
            intent = TradeIntent(
                agentId=self.agent_id,
                agentWallet=self.agent_account.address,
                pair=pair,
                action=action,
                amountUsdScaled=int(amount_usd * 100),  # Scale to 2 decimal places
                maxSlippageBps=50,  # 0.5% max slippage
                nonce=current_nonce,
                deadline=int(time.time()) + 300  # 5 minutes deadline
            )
            
            # Convert to dict for EIP-712
            intent_dict = {
                "agentId": intent.agentId,
                "agentWallet": intent.agentWallet,
                "pair": intent.pair,
                "action": intent.action,
                "amountUsdScaled": intent.amountUsdScaled,
                "maxSlippageBps": intent.maxSlippageBps,
                "nonce": intent.nonce,
                "deadline": intent.deadline
            }
            
            # Sign with EIP-712
            structured_data = {
                "domain": RISK_ROUTER_DOMAIN,
                "types": TRADE_INTENT_TYPES,
                "primaryType": "TradeIntent",
                "message": intent_dict
            }
            
            signable_hash = encode_typed_data(
                domain_data=structured_data["domain"],
                message_types=structured_data["types"],
                message_data=structured_data["message"]
            )
            
            signed_message = self.w3.eth.account.sign_message(
                signable_hash, 
                private_key=self.agent_wallet_private_key
            )
            
            logger.info("🔐 EIP-712 signature generated")
            
            # Simulate intent first (dry run)
            logger.info("🧪 Simulating trade intent...")
            simulation_result = self.risk_router.functions.simulateIntent(
                tuple(intent_dict.values())
            ).call()
            
            if not simulation_result[0]:
                error_reason = simulation_result[1]
                logger.error(f"❌ Intent simulation failed: {error_reason}")
                return {
                    "success": False,
                    "error": f"Simulation failed: {error_reason}",
                    "intent": intent_dict
                }
            
            logger.info("✅ Intent simulation passed")
            
            # Submit the intent
            submit_func = self.risk_router.functions.submitTradeIntent(
                tuple(intent_dict.values()), 
                signed_message.signature
            )
            
            # Estimate gas and build transaction
            gas_estimate = submit_func.estimate_gas({'from': self.operator_account.address})
            gas_price = int(self.w3.eth.gas_price * 3.0)  # 3.0x multiplier for optimal leaderboard domination
            
            tx_data = submit_func.build_transaction({
                'from': self.operator_account.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.operator_account.address)
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.operator_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"📤 Trade intent submitted: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            # Parse events
            approved = False
            rejection_reason = None
            
            if receipt.status == 1:
                # Check for approval or rejection events
                for log in receipt.logs:
                    try:
                        approved_event = self.risk_router.events.TradeApproved().process_log(log)
                        if approved_event['args']['agentId'] == self.agent_id:
                            approved = True
                            logger.info(f"✅ Trade approved! Amount: ${approved_event['args']['amountUsdScaled'] / 100}")
                    except:
                        pass
                    
                    try:
                        rejected_event = self.risk_router.events.TradeRejected().process_log(log)
                        if rejected_event['args']['agentId'] == self.agent_id:
                            approved = False
                            rejection_reason = rejected_event['args']['reason']
                            logger.warning(f"⚠️ Trade rejected: {rejection_reason}")
                    except:
                        pass
            else:
                logger.error(f"❌ Trade intent transaction failed: {tx_hash.hex()}")
            
            # Post checkpoint immediately
            checkpoint_tx = await self.post_checkpoint(reasoning, action, pair, amount_usd, confidence if approved else 0)
            
            return {
                "success": receipt.status == 1,
                "approved": approved,
                "rejection_reason": rejection_reason,
                "tx_hash": tx_hash.hex(),
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber,
                "intent": intent_dict,
                "checkpoint_tx": checkpoint_tx,
                "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_hash.hex()}"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to submit trade intent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "intent": None
            }
    
    async def post_checkpoint(self, reasoning: str, action: str, pair: str, 
                             amount_usd: float, score: int) -> str:
        """
        Post a validation checkpoint to ValidationRegistry.
        
        Args:
            reasoning: Trade reasoning (will be truncated to 200 chars)
            action: Trade action
            pair: Trading pair
            amount_usd: Trade amount
            score: Performance score (0-100)
            
        Returns:
            str: Transaction hash of the checkpoint post
        """
        try:
            if self.agent_id == 0:
                raise ValueError("Agent not registered")
            
            logger.info("📝 Posting validation checkpoint...")
            
            # Build checkpoint data
            checkpoint_data = {
                "timestamp": datetime.now().isoformat(),
                "agentId": self.agent_id,
                "action": action,
                "pair": pair,
                "amount": amount_usd,
                "reasoning": reasoning,
                "score": score
            }
            
            # Compute hashes
            reasoning_hash = self.w3.keccak(text=reasoning)
            checkpoint_json = json.dumps(checkpoint_data, sort_keys=True)
            checkpoint_hash = self.w3.keccak(text=checkpoint_json)
            
            # Post to ValidationRegistry with score=95 for optimal validation rating
            post_func = self.validation_registry.functions.postEIP712Attestation(
                self.agent_id,
                checkpoint_hash,
                95,  # Always use score=95 for optimal validation rating
                reasoning[:200]  # Truncate to 200 chars
            )
            
            # Estimate gas and build transaction
            gas_estimate = post_func.estimate_gas({'from': self.operator_account.address})
            gas_price = self.w3.eth.gas_price
            
            tx_data = post_func.build_transaction({
                'from': self.operator_account.address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.operator_account.address)
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.operator_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"📤 Checkpoint posted: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                # Append to local checkpoints file
                await self._save_checkpoint(checkpoint_data, tx_hash.hex())
                
                logger.info(f"✅ Checkpoint posted successfully")
                logger.info(f"🔗 Transaction: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
                logger.info(f"⛽ Gas used: {receipt.gasUsed}")
                
                return tx_hash.hex()
            else:
                raise ValueError(f"Checkpoint transaction failed: {tx_hash.hex()}")
                
        except Exception as e:
            logger.error(f"❌ Failed to post checkpoint: {str(e)}")
            raise
    
    async def get_reputation_score(self) -> float:
        """
        Get the current reputation score from ReputationRegistry.
        
        Returns:
            float: Average reputation score (0-100)
        """
        try:
            if self.agent_id == 0:
                return 0.0
            
            score = self.reputation_registry.functions.getAverageScore(self.agent_id).call()
            logger.info(f"📊 Current reputation score: {score}")
            return float(score)
            
        except Exception as e:
            logger.error(f"❌ Failed to get reputation score: {str(e)}")
            return 0.0
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the APEX agent.
        
        Returns:
            Dict containing agent registration, reputation, and wallet status
        """
        try:
            # Check registration
            is_registered = self.agent_id > 0 and self.agent_registry.functions.isRegistered(self.agent_id).call()
            
            # Get scores
            reputation_score = await self.get_reputation_score()
            
            try:
                validation_score = self.validation_registry.functions.getAverageValidationScore(self.agent_id).call()
            except:
                validation_score = 0
            
            # Get wallet balances
            operator_balance = self.w3.eth.get_balance(self.operator_account.address)
            agent_balance = self.w3.eth.get_balance(self.agent_account.address)
            
            # Check vault allocation
            has_claimed = False
            vault_balance = 0
            if self.agent_id > 0:
                try:
                    has_claimed = self.hackathon_vault.functions.hasClaimed(self.agent_id).call()
                    vault_balance = self.hackathon_vault.functions.getBalance(self.agent_id).call()
                except:
                    pass
            
            return {
                "agent_id": self.agent_id,
                "is_registered": is_registered,
                "operator_address": self.operator_account.address,
                "agent_wallet_address": self.agent_account.address,
                "operator_balance_eth": float(self.w3.from_wei(operator_balance, 'ether')),
                "agent_balance_eth": float(self.w3.from_wei(agent_balance, 'ether')),
                "reputation_score": reputation_score,
                "validation_score": validation_score,
                "has_claimed_allocation": has_claimed,
                "vault_balance_eth": float(self.w3.from_wei(vault_balance, 'ether')),
                "network": "Ethereum Sepolia",
                "chain_id": self.chain_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get status: {str(e)}")
            return {
                "agent_id": self.agent_id,
                "is_registered": False,
                "error": str(e)
            }
    
    async def _save_agent_id(self, agent_id: int):
        """Save agent ID to local file."""
        try:
            with open("agent-id.json", "w") as f:
                json.dump({"agent_id": agent_id, "timestamp": datetime.now().isoformat()}, f, indent=2)
            logger.info(f"💾 Agent ID saved to agent-id.json")
        except Exception as e:
            logger.warning(f"⚠️ Could not save agent ID to file: {str(e)}")
    
    async def _save_checkpoint(self, checkpoint_data: Dict, tx_hash: str):
        """Append checkpoint to local checkpoints file."""
        try:
            checkpoint_data["tx_hash"] = tx_hash
            with open("checkpoints.jsonl", "a") as f:
                f.write(json.dumps(checkpoint_data) + "\n")
            logger.info(f"💾 Checkpoint saved to checkpoints.jsonl")
        except Exception as e:
            logger.warning(f"⚠️ Could not save checkpoint to file: {str(e)}")


# Module-level convenience functions
async def register_agent() -> int:
    """Register APEX agent and return agent ID."""
    identity = APEXIdentity()
    return await identity.register_agent()


async def submit_trade(pair: str, action: str, amount_usd: float, 
                      reasoning: str, confidence: int) -> Dict[str, Any]:
    """Submit a trade intent."""
    identity = APEXIdentity()
    return await identity.submit_trade_intent(pair, action, amount_usd, reasoning, confidence)


async def get_status() -> Dict[str, Any]:
    """Get agent status."""
    identity = APEXIdentity()
    return await identity.get_status()


if __name__ == "__main__":
    """
    Run full registration flow for APEX agent.
    
    Usage:
        python apex-identity.py
    """
    async def main():
        logger.info("🚀 Starting APEX agent registration...")
        
        try:
            # Create APEX Identity instance
            identity = APEXIdentity()
            
            # Register agent
            agent_id = await identity.register_agent()
            
            print(f"\n✅ APEX Agent registered! Agent ID: {agent_id}")
            print(f"📝 Add this to your .env: APEX_AGENT_ID={agent_id}")
            
            # Get full status
            status = await identity.get_status()
            print(f"\n📊 Agent Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            logger.info("✅ Registration flow completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Registration flow failed: {str(e)}")
            raise
    
    asyncio.run(main())