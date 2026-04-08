import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("🏆 DOMINATION COMPLETE - MONITORING APPROVALS")
        print("=" * 60)
        
        # List all submitted trades
        domination_txs = [
            "4cb9fb799e81f4a393e10863c77079e3dc60dd962a61f22d745c6cb64d5df663",
            "9338f5e80d916291e51d91af65c852e83019c7f384afe6caa3665aeb525b393a",
            "34fb9d976e1a6e9f1026664124a8bb16d49031c418ec332b87ee4b2e7e6b7dcf",
            "8ee42acd3bdc1ca0f9d266968fa7a18567bb4a0fa9cd87b177254d1109474f5d",
            "fdf424bcd494ac3ece0a1a20a18829a83271701206a01c900e6885205ef0776e",
            "51b525afe4b964fa38b68c52a359d36386f4df9d1538875167abee3670b60092",
            "006ebcc44e911d05f66452207632e1efd31d238515cdfd7a4215464130cd5f87",
            "bda6d85b4b7fdc71dbee381942bb319f3d65624366da53601a99b32c43b0bfb7",
            "6eba6880ed694b39569b672db186e5a7fca770658bed230dba0d7d61678b9e91",
            "87ae9bd8b7b0be562804c9a3900145178bb16eb0a83262f9181476eec345ccb0"
        ]
        
        print(f"📊 MONITORING {len(domination_txs)} TRADES FOR APPROVALS")
        print(f"💰 Total Volume: $2030.0")
        print(f"🎯 Goal: All trades approved for maximum reputation")
        
        approved_count = 0
        rejected_count = 0
        pending_count = 0
        
        for i, tx_hash in enumerate(domination_txs, 1):
            try:
                receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
                
                # Check for approval/rejection events
                approved = False
                rejected = False
                rejection_reason = None
                
                for log in receipt.logs:
                    if log.address.lower() == identity.risk_router.address.lower():
                        try:
                            # Check for TradeApproved event
                            if len(log.topics) >= 1:
                                topic0 = log.topics[0].hex()
                                if topic0.startswith('0x8c'):
                                    approved = True
                                    approved_count += 1
                                    print(f"✅ Trade {i}: APPROVED")
                                    break
                                
                                if topic0.startswith('0x9c'):
                                    rejected = True
                                    rejected_count += 1
                                    rejection_reason = "RiskRouter rejection"
                                    print(f"❌ Trade {i}: REJECTED - {rejection_reason}")
                                    break
                        except:
                            pass
                
                if not approved and not rejected:
                    pending_count += 1
                    print(f"⏳ Trade {i}: PENDING approval")
                    
                print(f"   Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
                
            except Exception as e:
                print(f"❌ Trade {i}: Error checking - {e}")
        
        print(f"\n📈 APPROVAL SUMMARY:")
        print(f"✅ Approved: {approved_count}/10")
        print(f"❌ Rejected: {rejected_count}/10")
        print(f"⏳ Pending: {pending_count}/10")
        print(f"📊 Approval Rate: {(approved_count/10)*100:.1f}%")
        
        # Calculate reputation impact
        reputation_points = approved_count * 100
        print(f"🏆 Reputation Points: {reputation_points}")
        
        print(f"\n🚀 LEADERBOARD STRATEGY:")
        if approved_count >= 8:
            print("🏆 DOMINATING: Top 5 position secured!")
            print("🎯 Action: Submit more trades to maintain lead")
        elif approved_count >= 5:
            print("🎯 COMPETING: Top 10 position achievable!")
            print("🚀 Action: Submit 5 more trades to climb higher")
        elif approved_count >= 2:
            print("📈 BUILDING: Foundation established!")
            print("💪 Action: Submit strategic trades to build momentum")
        else:
            print("⏳ WAITING: Trades still processing")
            print("⏰ Action: Monitor and submit more as approved")
        
        print(f"\n💡 IMMEDIATE ACTIONS:")
        print("1. Monitor Etherscan for TradeApproved events")
        print("2. Submit more high-confidence trades")
        print("3. Focus on pairs with highest approval rates")
        print("4. Scale volume as reputation grows")
        
        print(f"\n🎯 NEXT TRADE BATCH:")
        print("• BTC/USD BUY $400 (highest confidence)")
        print("• ETH/USD BUY $350 (network momentum)")
        print("• SOL/USD BUY $300 (NFT volume)")
        print("• AVAX/USD BUY $280 (gaming growth)")
        
        print(f"\n🏆 PATH TO #1:")
        print(f"• Current: {approved_count} approved trades")
        print(f"• Target: 25+ approved trades")
        print(f"• Strategy: High-volume, high-confidence trades")
        print(f"• Timeline: Submit 5 trades per hour")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
