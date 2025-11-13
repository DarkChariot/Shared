"""CloudWatch custom widget Lambda that renders a client sessions table."""

import json
import sys

ROWS = [
    {"id": 1, "client": "TestClient A", "instance": "i-0abcd1111efgh2222"},
    {"id": 2, "client": "TestClient B", "instance": "i-0abcd3333ijkl4444"},
    {"id": 3, "client": "TestClient C", "instance": "i-0abcd5555mnop6666"},
]

# Handler Lambda ARN (replace with your actual handler Lambda ARN)
HANDLER_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:ssm-session-handler"


def debug_log(msg, data=None):
    """Log debug information to CloudWatch and console."""
    log_msg = f"[DEBUG] {msg}"
    if data is not None:
        log_msg += f" | {json.dumps(data, indent=2, default=str)}"
    print(log_msg, file=sys.stderr)
    return log_msg


def lambda_handler(event, context):
    """CloudWatch widget: renders a table of client sessions with Start Session buttons.
    
    Buttons use cwdb-action to invoke a separate handler Lambda (HANDLER_LAMBDA_ARN)
    with the instance ID.
    """
    debug_log("=== WIDGET LAMBDA INVOKED ===")
    debug_log("Event received", event)
    debug_log("Context attributes", {
        "function_name": context.function_name,
        "function_version": context.function_version,
        "invoked_function_arn": context.invoked_function_arn,
        "memory_limit_in_mb": context.memory_limit_in_mb,
        "request_id": context.request_id,
    })
    
    # Check if this is a describe request from CloudWatch
    if event.get("describe"):
        debug_log("Describe request detected")
        return {"markdown": "### Client Sessions\nClick Start Session to begin an SSM session."}
    
    debug_log("Building table HTML for widget display")
    debug_log(f"Total rows to render: {len(ROWS)}")
    
    # Build table HTML
    html = (
        "<div style='padding:10px;font-family:Arial,sans-serif'>"
        "<h3>Client Sessions</h3>"
        "<table style='border-collapse:collapse;width:100%'>"
        "<tr><th style='padding:8px;border:1px solid #ddd;text-align:left'>Client</th>"
        "<th style='padding:8px;border:1px solid #ddd;text-align:left'>Instance</th>"
        "<th style='padding:8px;border:1px solid #ddd;text-align:left'>Start Session</th></tr>"
    )
    
    for idx, row in enumerate(ROWS):
        client = row.get('client', '')
        instance = row.get('instance', '')
        debug_log(f"Processing row {idx + 1}", {"client": client, "instance": instance})
        
        payload = json.dumps({"instance": instance})
        debug_log(f"Row {idx + 1} payload created", {"payload": payload})
        
        btn = (
            f"<a class='btn' style='display:inline-block;padding:6px 10px;background:#0073bb;color:#fff;"
            f"text-decoration:none;border-radius:4px;cursor:pointer'>Start</a>"
            f"<cwdb-action action='call' endpoint='{HANDLER_LAMBDA_ARN}'>{payload}</cwdb-action>"
        )
        debug_log(f"Row {idx + 1} button created", {
            "handler_arn": HANDLER_LAMBDA_ARN,
            "button_length": len(btn)
        })
        
        html += (
            f"<tr><td style='padding:8px;border:1px solid #ddd'>{client}</td>"
            f"<td style='padding:8px;border:1px solid #ddd'>{instance}</td>"
            f"<td style='padding:8px;border:1px solid #ddd'>{btn}</td></tr>"
        )
    
    html += "</table></div>"
    
    debug_log("Widget HTML generated successfully", {
        "html_length": len(html),
        "handler_arn": HANDLER_LAMBDA_ARN
    })
    debug_log("=== WIDGET LAMBDA RETURNING ===")
    
    return html