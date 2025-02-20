import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration des clés API
airtable_api_key = os.getenv("AIRTABLE_API_KEY")
airtable_base_id = os.getenv("AIRTABLE_BASE_ID")
airtable_table_name = "messages_slack"
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")

def save_to_airtable(user, message, timestamp):
    url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_name}"
    headers = {
        "Authorization": f"Bearer {airtable_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [
            {
                "fields": {
                    "user": user,
                    "message": message,
                    "timestamp": timestamp
                }
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

@app.route("/slack", methods=["POST"])
def slack_event():
    event_data = request.json
    
    if "challenge" in event_data:
        return jsonify({"challenge": event_data["challenge"]})
    
    if "event" in event_data:
        event = event_data["event"]
        
        if event.get("type") == "message" and "subtype" not in event:
            user = event.get("user", "unknown")
            message = event.get("text", "")
            timestamp = datetime.utcnow().isoformat()
            save_to_airtable(user, message, timestamp)
            return jsonify({"status": "Message saved"})
    
    return jsonify({"status": "Ignored"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
