import sys
import time
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        print("🔍 Monitoring trade approval status...")
        
        tx_hash = "86df4e72c7332d58896593f1466b8e5dc874dcddcd1d134277d82a251b4bd8d4"
        
        # Monitor for approval/rejection events
        print("⏳ Waiting for RiskRouter approval...")
        print("Checking recent blocks for TradeApproved/TradeRejected events...")
        
        # Get current block
        current_block = identity.w3.eth.block_number
        start_block = current_block - 50  # Check last 50 blocks
        
        print(f"📦 Scanning blocks {start_block} to {current_block}")
        
        # Get events
        approved_events = identity.risk_router.events.TradeApproved().get_logs(
                fromBlock=start_block,
                toBlock=current_block,
                argument_filters={'agentId': identity.agent_id}
        )
        
        rejected_events = identity.risk_router.events.TradeRejected().get_logs(
                fromBlock=start_block,
                toBlock=current_block,
                argument_filters={'agentId': identity.agent_id}
        )
        
        if approved_events:
                event = approved_events[-1]  # Get most recent
                print(f"✅ Trade APPROVED!")
                print(f"💰 Amount: ${event.args.amountUsdScaled / 100}")
                print(f"📦 Block: {event.blockNumber}")
                print(f"🔗 Transaction: {event.transactionHash.hex()}")
                return True
        
        if rejected_events:
                event = rejected_events[-1]  # Get most recent
                print(f"❌ Trade REJECTED!")
                print(f"📝 Reason: {event.args.reason}")
                print(f"📦 Block: {event.blockNumber}")
                print(f"🔗 Transaction: {event.transactionHash.hex()}")
                return True
        
        print("⏳ No approval/rejection events found yet. Trade still pending...")
        print("🔄 Will continue monitoring...")
        
        # Continue monitoring
        for i in range(10):  # Check for 10 more cycles
                time.sleep(10)  # Wait 10 seconds
                
                try:
                        approved_events = identity.risk_router.events.TradeApproved().get_logs(
                                fromBlock=current_block,
                                argument_filters={'agentId': identity.agent_id}
                        )
                        
                        rejected_events = identity.risk_router.events.TradeRejected().get_logs(
                                fromBlock=current_block,
                                argument_filters={'agentId': identity.agent_id}
                        )
                        
                        if approved_events:
                                event = approved_events[-1]
                                print(f"\n✅ Trade APPROVED! (Cycle {i+1})")
                                print(f"💰 Amount: ${event.args.amountUsdScaled / 100}")
                                print(f"📦 Block: {event.blockNumber}")
                                print(f"🔗 Transaction: {event.transactionHash.hex()}")
                                return True
                        
                        if rejected_events:
                                event = rejected_events[-1]
                                print(f"\n❌ Trade REJECTED! (Cycle {i+1})")
                                print(f"📝 Reason: {event.args.reason}")
                                print(f"📦 Block: {event.blockNumber}")
                                print(f"🔗 Transaction: {event.transactionHash.hex()}")
                                return True
                        
                        current_block = identity.w3.eth.block_number
                        print(f"⏳ Still waiting... (Cycle {i+1}/10, Block: {current_block})")
                        
                except Exception as e:
                        print(f"⚠️ Error checking cycle {i+1}: {e}")
        
        print("⏰ Monitoring timeout. Trade may still be pending.")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
