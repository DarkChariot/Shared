"""CloudWatch custom widget Lambda that renders a client sessions table."""

import json

ROWS = [
    {"id": 1, "client": "TestClient A", "instance": "i-0abcd1111efgh2222"},
    {"id": 2, "client": "TestClient B", "instance": "i-0abcd3333ijkl4444"},
    {"id": 3, "client": "TestClient C", "instance": "i-0abcd5555mnop6666"},
]

# Handler Lambda ARN (replace with your actual handler Lambda ARN)
HANDLER_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:ssm-session-handler"


def lambda_handler(event, context):
    """CloudWatch widget: renders a table of client sessions with Start Session buttons.
    
    Buttons use cwdb-action to invoke a separate handler Lambda (HANDLER_LAMBDA_ARN)
    with the instance ID.
    """
    if event.get("describe"):
        return {"markdown": "### Client Sessions\nClick Start Session to begin an SSM session."}
    
    # Build table HTML
    html = (
        "<div style='padding:10px;font-family:Arial,sans-serif'>"
        "<h3>Client Sessions</h3>"
        "<table style='border-collapse:collapse;width:100%'>"
        "<tr><th style='padding:8px;border:1px solid #ddd;text-align:left'>Client</th>"
        "<th style='padding:8px;border:1px solid #ddd;text-align:left'>Instance</th>"
        "<th style='padding:8px;border:1px solid #ddd;text-align:left'>Start Session</th></tr>"
    )
    
    for row in ROWS:
        client = row.get('client', '')
        instance = row.get('instance', '')
        payload = json.dumps({"instance": instance})
        btn = (
            f"<a class='btn' style='display:inline-block;padding:6px 10px;background:#0073bb;color:#fff;"
            f"text-decoration:none;border-radius:4px;cursor:pointer'>Start</a>"
            f"<cwdb-action action='call' endpoint='{HANDLER_LAMBDA_ARN}'>{payload}</cwdb-action>"
        )
        html += (
            f"<tr><td style='padding:8px;border:1px solid #ddd'>{client}</td>"
            f"<td style='padding:8px;border:1px solid #ddd'>{instance}</td>"
            f"<td style='padding:8px;border:1px solid #ddd'>{btn}</td></tr>"
        )
    
    html += "</table></div>"
    return html