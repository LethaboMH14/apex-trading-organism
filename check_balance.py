import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("💰 WALLET BALANCE CHECK")
        print("=" * 40)
        
        # Check operator wallet balance
        operator_balance = identity.w3.eth.get_balance(identity.operator_account.address)
        operator_balance_eth = identity.w3.from_wei(operator_balance, 'ether')
        
        print(f"👤 Operator Wallet: {identity.operator_account.address}")
        print(f"💰 Balance: {operator_balance_eth:.6f} ETH")
        print(f"⛽ Balance (wei): {operator_balance}")
        
        # Check agent wallet balance
        agent_balance = identity.w3.eth.get_balance(identity.agent_account.address)
        agent_balance_eth = identity.w3.from_wei(agent_balance, 'ether')
        
        print(f"\n🤖 Agent Wallet: {identity.agent_account.address}")
        print(f"💰 Balance: {agent_balance_eth:.6f} ETH")
        print(f"⛽ Balance (wei): {agent_balance}")
        
        # Check current gas price
        gas_price = identity.w3.eth.gas_price
        gas_price_gwei = identity.w3.from_wei(gas_price, 'gwei')
        
        print(f"\n⛽ Current Gas Price:")
        print(f"  • Base: {gas_price} wei")
        print(f"  • Gwei: {gas_price_gwei:.2f}")
        print(f"  • With 5x multiplier: {int(gas_price * 5)} wei")
        
        # Calculate needed funds for more trades
        estimated_gas_per_trade = 100000  # Estimated gas per trade
        trades_possible = int(operator_balance / (gas_price * 5 * estimated_gas_per_trade))
        
        print(f"\n📊 Trade Capacity:")
        print(f"  • Estimated gas per trade: {estimated_gas_per_trade:,}")
        print(f"  • Gas cost per trade (5x): {gas_price * 5 * estimated_gas_per_trade} wei")
        print(f"  • Trades possible: {trades_possible}")
        
        print(f"\n💡 SOLUTIONS:")
        if operator_balance_eth < 0.01:
            print("  ❌ INSUFFICIENT FUNDS")
            print("  🪙 Fund operator wallet with ETH")
            print("  📄 Minimum needed: 0.01 ETH")
            print("  🔗 Recommended: 0.05 ETH for multiple trades")
        else:
            print("  ✅ Sufficient for trading")
            print("  🔄 Can submit {trades_possible} more trades")
        
        print(f"\n🌐 Sepolia Faucets:")
        print("  • https://sepoliafaucet.com/")
        print("  • https://www.infura.io/faucet/sepolia")
        print("  • https://sepolia-faucet.pk910.de/")
        
        print(f"\n🎯 RECOMMENDATION:")
        print("  1. Fund operator wallet with 0.05 ETH")
        print("  2. Run: python build_reputation.py")
        print("  3. Monitor trades on Etherscan")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
