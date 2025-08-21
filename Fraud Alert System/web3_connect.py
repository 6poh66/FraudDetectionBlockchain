# web3_connect.py
from web3 import Web3
import json
from pathlib import Path

# 1) Connect to Ganache (adjust port if your Ganache uses 8545)
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise RuntimeError(f"Web3 not connected to {GANACHE_URL}")

# 2) Load Truffle artifact (ABI + networks)
artifact_path = Path("build/contracts/FraudDetection.json")
with open(artifact_path, "r") as f:
    artifact = json.load(f)

abi = artifact["abi"]

# 3) Get deployed address from the artifact (network id 5777 on Ganache)
networks = artifact.get("networks", {})
if "5777" not in networks or "address" not in networks["5777"]:
    raise RuntimeError("FraudDetection not found in networks[5777]. Did you migrate on Ganache?")
contract_address = Web3.to_checksum_address(networks["5777"]["address"])

# 4) Build contract instance
fraud_contract = w3.eth.contract(address=contract_address, abi=abi)

# 5) Pick a sender account
# On Ganache, accounts are unlocked, so you can send with just 'from'
default_from = w3.eth.accounts[0]  # first Ganache account

def send_fraud_alert(reason: str, request_id: bytes = b""):
    """
    Calls FraudDetection.triggerAlert(string reason, bytes32 requestId)
    Emits FraudAlert(triggeredBy, reason, timestamp, requestId)
    """
    if not isinstance(request_id, (bytes, bytearray)) or len(request_id) not in (0, 32):
        # Normalize to 32 bytes
        request_id = (request_id or b"").ljust(32, b"\x00")

    tx = fraud_contract.functions.triggerAlert(reason, request_id).transact({
        "from": default_from
        # You can set "gas" or "maxFeePerGas" if you want, Ganache will auto-fill
    })
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    print("[CHAIN] FraudAlert sent. Tx:", receipt.transactionHash.hex())
    return receipt

