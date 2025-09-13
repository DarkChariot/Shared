import json
import boto3
from typing import Any, Dict, List

# Configuration
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

TARGET_REQUEST_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:request-handler"
TARGET_SECRET_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:secret-handler"

def _get_form_data(forms, rid):
    client = forms.get(f"client_{rid}", "")
    account = forms.get(f"account_{rid}", "")
    email = forms.get(f"email_{rid}", "")
    approver = forms.get(f"approver_{rid}", "")
    mfa = forms.get(f"mfa_{rid}", "")
    return client, account, email, approver, mfa

def _invoke_lambda(arn, payload):
    boto3.client('lambda').invoke(
        FunctionName=arn,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )

def _render_table(endpoint_arn):
    out = "<div style='padding:10px;'>"
    out += "<h3>Request/Secret Dashboard</h3>"
    out += "<table style='border-collapse:collapse;width:100%;'>"
    out += "<thead><tr>"
    out += "<th style='padding:8px;border:1px solid #ddd;'>Client</th>"
    out += "<th style='padding:8px;border:1px solid #ddd;'>Account Name</th>"
    out += "<th style='padding:8px;border:1px solid #ddd;'>Requester Email</th>"
    out += "<th style='padding:8px;border:1px solid #ddd;'>Approver</th>"
    out += "<th style='padding:8px;border:1px solid #ddd;'>Request</th>"
    out += "<th style='padding:8px;border:1px solid #ddd;'>MFA Code</th>"
    out += "<th style='padding:8px;border:1px solid #ddd;'>Secret</th>"
    out += "</tr></thead><tbody>"

    for row in ROWS:
        rid = row["id"]
        out += "<tr>"
        
        # Client (hardcoded)
        out += f"<td style='padding:8px;border:1px solid #ddd;'>{row['client']}"
        out += f"<input type='hidden' name='client_{rid}' value='{row['client']}'/></td>"
        
        # Account Name (hardcoded)
        out += f"<td style='padding:8px;border:1px solid #ddd;'>{row['account']}"
        out += f"<input type='hidden' name='account_{rid}' value='{row['account']}'/></td>"
        
        # Requester Email (input field)
        out += f"<td style='padding:8px;border:1px solid #ddd;'>"
        out += f"<input type='email' name='email_{rid}' placeholder='user@example.com' style='width:100%;'/></td>"
        
        # Approver (dropdown)
        out += f"<td style='padding:8px;border:1px solid #ddd;'>"
        out += f"<select name='approver_{rid}' style='width:100%;'>"
        out += "<option value=''>-- Select Approver --</option>"
        for approver in APPROVERS:
            out += f"<option value='{approver['email']}'>{approver['name']}</option>"
        out += "</select></td>"
        
        # Request Button
        out += f"<td style='padding:8px;border:1px solid #ddd;'>"
        out += f'<a class="btn btn-primary">Request</a><cwdb-action action="call" endpoint="{TARGET_REQUEST_LAMBDA_ARN}">{{"client": "TestClient", "account": "TestAccount", "requester_email": "test@example.com", "approver_email": "alice@example.com", "mfa_code": "123456"}}</cwdb-action>'
        out += "</td>"     
        # MFA Code (input field)
        out += f"<td style='padding:8px;border:1px solid #ddd;'>"
        out += f"<input name='mfa_{rid}' placeholder='123456' style='width:100%;'/></td>"
        
        # Secret Button
        out += f"<td style='padding:8px;border:1px solid #ddd;'>"
        out += f'<a class="btn btn-secondary">Secret</a><cwdb-action action="call" endpoint="{TARGET_SECRET_LAMBDA_ARN}">{{"client": "TestClient", "account": "TestAccount", "requester_email": "test@example.com", "approver_email": "alice@example.com", "mfa_code": "123456"}}</cwdb-action>'
        out += "</td>"
        
        out += "</tr>"
    
    out += "</tbody></table></div>"
    return out

def _render_success(message, data):
    out = "<div style='padding:20px;'>"
    out += f"<h3 style='color:green;'>{message}</h3>"
    out += "<div style='background:#f0f8f0;padding:10px;border-radius:5px;'>"
    for key, value in data.items():
        out += f"<div><b>{key}:</b> {value}</div>"
    out += "</div>"
    out += "<div style='margin-top:10px;'>"
    out += '<a class="btn">Back to Dashboard</a><cwdb-action action="call" endpoint="">{"action": "back"}</cwdb-action>'
    out += "</div></div>"
    return out

def lambda_handler(event, context):
    if event.get("describe"):
        return {
            "markdown": "### Request/Secret Dashboard\nManage requests and secrets with MFA verification."
        }
    
    endpoint_arn = getattr(context, "invoked_function_arn", "")
    wc = event.get("widgetContext", {})
    params = wc.get("params", {})
    forms = wc.get("forms", {}).get("all", {})
    action = params.get("action")
    rid = params.get("rowId")
    
    if not action or action == "back":
        return _render_table(endpoint_arn)
    
    if action == "request" and rid:
        client, account, email, approver, mfa = _get_form_data(forms, rid)
        # Debug: show what we received
        debug_info = f"<div>Action: {action}, RID: {rid}, Forms: {forms}</div>"
        payload = {
            "client": client,
            "account": account,
            "requester_email": email,
            "approver_email": approver,
            "mfa_code": mfa
        }
        _invoke_lambda(TARGET_REQUEST_LAMBDA_ARN, payload)
        return debug_info + _render_success("Request Sent Successfully!", payload)
    
    if action == "secret" and rid:
        client, account, email, approver, mfa = _get_form_data(forms, rid)
        # Debug: show what we received
        debug_info = f"<div>Action: {action}, RID: {rid}, Forms: {forms}</div>"
        payload = {
            "client": client,
            "account": account,
            "requester_email": email,
            "approver_email": approver,
            "mfa_code": mfa
        }
        _invoke_lambda(TARGET_SECRET_LAMBDA_ARN, payload)
        return debug_info + _render_success("Secret Request Sent Successfully!", payload)
    
    return _render_table(endpoint_arn)