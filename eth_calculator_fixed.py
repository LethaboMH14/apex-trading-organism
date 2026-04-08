import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("SEPOLIA ETH NEEDED FOR CONTINUOUS TRADING")
        print("=" * 60)
        
        # Current status
        balance = identity.w3.eth.get_balance(identity.operator_account.address)
        balance_eth = float(identity.w3.from_wei(balance, 'ether'))
        gas_price = identity.w3.eth.gas_price
        
        print(f"Current Balance: {balance_eth:.6f} ETH")
        print(f"Current Gas Price: {identity.w3.from_wei(gas_price, 'gwei'):.2f} Gwei")
        
        # Calculate costs at different gas multipliers
        gas_per_trade = 100000  # Estimated gas per trade
        
        print(f"\n📊 ETH NEEDED CALCULATIONS:")
        print(f"Gas per trade: {gas_per_trade:,}")
        
        multipliers = [1.0, 1.5, 2.0, 3.0]
        
        for multiplier in multipliers:
            gas_price_multiplier = int(gas_price * multiplier)
            eth_per_trade = float(identity.w3.from_wei(gas_price_multiplier * gas_per_trade, 'ether'))
            trades_possible = int(balance_eth / eth_per_trade)
            
            print(f"\n{multiplier}x Gas Multiplier:")
            print(f"  Gas price: {gas_price_multiplier} wei")
            print(f"  ETH per trade: {eth_per_trade:.6f}")
            print(f"  Trades possible: {trades_possible}")
            print(f"  Cost per 10 trades: {eth_per_trade * 10:.6f} ETH")
            print(f"  Cost per 50 trades: {eth_per_trade * 50:.6f} ETH")
        
        # Recommendations for different trading volumes
        print(f"\n🎯 RECOMMENDATIONS FOR CONTINUOUS TRADING:")
        
        scenarios = [
            {"trades": 10, "name": "Light Trading"},
            {"trades": 25, "name": "Active Trading"},
            {"trades": 50, "name": "Heavy Trading"},
            {"trades": 100, "name": "Maximum Trading"}
        ]
        
        for scenario in scenarios:
            eth_needed_1x = float(identity.w3.from_wei(gas_price * gas_per_trade * scenario['trades'], 'ether'))
            eth_needed_1_5x = float(identity.w3.from_wei(gas_price * 1.5 * gas_per_trade * scenario['trades'], 'ether'))
            eth_needed_2x = float(identity.w3.from_wei(gas_price * 2.0 * gas_per_trade * scenario['trades'], 'ether'))
            
            print(f"\n{scenario['name']} ({scenario['trades']} trades):")
            print(f"  1.0x multiplier: {eth_needed_1x:.6f} ETH")
            print(f"  1.5x multiplier: {eth_needed_1_5x:.6f} ETH")
            print(f"  2.0x multiplier: {eth_needed_2x:.6f} ETH")
        
        # Current capacity analysis
        print(f"\n📈 CURRENT CAPACITY ANALYSIS:")
        eth_per_trade_1_5x = float(identity.w3.from_wei(gas_price * 1.5 * gas_per_trade, 'ether'))
        current_trades_possible = int(balance_eth / eth_per_trade_1_5x)
        
        print(f"Current trades possible (1.5x): {current_trades_possible}")
        
        recommended_amounts = [0.01, 0.02, 0.05, 0.1, 0.2]
        
        print(f"\n💰 FUNDING RECOMMENDATIONS:")
        for amount in recommended_amounts:
            trades_with_amount = int((balance_eth + amount) / eth_per_trade_1_5x)
            print(f"  {amount:.3f} ETH = {trades_with_amount} trades total")
        
        # Optimal funding for leaderboard
        print(f"\n🏆 FOR 1ST PLACE COMPETITION:")
        print("  Minimum viable: 0.02 ETH (10-15 trades)")
        print("  Recommended: 0.05 ETH (25-30 trades)")
        print("  Competitive: 0.1 ETH (50+ trades)")
        print("  Maximum: 0.2 ETH (100+ trades)")
        
        print(f"\n💡 QUICK START:")
        print("  1. Fund with 0.02 ETH immediately")
        print("  2. Submit 5-10 strategic trades")
        print("  3. Monitor approvals")
        print("  4. Scale up as reputation grows")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Your balance: {balance_eth:.6f} ETH")
        print(f"  Need for 10 trades: ~0.002 ETH")
        print(f"  Need for 25 trades: ~0.005 ETH")
        print(f"  Need for 50 trades: ~0.01 ETH")
        print(f"  Need for 100 trades: ~0.02 ETH")
        
        print(f"\n🚀 IMMEDIATE ACTION:")
        print("  Fund wallet with 0.02-0.05 ETH")
        print("  This enables 10-30 trades")
        print("  Each approved trade = reputation points")
        print("  More reputation = higher ranking!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
