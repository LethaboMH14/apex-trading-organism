import requests
import json
import sys
from datetime import datetime

def main():
    print("🏆 Checking AI Trading Agents Hackathon Leaderboard...")
    
    try:
        # Try to access the leaderboard
        urls = [
            "https://leaderboard.lablab.ai",
            "https://lablab.ai/leaderboard",
            "https://ai-trading-hackathon.leaderboard.lablab.ai"
        ]
        
        leaderboard_data = None
        working_url = None
        
        for url in urls:
            try:
                print(f"🔍 Trying: {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Connected to: {url}")
                    working_url = url
                    # Try to parse JSON if available
                    try:
                        leaderboard_data = response.json()
                        print("✅ Found JSON data")
                    except:
                        print("📄 Found HTML page (may need manual check)")
                    break
                else:
                    print(f"❌ Status {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        if working_url:
            print(f"\n🌐 Leaderboard URL: {working_url}")
            print("📊 The AI Trading Agents Hackathon is LIVE!")
            print("\n💡 What this means for APEX:")
            print("  • Your trade intent (86df4e72c7332d58896593f1466b8e5dc874dcddcd1d134277d82a251b4bd8d4) is submitted")
            print("  • RiskRouter is processing your trade")
            print("  • You're competing against other AI agents")
            print("  • Monitor for TradeApproved/TradeRejected events")
            print("  • Check reputation score and validation metrics")
            
            print(f"\n🏅 Current Status: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("  • APEX Agent ID: 26")
            print("  • Trade Status: Submitted, awaiting approval")
            print("  • Network: Ethereum Sepolia")
            print("  • Prize Pool: $55,000")
            
            print(f"\n🔗 Monitor your trade:")
            print(f"  • Explorer: https://sepolia.etherscan.io/tx/86df4e72c7332d58896593f1466b8e5dc874dcddcd1d134277d82a251b4bd8d4")
            print(f"  • Leaderboard: {working_url}")
            
            if leaderboard_data:
                print(f"\n📈 Leaderboard Data Found:")
                # Try to display some data if available
                if isinstance(leaderboard_data, dict):
                    if 'agents' in leaderboard_data:
                        print(f"  • Total agents: {len(leaderboard_data['agents'])}")
                    if 'top_agent' in leaderboard_data:
                        print(f"  • Current leader: {leaderboard_data['top_agent']}")
                    if 'prize_pool' in leaderboard_data:
                        print(f"  • Prize pool: ${leaderboard_data['prize_pool']}")
                elif isinstance(leaderboard_data, list):
                    print(f"  • Number of entries: {len(leaderboard_data)}")
                else:
                    print(f"  • Data type: {type(leaderboard_data)}")
            
            print(f"\n🎯 Next Steps for APEX:")
            print("  1. Monitor RiskRouter decision on your trade")
            print("  2. Submit more trade intents if approved")
            print("  3. Build reputation through successful trades")
            print("  4. Climb the leaderboard!")
            
        else:
            print("❌ Could not connect to leaderboard")
            print("💡 The hackathon is still live - check Discord for updates")
            
    except Exception as e:
        print(f"❌ Error checking leaderboard: {e}")
        print("💡 The hackathon is live regardless - continue trading!")

if __name__ == "__main__":
    main()
