from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import pickle
import time
from web3 import Web3
import json
from chain_connect import w3, contract, default_account, contract_address

app = Flask(__name__, static_url_path="/static", static_folder="static")
CORS(app)

# ---- ML bits ----
with open("random_forest_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

THRESHOLD = 0.10  # demo threshold

# in-memory status (for GUI)
last_status = {
    "last_tx": None,
    "last_reason": None,
    "last_score": None,
    "last_features": None,
    "last_flag": None,
    "updated_at": None,
}

def send_fraud_alert(reason: str, *, features=None, score=None):
    # make a deterministic 32-byte id (bytes32) from the payload
    payload = {"reason": reason, "score": score, "features": features}
    alert_id = Web3.keccak(text=json.dumps(payload, sort_keys=True))  # bytes32

    tx = contract.functions.triggerAlert(reason, alert_id).transact({"from": default_account})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    print("[CHAIN] FraudAlert sent. Tx:", receipt.transactionHash.hex())
    return receipt.transactionHash.hex()

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    features = np.array(data["features"]).reshape(1, -1)
    features_scaled = scaler.transform(features)
    fraud_proba = float(model.predict_proba(features_scaled)[0][1])

    flagged = fraud_proba < THRESHOLD
    print(f"[INFO] Fraud probability: {fraud_proba:.4f}, Threshold: {THRESHOLD}, Flagged: {flagged}")

    tx_hash = None
    if flagged:
        tx_hash = send_fraud_alert("⚠️ Suspicious transaction detected")

    # update dashboard state
    last_status.update({
        "last_tx": tx_hash,
        "last_reason": "⚠️ Suspicious transaction detected" if flagged else None,
        "last_score": round(fraud_proba, 4),
        "last_features": data["features"],
        "last_flag": int(flagged),
        "updated_at": int(time.time()),
    })

    return jsonify({
    "fraud": int(flagged),        # 1 = alert
    "flagged": int(not flagged),      # 0 = fraud/suspicious, 1 = safe
    "score": round(fraud_proba, 3),
    "threshold": THRESHOLD,
    "contract": contract_address,
    "tx_hash": tx_hash,
})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "contract": contract_address,
        "threshold": THRESHOLD,
        **last_status
    })

@app.route("/events", methods=["GET"])
def events():
    """
    Return last N FraudAlert events from chain.
    """
    # Pull recent blocks for demo (last ~1000 blocks)
    latest = w3.eth.block_number
    frm = max(0, latest - 1000)
    to  = latest

    event_signature = contract.events.FraudAlert.create_filter(fromBlock=frm, toBlock=to)
    logs = event_signature.get_all_entries()

    out = []
    for ev in logs[-20:]:  # last 20
        out.append({
            "tx_hash": ev["transactionHash"].hex(),
            "triggeredBy": ev["args"]["triggeredBy"],
            "reason": ev["args"]["reason"],
            "timestamp": int(ev["args"]["timestamp"]),
            "blockNumber": ev["blockNumber"],
        })
    return jsonify({"events": out})

# Simple dashboard page
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(debug=True)

