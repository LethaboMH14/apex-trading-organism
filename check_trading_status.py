import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("CURRENT TRADING STATUS & BALANCE CHECK")
        print("=" * 50)
        
        # Check current balances
        operator_balance = identity.w3.eth.get_balance(identity.operator_account.address)
        agent_balance = identity.w3.eth.get_balance(identity.agent_account.address)
        
        operator_balance_eth = float(identity.w3.from_wei(operator_balance, 'ether'))
        agent_balance_eth = float(identity.w3.from_wei(agent_balance, 'ether'))
        
        print(f" balances:")
        print(f"  Operator: {operator_balance_eth:.6f} ETH")
        print(f"  Agent: {agent_balance_eth:.6f} ETH")
        print(f"  Total: {operator_balance_eth + agent_balance_eth:.6f} ETH")
        
        # Check gas price and calculate trade capacity
        gas_price = identity.w3.eth.gas_price
        gas_price_gwei = float(identity.w3.from_wei(gas_price, 'gwei'))
        
        print(f"\n gas:")
        print(f"  Current: {gas_price_gwei:.2f} Gwei")
        print(f"  With 1.5x multiplier: {gas_price_gwei * 1.5:.2f} Gwei")
        
        # Calculate trade capacity
        gas_per_trade = 100000
        eth_per_trade = float(identity.w3.from_wei(gas_price * 1.5 * gas_per_trade, 'ether'))
        trades_possible = int(operator_balance_eth / eth_per_trade)
        
        print(f"\n capacity:")
        print(f"  ETH per trade: {eth_per_trade:.6f}")
        print(f"  Trades possible: {trades_possible}")
        print(f"  Minimum needed: 0.002 ETH for 10 trades")
        
        # Check agent status
        print(f"\n status:")
        print(f"  Agent ID: {identity.agent_id}")
        print(f"  Registered: {identity.agent_id > 0}")
        
        try:
            is_registered = identity.agent_registry.functions.isRegistered(identity.agent_id).call()
            print(f"  Registry check: {is_registered}")
        except:
            print(f"  Registry check: Error")
        
        # Check recent trades
        print(f"\n trades:")
        recent_txs = [
            "bedb1eabc18631bec374bbc4c921a3af7736f513a115a717e476440f5620ba5f",
            "385a6de5d33b3baca7c121759c4332131b22e50d2f21f206196d2dd1f6603bf1",
            "eca94507c44fc31261628d378e14d7bb3fabbd30ad81082513443468cc68a5b0"
        ]
        
        for i, tx_hash in enumerate(recent_txs, 1):
            try:
                receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
                status = "CONFIRMED" if receipt.status == 1 else "FAILED"
                print(f"  Trade {i}: {status} (Block: {receipt.blockNumber})")
            except:
                print(f"  Trade {i}: Not found")
        
        # Trading readiness assessment
        print(f"\n READINESS:")
        
        if operator_balance_eth >= 0.002:
            print(f"  Balance: READY ({operator_balance_eth:.6f} ETH >= 0.002)")
        else:
            print(f"  Balance: LOW ({operator_balance_eth:.6f} ETH < 0.002)")
        
        if trades_possible >= 5:
            print(f"  Trades: READY ({trades_possible} possible)")
        elif trades_possible >= 1:
            print(f"  Trades: LIMITED ({trades_possible} possible)")
        else:
            print(f"  Trades: INSUFFICIENT")
        
        if identity.agent_id > 0:
            print(f"  Agent: READY (ID: {identity.agent_id})")
        else:
            print(f"  Agent: NOT REGISTERED")
        
        # Overall assessment
        print(f"\n ASSESSMENT:")
        if trades_possible >= 5:
            print("  Status: READY TO TRADE")
            print("  Action: Submit strategic trades now")
            print("  Command: python submit_single_trade.py")
        elif trades_possible >= 1:
            print("  Status: CAN TRADE (Limited)")
            print("  Action: Submit 1-2 high-value trades")
            print("  Command: python submit_single_trade.py")
        else:
            print("  Status: NEED FUNDING")
            print("  Action: Fund wallet with 0.01+ ETH")
            print("  Faucets: QuickNode, Chainstack, SepoliaFaucet")
        
        print(f"\n RECOMMENDATION:")
        if trades_possible >= 1:
            print("  Submit a trade now to build reputation!")
            print("  Each approved trade = leaderboard points")
        else:
            print("  Fund wallet first, then trade")
        
        print(f"\n Wallet for funding:")
        print(f"  0x909375eC03d6A001A95Bcf20E2260d671a84140B")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
