"""
APEX Identity & On-Chain Integration
Connects to lablab.ai hackathon shared contracts on Ethereum Sepolia.
Network: Ethereum Sepolia (Chain ID: 11155111)
"""

import os
import json
import time
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================
# SHARED HACKATHON CONTRACT ADDRESSES
# ============================================================
AGENT_REGISTRY_ADDRESS     = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"
HACKATHON_VAULT_ADDRESS    = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
RISK_ROUTER_ADDRESS        = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
REPUTATION_REGISTRY_ADDRESS= "0x423a9904e39537a9997fbaF0f220d79D7d545763"
VALIDATION_REGISTRY_ADDRESS= "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"

SEPOLIA_RPC = os.getenv("SEPOLIA_RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")

# ============================================================
# CONTRACT ABIs
# ============================================================
AGENT_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "agentWallet",   "type": "address"},
            {"name": "name",          "type": "string"},
            {"name": "description",   "type": "string"},
            {"name": "capabilities",  "type": "string[]"},
            {"name": "agentURI",      "type": "string"}
        ],
        "name": "register",
        "outputs": [{"name": "agentId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "isRegistered",
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getSigningNonce",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "name": "agentId",        "type": "uint256"},
            {"indexed": True,  "name": "operatorWallet",  "type": "address"},
            {"indexed": False, "name": "agentWallet",     "type": "address"},
            {"indexed": False, "name": "name",            "type": "string"}
        ],
        "name": "AgentRegistered",
        "type": "event"
    }
]

HACKATHON_VAULT_ABI = [
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "claimAllocation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getBalance",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "hasClaimed",
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

RISK_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"name": "agentId",         "type": "uint256"},
                    {"name": "agentWallet",     "type": "address"},
                    {"name": "pair",            "type": "string"},
                    {"name": "action",          "type": "string"},
                    {"name": "amountUsdScaled", "type": "uint256"},
                    {"name": "maxSlippageBps",  "type": "uint256"},
                    {"name": "nonce",           "type": "uint256"},
                    {"name": "deadline",        "type": "uint256"}
                ],
                "name": "intent",
                "type": "tuple"
            },
            {"name": "signature", "type": "bytes"}
        ],
        "name": "submitTradeIntent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {"name": "agentId",         "type": "uint256"},
                    {"name": "agentWallet",     "type": "address"},
                    {"name": "pair",            "type": "string"},
                    {"name": "action",          "type": "string"},
                    {"name": "amountUsdScaled", "type": "uint256"},
                    {"name": "maxSlippageBps",  "type": "uint256"},
                    {"name": "nonce",           "type": "uint256"},
                    {"name": "deadline",        "type": "uint256"}
                ],
                "name": "intent",
                "type": "tuple"
            }
        ],
        "name": "simulateIntent",
        "outputs": [
            {"name": "valid",  "type": "bool"},
            {"name": "reason", "type": "string"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getIntentNonce",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

VALIDATION_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "agentId",        "type": "uint256"},
            {"name": "checkpointHash", "type": "bytes32"},
            {"name": "score",          "type": "uint8"},
            {"name": "notes",          "type": "string"}
        ],
        "name": "postEIP712Attestation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getAverageValidationScore",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

REPUTATION_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "agentId",     "type": "uint256"},
            {"name": "score",       "type": "uint8"},
            {"name": "outcomeRef",  "type": "bytes32"},
            {"name": "comment",     "type": "string"},
            {"name": "feedbackType","type": "uint8"}
        ],
        "name": "submitFeedback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getAverageScore",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ============================================================
# EIP-712 DOMAIN & TYPES
# ============================================================
RISK_ROUTER_DOMAIN = {
    "name": "RiskRouter",
    "version": "1",
    "chainId": 11155111,
    "verifyingContract": RISK_ROUTER_ADDRESS
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


# ============================================================
# APEX IDENTITY CLASS
# ============================================================
class APEXIdentity:
    """
    Manages APEX's on-chain identity and trade submission
    on the lablab.ai hackathon shared contracts (Ethereum Sepolia).
    """

    def __init__(self):
        load_dotenv()

        # Wallet keys
        self.operator_private_key = (
            os.getenv("APEX_OPERATOR_PRIVATE_KEY") or
            os.getenv("APEX_PRIVATE_KEY", "")
        )
        self.agent_private_key = (
            os.getenv("APEX_AGENT_WALLET_PRIVATE_KEY") or
            self.operator_private_key
        )

        if not self.operator_private_key:
            raise ValueError(
                "APEX_OPERATOR_PRIVATE_KEY or APEX_PRIVATE_KEY not set in .env"
            )

        # Accounts
        self.operator_account = Account.from_key(self.operator_private_key)
        self.agent_account = Account.from_key(self.agent_private_key)
        self.operator_address = self.operator_account.address
        self.agent_address = self.agent_account.address

        # Web3
        self.w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))

        # Agent ID (loaded from env or agent-id.json)
        self.agent_id = self._load_agent_id()

        # Contracts
        self.agent_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address(AGENT_REGISTRY_ADDRESS),
            abi=AGENT_REGISTRY_ABI
        )
        self.hackathon_vault = self.w3.eth.contract(
            address=Web3.to_checksum_address(HACKATHON_VAULT_ADDRESS),
            abi=HACKATHON_VAULT_ABI
        )
        self.risk_router = self.w3.eth.contract(
            address=Web3.to_checksum_address(RISK_ROUTER_ADDRESS),
            abi=RISK_ROUTER_ABI
        )
        self.validation_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address(VALIDATION_REGISTRY_ADDRESS),
            abi=VALIDATION_REGISTRY_ABI
        )
        self.reputation_registry = self.w3.eth.contract(
            address=Web3.to_checksum_address(REPUTATION_REGISTRY_ADDRESS),
            abi=REPUTATION_REGISTRY_ABI
        )

        logger.info(f"APEXIdentity initialized")
        logger.info(f"Operator: {self.operator_address}")
        logger.info(f"Agent wallet: {self.agent_address}")
        logger.info(f"Agent ID: {self.agent_id or 'Not registered yet'}")
        logger.info(f"Connected to Sepolia: {self.w3.is_connected()}")

    def _load_agent_id(self) -> int:
        """Load agent ID from env or local file."""
        # Try env first
        env_id = os.getenv("APEX_AGENT_ID", "").strip()
        if env_id and env_id.isdigit():
            return int(env_id)

        # Try local file
        id_file = Path("agent-id.json")
        if id_file.exists():
            try:
                data = json.loads(id_file.read_text())
                return int(data.get("agentId", 0))
            except Exception:
                pass
        return 0

    def _save_agent_id(self, agent_id: int):
        """Save agent ID to local file and log instructions."""
        Path("agent-id.json").write_text(
            json.dumps({"agentId": agent_id, "network": "sepolia"}, indent=2)
        )
        self.agent_id = agent_id
        logger.info(f"Agent ID saved: {agent_id}")
        print(f"\n✅ Add this to your .env file:")
        print(f"   APEX_AGENT_ID={agent_id}\n")

    def _send_transaction(self, tx_func, from_address: str, private_key: str) -> dict:
        """Build, sign, and send a transaction. Returns receipt."""
        nonce = self.w3.eth.get_transaction_count(from_address)
        tx = tx_func.build_transaction({
            "from": from_address,
            "nonce": nonce,
            "gas": 500000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        logger.info(
            f"TX: {tx_hash.hex()} | "
            f"Block: {receipt['blockNumber']} | "
            f"Gas: {receipt['gasUsed']} | "
            f"Status: {'✅' if receipt['status'] == 1 else '❌'}"
        )
        return receipt

    async def register_agent(self) -> int:
        """Register APEX on the shared AgentRegistry. Returns agentId."""
        if self.agent_id:
            logger.info(f"Already registered with agentId: {self.agent_id}")
            return self.agent_id

        logger.info("Registering APEX agent on Sepolia AgentRegistry...")

        tx_func = self.agent_registry.functions.register(
            self.agent_address,
            "APEX Trading Organism",
            "Self-evolving multi-agent AI trading system with ERC-8004 on-chain proofs",
            ["trading", "eip712-signing", "autonomous-learning", "multi-agent", "crewai"],
            "https://github.com/lethabo-masilo/APEX"
        )

        receipt = self._send_transaction(
            tx_func, self.operator_address, self.operator_private_key
        )

        if receipt["status"] != 1:
            raise RuntimeError("Registration transaction failed")

        # Parse agentId from event logs
        try:
            events = self.agent_registry.events.AgentRegistered().process_receipt(receipt)
            agent_id = events[0]["args"]["agentId"]
        except Exception:
            # Fallback: read from logs directly
            logger.warning("Could not parse event — check agent-id.json manually")
            agent_id = 1  # placeholder

        self._save_agent_id(agent_id)
        print(f"\n🎉 APEX registered on-chain!")
        print(f"   Agent ID: {agent_id}")
        print(f"   TX: https://sepolia.etherscan.io/tx/{receipt['transactionHash'].hex()}")
        return agent_id

    async def claim_allocation(self) -> bool:
        """Claim 0.05 ETH sandbox capital from HackathonVault. Optional."""
        if not self.agent_id:
            logger.error("Must register first before claiming allocation")
            return False

        try:
            already_claimed = self.hackathon_vault.functions.hasClaimed(
                self.agent_id
            ).call()
            if already_claimed:
                balance = self.hackathon_vault.functions.getBalance(
                    self.agent_id
                ).call()
                logger.info(
                    f"Already claimed. Balance: "
                    f"{self.w3.from_wei(balance, 'ether')} ETH"
                )
                return True

            logger.info("Claiming 0.05 ETH allocation from HackathonVault...")
            tx_func = self.hackathon_vault.functions.claimAllocation(self.agent_id)
            receipt = self._send_transaction(
                tx_func, self.operator_address, self.operator_private_key
            )

            if receipt["status"] == 1:
                balance = self.hackathon_vault.functions.getBalance(
                    self.agent_id
                ).call()
                print(
                    f"\n💰 Claimed! Balance: "
                    f"{self.w3.from_wei(balance, 'ether')} ETH"
                )
                print(
                    f"   TX: https://sepolia.etherscan.io/tx/"
                    f"{receipt['transactionHash'].hex()}"
                )
                return True
            return False

        except Exception as e:
            logger.warning(f"Claim allocation failed (optional step): {e}")
            return False

    async def submit_trade_intent(
        self,
        pair: str,
        action: str,
        amount_usd: float,
        reasoning: str,
        confidence: int = 75
    ) -> dict:
        """
        Sign and submit a trade intent through RiskRouter.
        Max $500/trade, 10 trades/hour, 5% drawdown limit.
        """
        if not self.agent_id:
            return {"success": False, "error": "Agent not registered"}

        # Enforce limits
        amount_usd = min(amount_usd, 500.0)
        action = action.upper()
        if action not in ("BUY", "SELL"):
            return {"success": False, "error": f"Invalid action: {action}"}

        try:
            # Get current nonce
            nonce = self.risk_router.functions.getIntentNonce(
                self.agent_id
            ).call()

            intent = {
                "agentId":         self.agent_id,
                "agentWallet":     self.agent_address,
                "pair":            pair,
                "action":          action,
                "amountUsdScaled": int(amount_usd * 100),
                "maxSlippageBps":  100,
                "nonce":           nonce,
                "deadline":        int(time.time()) + 300
            }

            # Dry-run simulation first
            intent_tuple = (
                intent["agentId"],
                Web3.to_checksum_address(intent["agentWallet"]),
                intent["pair"],
                intent["action"],
                intent["amountUsdScaled"],
                intent["maxSlippageBps"],
                intent["nonce"],
                intent["deadline"]
            )

            try:
                valid, reason = self.risk_router.functions.simulateIntent(
                    intent_tuple
                ).call()
                if not valid:
                    logger.warning(f"Trade simulation rejected: {reason}")
                    return {"success": False, "error": reason, "simulated": True}
                logger.info(f"Trade simulation passed ✅")
            except Exception as sim_err:
                logger.warning(f"Simulation call failed: {sim_err} — proceeding anyway")

            # EIP-712 signing
            structured_data = {
                "domain": RISK_ROUTER_DOMAIN,
                "types":  TRADE_INTENT_TYPES,
                "message": {
                    "agentId":         intent["agentId"],
                    "agentWallet":     intent["agentWallet"],
                    "pair":            intent["pair"],
                    "action":          intent["action"],
                    "amountUsdScaled": intent["amountUsdScaled"],
                    "maxSlippageBps":  intent["maxSlippageBps"],
                    "nonce":           intent["nonce"],
                    "deadline":        intent["deadline"],
                },
                "primaryType": "TradeIntent"
            }

            signed = Account.sign_typed_data(
                self.agent_private_key,
                full_message=structured_data
            )

            # Submit
            tx_func = self.risk_router.functions.submitTradeIntent(
                intent_tuple,
                signed.signature
            )
            receipt = self._send_transaction(
                tx_func, self.operator_address, self.operator_private_key
            )

            tx_hash = receipt["transactionHash"].hex()
            success = receipt["status"] == 1

            # Post checkpoint immediately after
            if success:
                await self.post_checkpoint(
                    reasoning=reasoning,
                    action=action,
                    pair=pair,
                    amount_usd=amount_usd,
                    score=confidence
                )

            return {
                "success":  success,
                "tx_hash":  tx_hash,
                "explorer": f"https://sepolia.etherscan.io/tx/{tx_hash}",
                "intent":   intent,
            }

        except Exception as e:
            logger.error(f"submit_trade_intent failed: {e}")
            return {"success": False, "error": str(e)}

    async def post_checkpoint(
        self,
        reasoning: str,
        action: str,
        pair: str,
        amount_usd: float,
        score: int = 75
    ) -> str:
        """Post a validation checkpoint to ValidationRegistry."""
        if not self.agent_id:
            return ""

        try:
            # Build checkpoint hash
            checkpoint_data = json.dumps({
                "agentId":   self.agent_id,
                "timestamp": int(time.time()),
                "action":    action,
                "pair":      pair,
                "amount":    amount_usd,
                "reasoning": reasoning,
            }, sort_keys=True)

            checkpoint_hash = Web3.keccak(text=checkpoint_data)

            tx_func = self.validation_registry.functions.postEIP712Attestation(
                self.agent_id,
                checkpoint_hash,
                min(score, 100),
                reasoning[:200]
            )
            receipt = self._send_transaction(
                tx_func, self.operator_address, self.operator_private_key
            )

            tx_hash = receipt["transactionHash"].hex()

            # Append to local audit trail
            log_entry = {
                "timestamp":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "agentId":    self.agent_id,
                "action":     action,
                "pair":       pair,
                "amount_usd": amount_usd,
                "reasoning":  reasoning,
                "score":      score,
                "tx_hash":    tx_hash,
            }
            with open("checkpoints.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            logger.info(f"Checkpoint posted: {tx_hash}")
            return tx_hash

        except Exception as e:
            logger.error(f"post_checkpoint failed: {e}")
            return ""

    async def get_reputation_score(self) -> float:
        """Get current reputation score from ReputationRegistry."""
        if not self.agent_id:
            return 0.0
        try:
            score = self.reputation_registry.functions.getAverageScore(
                self.agent_id
            ).call()
            return float(score)
        except Exception as e:
            logger.error(f"get_reputation_score failed: {e}")
            return 0.0

    async def get_status(self) -> dict:
        """Return full agent status."""
        try:
            registered = (
                self.agent_registry.functions.isRegistered(
                    self.agent_id
                ).call()
                if self.agent_id else False
            )
            balance_wei = self.w3.eth.get_balance(self.operator_address)
            rep_score = await self.get_reputation_score()

            return {
                "agent_id":       self.agent_id,
                "registered":     registered,
                "operator":       self.operator_address,
                "agent_wallet":   self.agent_address,
                "eth_balance":    float(self.w3.from_wei(balance_wei, "ether")),
                "reputation":     rep_score,
                "network":        "Ethereum Sepolia",
                "chain_id":       11155111,
                "connected":      self.w3.is_connected(),
            }
        except Exception as e:
            return {"error": str(e)}


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================
async def register_agent() -> int:
    identity = APEXIdentity()
    return await identity.register_agent()


async def submit_trade(
    pair: str,
    action: str,
    amount_usd: float,
    reasoning: str,
    confidence: int = 75
) -> dict:
    identity = APEXIdentity()
    return await identity.submit_trade_intent(
        pair, action, amount_usd, reasoning, confidence
    )


async def get_status() -> dict:
    identity = APEXIdentity()
    return await identity.get_status()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    async def main():
        identity = APEXIdentity()
        status = await identity.get_status()
        print("\n📊 APEX Status:")
        for k, v in status.items():
            print(f"   {k}: {v}")

    asyncio.run(main())
