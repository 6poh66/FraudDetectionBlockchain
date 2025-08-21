# read_events.py
from web3_connect import w3, fraud_contract

event = fraud_contract.events.FraudAlert
logs = event().get_logs(fromBlock=0, toBlock='latest')

for l in logs:
    args = l['args']
    print("Alert:", {
        "triggeredBy": args["triggeredBy"],
        "reason": args["reason"],
        "timestamp": int(args["timestamp"]),
        "requestId": args.get("requestId", b"").hex()
    })

