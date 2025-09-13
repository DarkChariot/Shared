# request_lambda_function.py
import json

def lambda_handler(event, context):
    # Expected from widget-lambda: client, account, requester_email, approver_email
    return {
        "statusCode": 200,
        "body": json.dumps({
            "ok": True,
            "received": {
                "client": event.get("client"),
                "account": event.get("account"),
                "requester_email": event.get("requester_email"),
                "approver_email": event.get("approver_email"),
            }
        })
    }
