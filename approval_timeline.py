import sys
import time
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("🎯 TRADE APPROVAL & LEADERBOARD MONITOR")
        print("=" * 60)
        
        print("📊 HOW TO KNOW WHEN TRADES ARE APPROVED:")
        print("1. Etherscan Events: Look for 'TradeApproved' logs")
        print("2. Our Monitor Script: python monitor_approvals.py")
        print("3. Real-time Tracking: Check transaction pages")
        print("4. Leaderboard Updates: Reputation score changes")
        
        print(f"\n⏰ TIMELINE EXPECTATIONS:")
        print("• Trade Submission: Instant")
        print("• RiskRouter Processing: 5-30 minutes")
        print("• Approval/Rejection: 30-60 minutes average")
        print("• Leaderboard Update: 15-30 minutes after approval")
        
        # Check current trades status
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
        
        print(f"\n🔍 CHECKING CURRENT TRADE STATUS:")
        
        approved_count = 0
        rejected_count = 0
        pending_count = 0
        
        for i, tx_hash in enumerate(domination_txs, 1):
            try:
                receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
                
                # Check for approval/rejection events
                approved = False
                rejected = False
                
                for log in receipt.logs:
                    if log.address.lower() == identity.risk_router.address.lower():
                        try:
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
                                    print(f"❌ Trade {i}: REJECTED")
                                    break
                        except:
                            pass
                
                if not approved and not rejected:
                    pending_count += 1
                    print(f"⏳ Trade {i}: PENDING")
                
                print(f"   🔗 Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
                
            except Exception as e:
                print(f"❌ Trade {i}: Error - {e}")
        
        print(f"\n📈 CURRENT STATUS:")
        print(f"✅ Approved: {approved_count}/10")
        print(f"❌ Rejected: {rejected_count}/10")
        print(f"⏳ Pending: {pending_count}/10")
        print(f"🏆 Reputation Points: {approved_count * 100}")
        
        # Check reputation score
        try:
            reputation = identity.w3.eth.contract(
                address=identity.reputation_registry_address,
                abi=identity.reputation_registry.abi
            ).functions.getAverageScore(identity.agent_id).call()
            print(f"📊 Reputation Score: {reputation}")
        except:
            print(f"📊 Reputation Score: Checking...")
        
        print(f"\n🚀 NEXT STEPS:")
        if approved_count >= 5:
            print("🎯 EXCELLENT! Submit more trades to maintain momentum")
            print("💡 Command: python dominate_leaderboard.py")
        elif approved_count >= 2:
            print("📈 GOOD START! Monitor and submit strategic follow-ups")
            print("💡 Command: python submit_single_trade.py")
        else:
            print("⏳ PATIENCE: Trades still processing (normal)")
            print("💡 Command: python monitor_approvals.py (check every 10 mins)")
        
        print(f"\n⏰ MONITORING SCHEDULE:")
        print("• Every 10 minutes: python monitor_approvals.py")
        print("• Every 30 minutes: Check Etherscan for events")
        print("• Every hour: Check leaderboard position")
        print("• Every 2 hours: Submit new batch if approved")
        
        print(f"\n🎯 LEADERBOARD TIMING:")
        print("• Trade Approval: 30-60 minutes")
        print("• Reputation Update: 15-30 minutes after approval")
        print("• Leaderboard Refresh: Every 5-10 minutes")
        print("• Ranking Change: Immediate after reputation update")
        
        print(f"\n💡 PRO TIPS:")
        print("• High-confidence trades (90%+) approve faster")
        print("• Lower amounts ($100-200) have higher approval rates")
        print("• BTC/USD and ETH/USD typically approve first")
        print("• Check Etherscan 'Logs' tab for TradeApproved events")
        
        print(f"\n🔔 AUTOMATED MONITORING:")
        print("• Set phone timer for every 15 minutes")
        print("• Run: python monitor_approvals.py")
        print("• Submit more trades when approvals come in")
        print("• Scale up volume as reputation grows")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
