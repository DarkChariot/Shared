"""
Simple CloudWatch custom widget Lambda

Renders a small table with these columns: client, instance, browser session.
The Browser Session column contains a button (anchor) that opens the CloudWatch
console/session URL for that row.

This Lambda returns an HTML fragment (string) suitable for use as the body of a
CloudWatch custom widget backed by a Lambda function.
"""

import json
import boto3

ROWS = [
  {"id": 1, "client": "TestClient A", "instance": "i-0abcd1111efgh2222"},
  {"id": 2, "client": "TestClient B", "instance": "i-0abcd3333ijkl4444"},
  {"id": 3, "client": "TestClient C", "instance": "i-0abcd5555mnop6666"},
]


def lambda_handler(event, context):
  """Lambda handler that returns an HTML fragment for the widget.

  If the CloudWatch widget calls the function with {"describe": true},
  return a small markdown description (used by the console).
  """

  if event.get("describe"):
    return {"markdown": "### Client Sessions\nShows client, instance and a CloudWatch session button."}

  # If invoked by a cwdb-action, the event may include action/instance params.
  # Support receiving either top-level event keys or widgetContext.params.
  widget_ctx = event.get('widgetContext', {}) if isinstance(event, dict) else {}
  params = widget_ctx.get('params', {}) if isinstance(widget_ctx, dict) else {}
  action = event.get('action') or params.get('action')
  instance_param = event.get('instance') or params.get('instance')
  # If rowId is provided instead of instance, resolve instance from ROWS
  row_id = event.get('rowId') or params.get('rowId')
  if not instance_param and row_id is not None:
    try:
      rid_val = int(row_id)
    except Exception:
      rid_val = row_id
    for r in ROWS:
      if r.get('id') == rid_val:
        instance_param = r.get('instance')
        break

  if action == 'start_ssm' and instance_param:
    try:
      ssm = boto3.client('ssm')
      resp = ssm.start_session(Target=instance_param)
      session_id = resp.get('SessionId')
      stream_url = resp.get('StreamUrl')
      token = resp.get('TokenValue')
      endpoint_arn = getattr(context, 'invoked_function_arn', '')
      return (
        f"<div style='padding:16px'>"
        f"<h3 style='color:green'>SSM Session Started</h3>"
        f"<p><b>Instance:</b> {instance_param}</p>"
        f"<p><b>SessionId:</b> {session_id}</p>"
        f"<p><b>StreamUrl:</b> {stream_url}</p>"
        f"<p class='small'>To connect to the session, use the AWS CLI Session Manager plugin or the Session Manager console. This Lambda only starts the session.</p>"
        f"<a class='btn'>Back</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{}}</cwdb-action></div>"
      )
    except Exception as e:
      endpoint_arn = getattr(context, 'invoked_function_arn', '')
      return (
        f"<div style='padding:16px'>"
        f"<h3 style='color:crimson'>Failed to start SSM session</h3>"
        f"<p>{str(e)}</p>"
        f"<a class='btn'>Back</a><cwdb-action action='call' endpoint='{endpoint_arn}'>{{}}</cwdb-action></div>"
      )

  # Build table HTML
  html = (
    "<div style='padding:10px;font-family:Arial,Helvetica,sans-serif'>"
    "<h3 style='margin:0 0 8px 0'>Client Sessions</h3>"
    "<table style='border-collapse:collapse;width:100%'>"
    "<thead>"
    "<tr>"
    "<th style='padding:8px;border:1px solid #ddd;text-align:left'>Client</th>"
    "<th style='padding:8px;border:1px solid #ddd;text-align:left'>Instance</th>"
    "<th style='padding:8px;border:1px solid #ddd;text-align:left'>Browser Session</th>"
    "</tr>"
    "</thead>"
    "<tbody>"
  )

  for r in ROWS:
    client = r.get('client', '')
    instance = r.get('instance', '')
    rid = r.get('id')
    # Build a cwdb-action payload that will call this Lambda with action=start_ssm
    # Send only the rowId; the Lambda will resolve the instance from its data
    payload = json.dumps({"action": "start_ssm", "rowId": rid})
    # Use literal {endpoint} placeholder; CloudWatch replaces it with the invoking lambda ARN
    btn = (
      f"<a class='btn' style='display:inline-block;padding:6px 10px;background:#0073bb;color:#fff;text-decoration:none;border-radius:4px'>Start SSM</a>"
      f"<cwdb-action action='call' endpoint='{{endpoint}}'>{payload}</cwdb-action>"
    )
    html += (
      f"<tr>"
      f"<td style='padding:8px;border:1px solid #ddd'>{client}</td>"
      f"<td style='padding:8px;border:1px solid #ddd'>{instance}</td>"
      f"<td style='padding:8px;border:1px solid #ddd'>{btn}</td>"
      f"</tr>"
    )

  html += "</tbody></table></div>"
  return html