import sys
import asyncio
sys.path.insert(0, 'apex')
from apex_identity import APEXIdentity

async def main():
    try:
        identity = APEXIdentity()
        
        # Get user input for trade
        print("🚀 APEX Trade Submission")
        print("=" * 40)
        
        print("\n📊 Trade Details:")
        pair = input("Trading pair (e.g., BTC/USD): ").strip()
        action = input("Action (BUY/SELL): ").strip().upper()
        
        while True:
            try:
                amount = float(input("Amount in USD (max 500): ").strip())
                if amount <= 500:
                    break
                else:
                    print("❌ Amount exceeds $500 limit. Try again.")
            except ValueError:
                print("❌ Invalid amount. Try again.")
        
        reasoning = input("Trade reasoning: ").strip()
        
        while True:
            try:
                confidence = int(input("Confidence score (0-100): ").strip())
                if 0 <= confidence <= 100:
                    break
                else:
                    print("❌ Confidence must be 0-100. Try again.")
            except ValueError:
                print("❌ Invalid confidence. Try again.")
        
        print(f"\n🔄 Submitting trade: {action} {pair} for ${amount}")
        print(f"📝 Reasoning: {reasoning}")
        print(f"📊 Confidence: {confidence}%")
        
        # Submit trade
        result = await identity.submit_trade_intent(
            pair=pair,
            action=action,
            amount_usd=amount,
            reasoning=reasoning,
            confidence=confidence
        )
        
        print(f"\n" + "=" * 40)
        print("📋 RESULT:")
        
        if result['success']:
            print("✅ Trade submitted successfully!")
            print(f"🔗 Transaction: {result['tx_hash']}")
            print(f"📦 Gas Used: {result.get('gas_used', 'N/A')}")
            print(f"🔍 Explorer: {result.get('explorer_url', 'N/A')}")
            
            if result.get('approved'):
                print("🎯 Trade APPROVED!")
                print(f"💰 Amount: ${result['intent']['amountUsdScaled'] / 100}")
            elif result.get('rejection_reason'):
                print(f"❌ Trade REJECTED: {result['rejection_reason']}")
            else:
                print("⏳ Trade pending approval...")
        else:
            print("❌ Trade submission failed!")
            print(f"🚨 Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n💡 Next Steps:")
        print("1. Monitor transaction on Etherscan")
        print("2. Wait for TradeApproved/TradeRejected events")
        print("3. Submit more trades if approved")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
