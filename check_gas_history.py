import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("🔍 GAS USAGE ANALYSIS")
        print("=" * 50)
        
        # Check all your previous transactions
        tx_hashes = [
            "6ac256a9966e5d0dd476b828265ff2dedba32063db21980ace92f481242d4f66",  # Registration
            "86df4e72c7332d58896593f1466b8e5dc874dcddcd1d134277d82a251b4bd8d4",  # First trade intent
            "385a6de5d33b3baca7c121759c4332131b22e50d2f21f206196d2dd1f6603bf1",  # Second trade intent
            "eca94507c44fc31261628d378e14d7bb3fabbd30ad81082513443468cc68a5b0",  # Third trade intent
            "126a2b070ad0445bcc202f27729772cf0eb536e2d70e23c1945c516015bef838",  # Fourth trade intent
            "b0cd54393eb3418460d36abf4146e897aaa9856cc95963a4743e815ae21293d0"   # Fifth trade intent
        ]
        
        total_gas_used = 0
        total_eth_spent = 0
        
        print(f"📊 Analyzing {len(tx_hashes)} transactions...")
        
        for i, tx_hash in enumerate(tx_hashes, 1):
            try:
                receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
                gas_used = receipt.gasUsed
                gas_price = receipt.effectiveGasPrice or identity.w3.eth.gas_price
                
                # Calculate ETH spent on gas
                eth_spent = identity.w3.from_wei(gas_used * gas_price, 'ether')
                
                total_gas_used += gas_used
                total_eth_spent += eth_spent
                
                print(f"\n📋 Transaction {i}:")
                print(f"  🔗 Hash: {tx_hash}")
                print(f"  📦 Block: {receipt.blockNumber}")
                print(f"  ⛽ Gas Used: {gas_used:,}")
                print(f"  💰 ETH Spent: {eth_spent:.6f}")
                print(f"  🔍 Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
                
            except Exception as e:
                print(f"\n❌ Error analyzing TX {i}: {e}")
        
        print(f"\n" + "=" * 50)
        print("📈 TOTAL GAS USAGE SUMMARY")
        print("=" * 50)
        
        print(f"📊 Total Transactions: {len(tx_hashes)}")
        print(f"⛽ Total Gas Used: {total_gas_used:,}")
        print(f"💰 Total ETH Spent: {total_eth_spent:.6f}")
        print(f"📊 Average Gas per TX: {total_gas_used // len(tx_hashes):,}")
        
        # Check current balances
        operator_balance = identity.w3.eth.get_balance(identity.operator_account.address)
        agent_balance = identity.w3.eth.get_balance(identity.agent_account.address)
        
        print(f"\n💰 CURRENT BALANCES:")
        print(f"  👤 Operator: {identity.w3.from_wei(operator_balance, 'ether'):.6f} ETH")
        print(f"  🤖 Agent: {identity.w3.from_wei(agent_balance, 'ether'):.6f} ETH")
        
        # Calculate remaining ETH
        total_eth = identity.w3.from_wei(operator_balance + agent_balance, 'ether')
        
        print(f"\n📊 REMAINING ETH: {total_eth:.6f}")
        print(f"💡 Gas Price: {identity.w3.from_wei(identity.w3.eth.gas_price, 'gwei'):.2f} Gwei")
        
        # Estimate future trade capacity
        estimated_gas_per_trade = 100000
        gas_price_with_multiplier = identity.w3.eth.gas_price * 5  # Current multiplier
        eth_per_trade = identity.w3.from_wei(estimated_gas_per_trade * gas_price_with_multiplier, 'ether')
        
        trades_possible = int(total_eth / eth_per_trade) if total_eth > 0 else 0
        
        print(f"\n🔮 FUTURE TRADE CAPACITY:")
        print(f"  📊 Gas per trade: {estimated_gas_per_trade:,}")
        print(f"  💰 ETH per trade: {eth_per_trade:.6f}")
        print(f"  🔄 Trades possible: {trades_possible}")
        
        print(f"\n💡 WHAT HAPPENED TO YOUR ETH:")
        print(f"  💸 Initial balance: ~0.05 ETH (from registration)")
        print(f"  ⛽ Gas spent: {total_eth_spent:.6f} ETH")
        print(f"  📉 Remaining: {total_eth:.6f} ETH")
        print(f"  📉 Percentage used: {(total_eth_spent / 0.05) * 100:.1f}%")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if total_eth < 0.01:
            print("  ❌ CRITICAL: Low on funds!")
            print("  🪙 Fund wallet with 0.05+ ETH")
            print("  🔄 Or reduce gas multiplier (currently 5x)")
        elif total_eth < 0.02:
            print("  ⚠️ WARNING: Low on funds")
            print("  📊 Consider funding with 0.02 ETH")
        else:
            print("  ✅ Adequate for few trades")
        
        print(f"\n🚀 NEXT STEPS:")
        print("  1. Fund operator wallet (0.01-0.05 ETH)")
        print("  2. Run: python build_reputation.py")
        print("  3. Monitor: check_new_trade.py")
        print("  4. Climb leaderboard!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
