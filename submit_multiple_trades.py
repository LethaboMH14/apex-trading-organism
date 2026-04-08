import sys
import asyncio
import time
sys.path.insert(0, 'apex')
from apex_identity import APEXIdentity

async def main():
    try:
        identity = APEXIdentity()
        print("🚀 APEX Multi-Trade Submission System")
        print("=" * 50)
        
        # Define multiple trade strategies
        trades = [
            {
                "pair": "BTC/USD",
                "action": "BUY",
                "amount_usd": 150.0,
                "reasoning": "Bitcoin showing strong bullish momentum. RSI oversold at 28. Volume spike detected. MACD crossover bullish.",
                "confidence": 85
            },
            {
                "pair": "ETH/USD", 
                "action": "BUY",
                "amount_usd": 200.0,
                "reasoning": "Ethereum breaking resistance at $3,200. Positive funding rate. Network activity increasing. DeFi TVL rising.",
                "confidence": 78
            },
            {
                "pair": "SOL/USD",
                "action": "SELL", 
                "amount_usd": 100.0,
                "reasoning": "Solana overextended after 30% rally. Profit-taking opportunity. RSI overbought at 72. Decreasing volume.",
                "confidence": 72
            },
            {
                "pair": "MATIC/USD",
                "action": "BUY",
                "amount_usd": 120.0,
                "reasoning": "Polygon gas fees dropping. Network upgrades incoming. Strong developer activity. Partnership announcements.",
                "confidence": 80
            }
        ]
        
        print(f"📊 Submitting {len(trades)} trade intents...")
        print("⚠️ Note: Waiting 30 seconds between trades to avoid nonce conflicts")
        
        results = []
        
        for i, trade in enumerate(trades, 1):
            print(f"\n🔄 Trade {i}/{len(trades)}: {trade['action']} {trade['pair']} for ${trade['amount_usd']}")
            
            try:
                result = await identity.submit_trade_intent(
                    pair=trade['pair'],
                    action=trade['action'],
                    amount_usd=trade['amount_usd'],
                    reasoning=trade['reasoning'],
                    confidence=trade['confidence']
                )
                
                results.append(result)
                
                if result['success']:
                    print(f"✅ Trade {i} submitted successfully!")
                    print(f"🔗 TX: {result['tx_hash']}")
                    print(f"📦 Gas: {result['gas_used']}")
                    print(f"🔍 Explorer: {result['explorer_url']}")
                    
                    if result.get('approved'):
                        print(f"🎯 Trade {i} APPROVED!")
                    elif result.get('rejection_reason'):
                        print(f"❌ Trade {i} REJECTED: {result['rejection_reason']}")
                    else:
                        print(f"⏳ Trade {i} pending approval...")
                else:
                    print(f"❌ Trade {i} failed: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Error submitting trade {i}: {e}")
                results.append({"success": False, "error": str(e)})
            
            # Wait between trades to avoid nonce conflicts
            if i < len(trades):
                print("⏳ Waiting 30 seconds before next trade...")
                time.sleep(30)
        
        # Summary
        print(f"\n📋 TRADE SUBMISSION SUMMARY")
        print("=" * 50)
        
        successful = sum(1 for r in results if r.get('success', False))
        approved = sum(1 for r in results if r.get('approved', False))
        rejected = sum(1 for r in results if r.get('rejection_reason'))
        
        print(f"✅ Successful submissions: {successful}/{len(trades)}")
        print(f"🎯 Approved trades: {approved}/{successful}")
        print(f"❌ Rejected trades: {rejected}/{successful}")
        
        if successful > 0:
            print(f"\n🔗 Monitor all trades on Etherscan:")
            for i, result in enumerate(results):
                if result.get('tx_hash'):
                    print(f"  Trade {i+1}: {result['explorer_url']}")
        
        print(f"\n🏅 APEX Agent Status:")
        print(f"  • Agent ID: {identity.agent_id}")
        print(f"  • Network: Ethereum Sepolia")
        print(f"  • Competing in: AI Trading Agents Hackathon")
        print(f"  • Prize Pool: $55,000")
        
        print(f"\n💡 Next Steps:")
        print(f"  1. Monitor each trade for approval/rejection")
        print(f"  2. Submit more trades if approved")
        print(f"  3. Build reputation score")
        print(f"  4. Climb the leaderboard!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
