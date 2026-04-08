import sys
sys.path.insert(0, 'apex')
from apex_identity import APEXIdentity

def main():
    try:
        identity = APEXIdentity()
        print("✅ APEX Identity initialized")
        print(f"Agent ID: {identity.agent_id}")
        print(f"Operator: {identity.operator_account.address}")
        print(f"Agent Wallet: {identity.agent_account.address}")
        
        # Test just the gas price calculation
        gas_price = identity.w3.eth.gas_price
        print(f"Current gas price: {gas_price}")
        print(f"Gas price x3: {int(gas_price * 3)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
