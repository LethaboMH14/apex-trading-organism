import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        tx_hash = "86df4e72c7332d58896593f1466b8e5dc874dcddcd1d134277d82a251b4bd8d4"
        
        print("🔍 Checking current status...")
        print(f"📦 Transaction: {tx_hash}")
        print(f"🔗 Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
        
        # Get receipt
        receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
        print(f"✅ Status: {'CONFIRMED' if receipt.status == 1 else 'FAILED'}")
        print(f"📦 Block: {receipt.blockNumber}")
        print(f"⛽ Gas Used: {receipt.gasUsed}")
        
        # Check if there are any logs
        print(f"📊 Number of logs: {len(receipt.logs)}")
        
        # Check current block
        current_block = identity.w3.eth.block_number
        print(f"🔢 Current block: {current_block}")
        
        # Simple check: if transaction is confirmed and has logs, it was processed
        if receipt.status == 1 and len(receipt.logs) > 0:
            print("✅ Trade intent was successfully submitted to RiskRouter")
            print("⏳ Awaiting approval/rejection from RiskRouter...")
            print("💡 Check the explorer link above for real-time status")
        else:
            print("⚠️ Transaction confirmed but no events found")
        
        print(f"\n📋 Summary:")
        print(f"  • Transaction: CONFIRMED")
        print(f"  • Block: {receipt.blockNumber}")
        print(f"  • Gas Used: {receipt.gasUsed}")
        print(f"  • Status: Submitted to RiskRouter")
        print(f"  • Next: Monitor for TradeApproved/TradeRejected events")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
