import sys, asyncio
sys.path.insert(0, 'apex')
from apex_identity import APEXIdentity

async def main():
    identity = APEXIdentity()
    result = await identity.submit_trade_intent(
        pair='XBTUSD',
        action='BUY',
        amount_usd=100.0,
        reasoning='BTC momentum signal positive. Volume spike at support. Sentiment bullish 71/100. Sharpe above threshold.',
        confidence=78
    )
    print("Trade Intent Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
