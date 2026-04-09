#!/usr/bin/env python3
"""
APEX Agent Registration Script

Standalone script to register APEX agent with lablab.ai hackathon shared contracts
on Ethereum Sepolia and optionally claim the 0.05 ETH sandbox allocation.

Usage:
    python register_apex.py

Author: DR. PRIYA NAIR
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from apex_identity import APEXIdentity
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv()


async def main():
    """Run complete APEX agent registration flow."""
    print("🚀 APEX Agent Registration - Lablab.ai Hackathon")
    print("=" * 50)
    
    try:
        # Initialize APEX Identity
        print("🔧 Initializing APEX Identity...")
        identity = APEXIdentity()
        
        # Check if already registered
        if identity.agent_id > 0:
            print(f"✅ Agent already registered with ID: {identity.agent_id}")
            
            # Verify registration on-chain
            is_registered = identity.agent_registry.functions.isRegistered(identity.agent_id).call()
            if is_registered:
                print("✅ Registration verified on-chain")
            else:
                print("⚠️ Agent ID found but not registered on-chain. Re-registering...")
                identity.agent_id = 0
        else:
            print("🔍 No existing agent ID found. Proceeding with registration...")
        
        # Register agent if needed
        if identity.agent_id == 0:
            print("\n📝 Registering APEX Trading Organism...")
            agent_id = await identity.register_agent()
            
            print(f"\n✅ APEX Agent registered! Agent ID: {agent_id}")
            print(f"📝 Add this to your .env: APEX_AGENT_ID={agent_id}")
            
            # Update .env file
            env_file = Path(__file__).parent.parent / ".env"
            set_key(str(env_file), "APEX_AGENT_ID", str(agent_id))
            print(f"💾 Automatically updated .env file")
            
            # Update identity instance
            identity.agent_id = agent_id
        else:
            agent_id = identity.agent_id
        
        # Get and display full status
        print("\n📊 Agent Status:")
        print("-" * 30)
        status = await identity.get_status()
        
        for key, value in status.items():
            if isinstance(value, float):
                if "balance" in key.lower() or "score" in key.lower():
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        
        # Ask about claiming allocation
        print(f"\n💰 Hackathon Vault Allocation:")
        print(f"  Available: 0.05 ETH sandbox funds")
        print(f"  Claimed: {'Yes' if status.get('has_claimed_allocation') else 'No'}")
        
        if not status.get('has_claimed_allocation'):
            response = input("\nClaim 0.05 ETH sandbox allocation? (y/n): ").strip().lower()
            
            if response == 'y':
                print("\n🎯 Claiming allocation...")
                success = await identity.claim_allocation()
                
                if success:
                    print("✅ Allocation claimed successfully!")
                    
                    # Refresh status
                    updated_status = await identity.get_status()
                    print(f"💰 New vault balance: {updated_status.get('vault_balance_eth', 0):.4f} ETH")
                else:
                    print("❌ Failed to claim allocation")
            else:
                print("⏭️ Skipping allocation claim")
        else:
            print("✅ Allocation already claimed")
        
        # Final summary
        print(f"\n🎉 Registration Complete!")
        print(f"🤖 Agent ID: {agent_id}")
        print(f"🌐 Network: Ethereum Sepolia")
        print(f"🔗 Explorer: https://sepolia.etherscan.io/address/{identity.operator_account.address}")
        
        # Save agent ID to local file for reference
        agent_id_file = Path(__file__).parent / "agent-id.json"
        with open(agent_id_file, "w") as f:
            json.dump({
                "agent_id": agent_id,
                "operator_address": identity.operator_account.address,
                "agent_wallet_address": identity.agent_account.address,
                "network": "Ethereum Sepolia",
                "chain_id": 11155111,
                "registered_at": status.get("timestamp", "unknown")
            }, f, indent=2)
        
        print(f"💾 Agent details saved to: {agent_id_file}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Configure your trading strategies")
        print(f"2. Run APEX with: python apex_core.py")
        print(f"3. Submit trade intents via submit_trade_intent()")
        
    except KeyboardInterrupt:
        print(f"\n❌ Registration cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Registration failed: {str(e)}")
        
        # Provide helpful error messages
        if "insufficient funds" in str(e).lower():
            print(f"💡 Tip: Ensure your operator wallet has ETH for gas fees")
        elif "private key" in str(e).lower():
            print(f"💡 Tip: Check APEX_OPERATOR_PRIVATE_KEY in your .env file")
        elif "network" in str(e).lower() or "rpc" in str(e).lower():
            print(f"💡 Tip: Verify SEPOLIA_RPC_URL is accessible")
        
        sys.exit(1)


if __name__ == "__main__":
    """Run APEX agent registration."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n👋 Goodbye!")
        sys.exit(0)
