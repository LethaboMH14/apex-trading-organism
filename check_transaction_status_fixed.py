import sys
import asyncio
sys.path.insert(0, 'apex')
from web3 import Web3
from apex_identity import APEXIdentity

async def main():
    try:
        identity = APEXIdentity()
        
        print("TRANSACTION STATUS CHECK")
        print("=" * 50)
        
        # Transaction hashes to check
        tx_hashes = [
            "a1a9c7008c69b3ad2d429ba577fc20bac92e80ad6326816880d66c7e54cd7ce8",
            "a988e0f6c0b12a81d6b248ab1a02cdd07e5461e2559e6eeb700604e60d392a23"
        ]
        
        print(f"Checking {len(tx_hashes)} transactions...")
        
        for i, tx_hash in enumerate(tx_hashes, 1):
            print(f"\n--- Transaction {i} ---")
            print(f"Hash: {tx_hash}")
            print(f"Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
            
            try:
                # Get transaction receipt
                receipt = identity.w3.eth.get_transaction_receipt(tx_hash)
                
                if receipt:
                    print(f"Status: CONFIRMED")
                    print(f"Block Number: {receipt.blockNumber}")
                    print(f"Gas Used: {receipt.gasUsed}")
                    print(f"Transaction Status: {'SUCCESS' if receipt.status == 1 else 'FAILED'}")
                    
                    # Check for TradeApproved events
                    approved = False
                    for log in receipt.logs:
                        if log.address.lower() == identity.risk_router.address.lower():
                            try:
                                if len(log.topics) >= 1:
                                    topic0 = log.topics[0].hex()
                                    if topic0.startswith('0x8c'):
                                        approved = True
                                        print(f"Trade Event: TRADE APPROVED")
                                        break
                            except:
                                pass
                    
                    if not approved:
                        print(f"Trade Event: No approval detected yet")
                        
                else:
                    print(f"Status: NOT FOUND")
                    
            except Exception as e:
                print(f"Error checking transaction: {e}")
        
        # Check current agent status
        print(f"\n--- AGENT STATUS ---")
        try:
            status = await identity.get_status()
            print(f"Agent ID: {status['agent_id']}")
            print(f"Validation Score: {status['validation_score']}")
            print(f"Reputation Score: {status['reputation_score']}")
            print(f"Operator Balance: {status['operator_balance_eth']:.6f} ETH")
            
        except Exception as e:
            print(f"Error getting agent status: {e}")
        
        print(f"\n--- LEADERBOARD POSITION ---")
        print("Note: Cannot directly access leaderboard from blockchain")
        print("Please check LabLab.ai hackathon leaderboard for current position")
        print("Expected improvement with score=95 checkpoints")
        
        print(f"\n--- RECOMMENDATIONS ---")
        print("1. Check Etherscan links above for transaction details")
        print("2. Monitor LabLab.ai leaderboard for position changes")
        print("3. Validation score should improve with score=95 checkpoints")
        print("4. Submit more quality trades if validation score < 95")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
