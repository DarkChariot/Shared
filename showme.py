# secret_lambda_function.py
import json

def lambda_handler(event, context):
    # Expected from widget-lambda: + mfa_code
    return {
        "statusCode": 200,
        "body": json.dumps({
            "ok": True,
            "received": {
                "client": event.get("client"),
                "account": event.get("account"),
                "requester_email": event.get("requester_email"),
                "approver_email": event.get("approver_email"),
                "mfa_code": event.get("mfa_code"),
            }
        })
    }
