import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        print("🔍 Checking trade status...")
        
        # Get transaction hash from previous trade
        tx_hash = "86df4e72c7332d58896593f1466b8e5dc874dcddcd1d134277d82a251b4bd8d4"
        
        # Get transaction receipt
        receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
        
        print(f"📦 Block: {receipt.blockNumber}")
        print(f"⛽ Gas Used: {receipt.gasUsed}")
        print(f"✅ Status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")
        
        # Parse events for approval/rejection
        approved = False
        rejection_reason = None
        
        for log in receipt.logs:
            try:
                approved_event = identity.risk_router.events.TradeApproved().process_log(log)
                if approved_event['args']['agentId'] == identity.agent_id:
                    approved = True
                    print(f"✅ Trade APPROVED! Amount: ${approved_event['args']['amountUsdScaled'] / 100}")
            except:
                pass
            
            try:
                rejected_event = identity.risk_router.events.TradeRejected().process_log(log)
                if rejected_event['args']['agentId'] == identity.agent_id:
                    approved = False
                    rejection_reason = rejected_event['args']['reason']
                    print(f"❌ Trade REJECTED: {rejection_reason}")
            except:
                pass
        
        if not approved and not rejection_reason:
            print("⏳ Trade still pending approval...")
        
        print(f"🔗 Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
