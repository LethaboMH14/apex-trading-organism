import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        # Check the latest trade transaction
        tx_hash = "385a6de5d33b3baca7c121759c4332131b22e50d2f21f206196d2dd1f6603bf1"
        
        print("🔍 Checking your latest trade...")
        print(f"📦 Transaction: {tx_hash}")
        print(f"🔗 Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
        
        # Get transaction receipt
        receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
        
        print(f"\n📊 Transaction Status:")
        print(f"  ✅ Status: {'CONFIRMED' if receipt.status == 1 else 'FAILED'}")
        print(f"  📦 Block: {receipt.blockNumber}")
        print(f"  ⛽ Gas Used: {receipt.gasUsed}")
        
        # Check for approval/rejection events
        print(f"\n🔍 Checking for TradeApproved/TradeRejected events...")
        
        approved = False
        rejected = False
        approval_details = None
        rejection_reason = None
        
        for log in receipt.logs:
            # Check for TradeApproved event
            if log.address.lower() == identity.risk_router.address.lower():
                try:
                    # Try to decode as TradeApproved event
                    if len(log.topics) >= 1:
                        topic0 = log.topics[0].hex()
                        # TradeApproved event signature (approximate)
                        if topic0.startswith('0x8c'):
                            approved = True
                            print("✅ Found TradeApproved event!")
                            if len(log.data) >= 32:
                                amount_bytes = log.data[:32]
                                amount = int.from_bytes(amount_bytes, 'big')
                                approval_details = f"Amount: ${amount / 100:.2f}"
                except:
                    pass
                
                # Check for TradeRejected event
                try:
                    if len(log.topics) >= 1:
                        topic0 = log.topics[0].hex()
                        if topic0.startswith('0x9c'):
                            rejected = True
                            # Try to extract rejection reason from data
                            if log.data:
                                try:
                                    reason_bytes = log.data[32:]  # Skip first 32 bytes
                                    rejection_reason = reason_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
                                except:
                                    rejection_reason = "Unknown rejection reason"
                            print("❌ Found TradeRejected event!")
                except:
                    pass
        
        print(f"\n🎯 Trade Result:")
        if approved:
            print("  ✅ STATUS: APPROVED")
            if approval_details:
                print(f"  💰 {approval_details}")
            print("  🚀 Your trade was accepted by RiskRouter!")
        elif rejected:
            print("  ❌ STATUS: REJECTED")
            if rejection_reason:
                print(f"  📝 Reason: {rejection_reason}")
            print("  ⚠️ Your trade was rejected by RiskRouter")
        else:
            print("  ⏳ STATUS: PENDING")
            print("  🔍 Still waiting for RiskRouter decision")
        
        print(f"\n📈 Next Steps:")
        if approved:
            print("  • Trade approved! Submit more trades.")
            print("  • Build reputation score.")
            print("  • Climb the leaderboard!")
        elif rejected:
            print("  • Review rejection reason.")
            print("  • Adjust strategy and retry.")
        else:
            print("  • Monitor for approval/rejection.")
            print("  • Check Etherscan for updates.")
        
        print(f"\n💡 Quick Submit Another Trade:")
        print("python submit_single_trade.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
