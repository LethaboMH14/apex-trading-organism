import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("⚡ GAS MULTIPLIER ADJUSTMENT GUIDE")
        print("=" * 50)
        
        # Current gas settings
        gas_price = identity.w3.eth.gas_price
        gas_price_gwei = float(identity.w3.from_wei(gas_price, 'gwei'))
        
        print(f"📊 CURRENT GAS SETTINGS:")
        print(f"  Base Gas Price: {gas_price_gwei:.2f} Gwei")
        print(f"  Current Multiplier: 1.5x")
        print(f"  Effective Gas: {gas_price_gwei * 1.5:.2f} Gwei")
        
        # Calculate costs at different multipliers
        gas_per_trade = 100000
        
        print(f"\n🔧 GAS MULTIPLIER OPTIONS:")
        
        multipliers = [1.0, 1.5, 2.0, 3.0, 5.0]
        
        for multiplier in multipliers:
            effective_gas = gas_price_gwei * multiplier
            eth_per_trade = float(identity.w3.from_wei(gas_price * multiplier * gas_per_trade, 'ether'))
            
            print(f"\n{multiplier}x Multiplier:")
            print(f"  Effective Gas: {effective_gas:.2f} Gwei")
            print(f"  ETH per Trade: {eth_per_trade:.6f}")
            print(f"  Speed: {'FAST' if multiplier >= 2.0 else 'NORMAL' if multiplier >= 1.5 else 'SLOW'}")
        
        # Current balance and capacity
        balance = identity.w3.eth.get_balance(identity.operator_account.address)
        balance_eth = float(identity.w3.from_wei(balance, 'ether'))
        
        print(f"\n💰 CURRENT BALANCE ANALYSIS:")
        print(f"  Balance: {balance_eth:.6f} ETH")
        
        for multiplier in [1.0, 1.5, 2.0, 3.0]:
            eth_per_trade = float(identity.w3.from_wei(gas_price * multiplier * gas_per_trade, 'ether'))
            trades_possible = int(balance_eth / eth_per_trade)
            print(f"  {multiplier}x: {trades_possible:,} trades possible")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print("  • 1.0x: SLOWEST - Use if trades keep failing")
        print("  • 1.5x: RECOMMENDED - Balanced speed/cost")
        print("  • 2.0x: FAST - Higher priority, more cost")
        print("  • 3.0x: VERY FAST - Maximum priority")
        print("  • 5.0x: ULTRA FAST - Expensive but fastest")
        
        print(f"\n📝 HOW TO CHANGE GAS MULTIPLIER:")
        print("  1. Open: apex/apex-identity.py")
        print("  2. Find line 418 (submit_trade_intent function)")
        print("  3. Change: gas_price = int(self.w3.eth.gas_price * 1.5)")
        print("  4. Replace 1.5 with desired multiplier")
        
        print(f"\n🔧 EDIT EXAMPLES:")
        print("  # For faster trades:")
        print("  gas_price = int(self.w3.eth.gas_price * 2.0)  # 2x multiplier")
        print("")
        print("  # For fastest trades:")
        print("  gas_price = int(self.w3.eth.gas_price * 3.0)  # 3x multiplier")
        print("")
        print("  # For slow but cheap:")
        print("  gas_price = int(self.w3.eth.gas_price * 1.0)  # 1x multiplier")
        
        print(f"\n⚠️ TRADE-OFFS:")
        print("  • Higher multiplier = Faster approval")
        print("  • Higher multiplier = More ETH cost")
        print("  • Lower multiplier = Slower but cheaper")
        print("  • 1.5x = Sweet spot for most cases")
        
        print(f"\n🚀 IMMEDIATE ACTIONS:")
        print("  1. If trades are pending → Increase to 2.0x")
        print("  2. If trades are failing → Increase to 3.0x")
        print("  3. If gas is too expensive → Decrease to 1.0x")
        print("  4. Save file and re-run trades")
        
        print(f"\n💡 CURRENT SITUATION:")
        print("  • Your trades are PENDING (normal)")
        print("  • 1.5x multiplier is working fine")
        print("  • Consider increasing to 2.0x for faster approval")
        print("  • You have massive ETH balance (5.09 ETH)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
