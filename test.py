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
    
    # Try both locations for action and rowId
    action = event.get("action") or params.get("action")
    rid = event.get("rowId") or params.get("rowId")
    
    if action == "confirm_request" and rid:
        # Get payload from button data or forms
        if event.get("payload"):
            payload = json.loads(event.get("payload"))
        else:
            payload = {
                "client": forms.get(f"client_{rid}", ""),
                "account": forms.get(f"account_{rid}", ""),
                "requester_email": forms.get(f"requester_{rid}", ""),
                "approver_email": forms.get(f"approver_{rid}", ""),
                "mfa_code": forms.get(f"mfa_{rid}", "")
            }
        try:
            response = boto3.client('lambda').invoke(
                FunctionName=REQUEST_LAMBDA_ARN,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            result = json.loads(response['Payload'].read())
        except Exception as e:
            result = {"error": f"Lambda invoke failed: {str(e)}"}
        
        return f"<div style='padding:20px;'><h3 style='color:green;'>Request Sent!</h3><div style='background:#f0f8f0;padding:10px;'><b>Payload:</b> {payload}<br><b>Result:</b> {result}</div><a class='btn'>Back</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{}}</cwdb-action></div>"
    
    if action == "request" and rid:
        payload = {
            "client": forms.get(f"client_{rid}", ""),
            "account": forms.get(f"account_{rid}", ""),
            "requester_email": forms.get(f"requester_{rid}", ""),
            "approver_email": forms.get(f"approver_{rid}", ""),
            "mfa_code": forms.get(f"mfa_{rid}", "")
        }
        # Find approver name from email
        approver_name = next((a['name'] for a in APPROVERS if a['email'] == payload['approver_email']), payload['approver_email'])
        
        return f"<div style='padding:20px;'><h3>Confirm Request</h3><div style='background:#f9f9f9;padding:15px;border:1px solid #ddd;'><h4>Please confirm the following details:</h4><p><b>Client:</b> {payload['client']}</p><p><b>Account:</b> {payload['account']}</p><p><b>Requester Email:</b> {payload['requester_email']}</p><p><b>Approver:</b> {approver_name}</p><p><b>MFA Code:</b> {payload['mfa_code']}</p></div><div style='margin-top:15px;'><a class='btn btn-success' style='margin-right:10px;'>Confirm Request</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{\"action\": \"confirm_request\", \"rowId\": {rid}, \"payload\": {json.dumps(payload)}}}</cwdb-action><a class='btn btn-secondary'>Cancel</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{}}</cwdb-action></div></div>"
    
    if action == "confirm_secret" and rid:
        # Get payload from button data or forms
        if event.get("payload"):
            payload = json.loads(event.get("payload"))
        else:
            payload = {
                "client": forms.get(f"client_{rid}", ""),
                "account": forms.get(f"account_{rid}", ""),
                "requester_email": forms.get(f"requester_{rid}", ""),
                "approver_email": forms.get(f"approver_{rid}", ""),
                "mfa_code": forms.get(f"mfa_{rid}", "")
            }
        try:
            response = boto3.client('lambda').invoke(
                FunctionName=SECRET_LAMBDA_ARN,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            result = json.loads(response['Payload'].read())
        except Exception as e:
            result = {"error": f"Lambda invoke failed: {str(e)}"}
        
        return f"<div style='padding:20px;'><h3 style='color:green;'>Secret Sent!</h3><div style='background:#f0f8f0;padding:10px;'><b>Payload:</b> {payload}<br><b>Result:</b> {result}</div><a class='btn'>Back</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{}}</cwdb-action></div>"
    
    if action == "secret" and rid:
        payload = {
            "client": forms.get(f"client_{rid}", ""),
            "account": forms.get(f"account_{rid}", ""),
            "requester_email": forms.get(f"requester_{rid}", ""),
            "approver_email": forms.get(f"approver_{rid}", ""),
            "mfa_code": forms.get(f"mfa_{rid}", "")
        }
        # Find approver name from email
        approver_name = next((a['name'] for a in APPROVERS if a['email'] == payload['approver_email']), payload['approver_email'])
        
        return f"<div style='padding:20px;'><h3>Confirm Secret Request</h3><div style='background:#f9f9f9;padding:15px;border:1px solid #ddd;'><h4>Please confirm the following details:</h4><p><b>Client:</b> {payload['client']}</p><p><b>Account:</b> {payload['account']}</p><p><b>Requester Email:</b> {payload['requester_email']}</p><p><b>Approver:</b> {approver_name}</p><p><b>MFA Code:</b> {payload['mfa_code']}</p></div><div style='margin-top:15px;'><a class='btn btn-success' style='margin-right:10px;'>Confirm Secret</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{\"action\": \"confirm_secret\", \"rowId\": {rid}, \"payload\": {json.dumps(payload)}}}</cwdb-action><a class='btn btn-secondary'>Cancel</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{}}</cwdb-action></div></div>"
    

    
    # Debug: Add simple test button
    debug_test = f"<div style='padding:10px;background:lightcoral;'><h4>Button Test</h4><p>Action: {action}, RID: {rid}, Event: {event}</p><a class='btn'>Test Button</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{\"test\": \"button_clicked\"}}</cwdb-action></div>"
    
    # Render table
    out = debug_test + "<div style='padding:10px;'><h3>Request/Secret Dashboard</h3><table style='border-collapse:collapse;width:100%;'><thead><tr><th style='padding:8px;border:1px solid #ddd;'>Client</th><th style='padding:8px;border:1px solid #ddd;'>Account</th><th style='padding:8px;border:1px solid #ddd;'>Requester</th><th style='padding:8px;border:1px solid #ddd;'>Approver</th><th style='padding:8px;border:1px solid #ddd;'>Request</th><th style='padding:8px;border:1px solid #ddd;'>MFA</th><th style='padding:8px;border:1px solid #ddd;'>Secret</th></tr></thead><tbody>"
    
    for row in ROWS:
        rid = row["id"]
        out += f"<tr><td style='padding:8px;border:1px solid #ddd;'>{row['client']}<input type='hidden' name='client_{rid}' value='{row['client']}'/></td><td style='padding:8px;border:1px solid #ddd;'>{row['account']}<input type='hidden' name='account_{rid}' value='{row['account']}'/></td><td style='padding:8px;border:1px solid #ddd;'><select name='requester_{rid}' style='width:100%;'><option value=''>-- Select Requester --</option>" + "".join([f"<option value='{req['email']}'>{req['name']}</option>" for req in REQUESTERS]) + f"</select></td><td style='padding:8px;border:1px solid #ddd;'><select name='approver_{rid}' style='width:100%;'><option value=''>-- Select --</option>"
        
        for approver in APPROVERS:
            out += f"<option value='{approver['email']}'>{approver['name']}</option>"
        
        out += f"</select></td><td style='padding:8px;border:1px solid #ddd;'><a class='btn btn-primary'>Request</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{\"action\": \"request\", \"rowId\": {rid}}}</cwdb-action></td><td style='padding:8px;border:1px solid #ddd;'><input name='mfa_{rid}' placeholder='123456' style='width:100%;'/></td><td style='padding:8px;border:1px solid #ddd;'><a class='btn btn-secondary'>Secret</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{\"action\": \"secret\", \"rowId\": {rid}}}</cwdb-action></td></tr>"
    
    out += "</tbody></table></div>"
    return out