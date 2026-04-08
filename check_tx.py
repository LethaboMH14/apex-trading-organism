from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))
tx_hash = '0x6ac256a9966e5d0dd476b828265ff2dedba32063db21980ace92f481242d4f66'

try:
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    if receipt:
        status = "SUCCESS" if receipt["status"] == 1 else "FAILED"
        print(f"Status: {status}")
        print(f"Block: {receipt['blockNumber']}")
        print(f"Gas used: {receipt['gasUsed']}")
        print(f"Explorer: https://sepolia.etherscan.io/tx/{tx_hash}")
    else:
        print("Transaction not yet mined")
except Exception as e:
    print(f"Error: {e}")
    print("Checking transaction directly...")
    try:
        tx = w3.eth.get_transaction(tx_hash)
        print(f"Transaction found: {tx['hash'].hex()}")
        print(f"From: {tx['from']}")
        print(f"To: {tx['to']}")
        print(f"Gas limit: {tx['gas']}")
    except Exception as e2:
        print(f"Could not get transaction: {e2}")
