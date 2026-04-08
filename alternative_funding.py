import sys
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        
        print("ALTERNATIVE FUNDING METHODS")
        print("=" * 40)
        
        print("If faucets aren't working, try these alternatives:")
        
        print("\n1. BRIDGE FROM MAINNET:")
        print("   https://bridge.arbitrum.io/")
        print("   https://www.layerzero.finance/")
        print("   Bridge 0.01 ETH from mainnet to Sepolia")
        
        print("\n2. EXCHANGE WITHDRAWALS:")
        print("   Binance, Coinbase, Kraken")
        print("   Withdraw ETH to Sepolia network")
        print("   Minimum: 0.01 ETH")
        
        print("\n3. SOCIAL FAUCETS:")
        print("   Discord: https://discord.gg/lablab")
        print("   Twitter: @LabLabAI")
        print("   Ask for Sepolia ETH in hackathon channels")
        
        print("\n4. ALTERNATIVE FAUCETS:")
        print("   https://faucet.quicknode.com/ethereum/sepolia")
        print("   https://sepolia-faucet.publicnode.com/")
        print("   https://sepoliafaucet.net/")
        
        print("\n5. COMMUNITY HELP:")
        print("   LabLab Discord hackathon channel")
        print("   Ask other participants for ETH")
        print("   Offer to trade testnet assets")
        
        print(f"\nYOUR WALLET ADDRESS:")
        print(f"0x909375eC03d6A001A95Bcf20E2260d671a84140B")
        
        print(f"\nCURRENT STATUS:")
        balance = identity.w3.eth.get_balance(identity.operator_account.address)
        print(f"Balance: {identity.w3.from_wei(balance, 'ether'):.6f} ETH")
        print(f"Need: 0.01-0.05 ETH for trading")
        
        print(f"\nTEMPORARY SOLUTION:")
        print("1. Reduce gas multiplier to 1.5x")
        print("2. Submit 1-2 strategic trades")
        print("3. Build reputation slowly")
        
        print(f"\nQUICK FIX - REDUCE GAS:")
        print("Edit apex-identity.py line 418:")
        print("gas_price = int(self.w3.eth.gas_price * 1.5)  # Reduce to 1.5x")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
