# chain_connect.py
import json, os
from web3 import Web3

GANACHE_RPC = os.getenv("GANACHE_RPC", "http://127.0.0.1:7545")  # or 8545 if that’s your port
w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))
assert w3.is_connected(), "Web3 not connected – is Ganache running?"

# Load Truffle artifact
with open("build/contracts/FraudDetection.json") as f:
    artifact = json.load(f)

# Use Ganache network id (5777) or detect dynamically
network_id = list(artifact["networks"].keys())[0]  # assumes only Ganache network deployed
contract_address = Web3.to_checksum_address(artifact["networks"][network_id]["address"])
contract_abi = artifact["abi"]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# default account for sending transactions (first Ganache account)
default_account = w3.eth.accounts[0]

