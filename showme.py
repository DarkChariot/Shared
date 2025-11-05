import json
import boto3

def lambda_handler(event, context):
    # Extract values
    client = event.get("client")
    requester_email = event.get("requester_email")
    approver_email = event.get("approver_email")
    
    # Set variable based on requester
    if requester_email == "john.doe@example.com":
        variable = "special_value_for_john"
    elif requester_email == "jane.smith@example.com":
        variable = "special_value_for_jane"
    else:
        variable = "default_value"
    
    # Send SNS email
    sns = boto3.client('sns')
    
    message = f"""
    New request from {client}
    
    Requester: {requester_email}
    Approver: {approver_email}
    Account: {event.get("account")}
    MFA Code: {event.get("mfa_code")}
    """
    
    try:
        response = sns.publish(
            TargetArn=approver_email,
            Message=message,
            Subject=f'Request from {client}'
        )
        email_result = f"Email sent to {approver_email}: {response['MessageId']}"
    except Exception as e:
        email_result = f"Email to {approver_email} failed: {str(e)}"
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "ok": True,
            "client": client,
            "variable_set": variable,
            "email_result": email_result,
            "received": {
                "client": event.get("client"),
                "account": event.get("account"),
                "requester_email": event.get("requester_email"),
                "approver_email": event.get("approver_email"),
                "mfa_code": event.get("mfa_code"),
            }
        })
    }
