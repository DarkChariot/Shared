import json
import boto3

ROWS = [
    {"id": 1, "client": "TestClient A", "account": "TestAccount A"},
    {"id": 2, "client": "TestClient B", "account": "TestAccount B"},
    {"id": 3, "client": "TestClient C", "account": "TestAccount C"},
]

APPROVERS = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]

REQUESTERS = [
    {"name": "John Doe", "email": "john.doe@example.com"},
    {"name": "Jane Smith", "email": "jane.smith@example.com"},
    {"name": "Mike Wilson", "email": "mike.wilson@example.com"},
]

REQUEST_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:request-handler"
SECRET_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:secret-handler"

def lambda_handler(event, context):
    if event.get("describe"):
        return {"markdown": "### Request/Secret Dashboard"}
    
    endpoint_arn = getattr(context, "invoked_function_arn", "")
    wc = event.get("widgetContext", {})
    params = wc.get("params", {})
    forms = wc.get("forms", {}).get("all", {})
    action = params.get("action")
    rid = params.get("rowId")
    

    
    # Render table
    out = "<div style='padding:10px;'><h3>Request/Secret Dashboard</h3><table style='border-collapse:collapse;width:100%;'><thead><tr><th style='padding:8px;border:1px solid #ddd;'>Client</th><th style='padding:8px;border:1px solid #ddd;'>Account</th><th style='padding:8px;border:1px solid #ddd;'>Requester</th><th style='padding:8px;border:1px solid #ddd;'>Approver</th><th style='padding:8px;border:1px solid #ddd;'>Request</th><th style='padding:8px;border:1px solid #ddd;'>MFA</th><th style='padding:8px;border:1px solid #ddd;'>Secret</th></tr></thead><tbody>"
    
    for row in ROWS:
        rid = row["id"]
        out += f"<tr><td style='padding:8px;border:1px solid #ddd;'>{row['client']}<input type='hidden' name='client_{rid}' value='{row['client']}'/></td><td style='padding:8px;border:1px solid #ddd;'>{row['account']}<input type='hidden' name='account_{rid}' value='{row['account']}'/></td><td style='padding:8px;border:1px solid #ddd;'><select name='requester_{rid}' style='width:100%;'><option value=''>-- Select Requester --</option>" + "".join([f"<option value='{req['email']}'>{req['name']}</option>" for req in REQUESTERS]) + "</select></td><td style='padding:8px;border:1px solid #ddd;'><select name='approver_{rid}' style='width:100%;'><option value=''>-- Select --</option>"
        
        for approver in APPROVERS:
            out += f"<option value='{approver['email']}'>{approver['name']}</option>"
        
        out += f"</select></td><td style='padding:8px;border:1px solid #ddd;'><a class='btn btn-primary'>Request</a><cwdb-action action='call' endpoint='{REQUEST_LAMBDA_ARN}'>{{\"client\": \"{row['client']}\", \"account\": \"{row['account']}\"}}</cwdb-action></td><td style='padding:8px;border:1px solid #ddd;'><input name='mfa_{rid}' placeholder='123456' style='width:100%;'/></td><td style='padding:8px;border:1px solid #ddd;'><a class='btn btn-secondary'>Secret</a><cwdb-action action='call' endpoint='{SECRET_LAMBDA_ARN}'>{{\"client\": \"{row['client']}\", \"account\": \"{row['account']}\"}}</cwdb-action></td></tr>"
    
    out += "</tbody></table></div>"
    return out