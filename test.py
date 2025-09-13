# lambda_function.py  (Widget Lambda)
import html
import json
from typing import Optional, List, Dict, Any, Tuple
import boto3

# ---------------- CONFIG: set your target Lambda ARNs ----------------
TARGET_REQUEST_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:my-request-lambda"
TARGET_SECRET_LAMBDA_ARN  = "arn:aws:lambda:us-east-1:123456789012:function:my-secret-lambda"

lambda_client = boto3.client("lambda")

# ---------------- DYNAMIC ROWS (replace with your data source) -------
ROWS: List[Dict[str, Any]] = [
    {"id": 3001, "client": "TestClient A", "account": "TestUserA"},
    {"id": 3002, "client": "TestClient B", "account": "TestUserB"},
    {"id": 3003, "client": "TestClient C", "account": "TestUserC"},
]

# Approvers (names shown, email is the option value)
APPROVERS: List[Dict[str, str]] = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]

# ---------------- Helpers ----------------
def _esc(v: Any) -> str:
    return html.escape("" if v is None else str(v))

def _normalize_forms_all(forms_all: Any) -> List[Dict[str, Any]]:
    if isinstance(forms_all, dict):
        return [forms_all]
    if isinstance(forms_all, list):
        return [d for d in forms_all if isinstance(d, dict)]
    return []

def _keys_for_row(rid: int) -> Dict[str, str]:
    return {
        "client":   f"r_{rid}_client",     # hidden input (client text mirrored)
        "account":  f"r_{rid}_account",    # hidden input (account text mirrored)
        "email":    f"r_{rid}_email",      # requester email
        "approver": f"r_{rid}_approver",   # approver email (value)
        "mfa":      f"r_{rid}_mfa",        # mfa code
    }

def _extract_row(dicts: List[Dict[str, Any]], rid: int) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    k = _keys_for_row(rid)
    client = account = email = approver = mfa = None
    for d in dicts:
        if k["client"]   in d and client   is None: client   = d.get(k["client"])
        if k["account"]  in d and account  is None: account  = d.get(k["account"])
        if k["email"]    in d and email    is None: email    = d.get(k["email"])
        if k["approver"] in d and approver is None: approver = d.get(k["approver"])
        if k["mfa"]      in d and mfa      is None: mfa      = d.get(k["mfa"])
    return client, account, email, approver, mfa

def _invoke_lambda(function_arn: str, payload: Dict[str, Any]) -> None:
    # Use Event for async fire-and-forget; switch to RequestResponse for debugging
    lambda_client.invoke(
        FunctionName=function_arn,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )

# ---------------- Renderers ----------------
def _render_table(endpoint_arn: str) -> str:
    out  = "<div style='padding:10px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>Client • Account • Requester Email • Approver • Request • MFA • Secret</h3>"
    out += "<table style='border-collapse:collapse;width:100%;max-width:1600px;'>"
    out += ("<thead><tr>"
            "<th style='text-align:left;padding:6px 8px;'>Client</th>"
            "<th style='text-align:left;padding:6px 8px;'>Account Name</th>"
            "<th style='text-align:left;padding:6px 8px;'>Requester Email</th>"
            "<th style='text-align:left;padding:6px 8px;'>Approver</th>"
            "<th style='text-align:left;padding:6px 8px;'>Request</th>"
            "<th style='text-align:left;padding:6px 8px;'>MFA Code</th>"
            "<th style='text-align:left;padding:6px 8px;'>Secret</th>"
            "</tr></thead><tbody>")

    for r in ROWS:
        rid     = r["id"]
        client  = r.get("client", "")
        account = r.get("account", "")
        k       = _keys_for_row(rid)

        out += "<tr>"

        # Client (text) + hidden mirror
        out += f"<td style='padding:6px 8px;'><span>{_esc(client)}</span>"
        out += f"<input type='hidden' name='{_esc(k['client'])}' value='{_esc(client)}'/></td>"

        # Account (text) + hidden mirror
        out += f"<td style='padding:6px 8px;'><span>{_esc(account)}</span>"
        out += f"<input type='hidden' name='{_esc(k['account'])}' value='{_esc(account)}'/></td>"

        # Requester Email
        out += ("<td style='padding:6px 8px;'>"
                "<input type='email' name='{name}' placeholder='name@example.com' "
                "style='width:100%;max-width:260px;'/>"
                "</td>".format(name=_esc(k["email"])))

        # Approver dropdown (name shown, email as value)
        out += "<td style='padding:6px 8px;'><select name='{name}' style='width:100%;max-width:260px;'>".format(
            name=_esc(k["approver"])
        )
        out += "<option value='' selected>-- select approver --</option>"
        for a in APPROVERS:
            out += "<option value='{val}'>{label}</option>".format(val=_esc(a["email"]), label=_esc(a["name"]))
        out += "</select></td>"

        # Request button (calls THIS Lambda; handler invokes request target)
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn btn-primary'>Request</a>"
        out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "request", "rowId": {rid} }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn), rid=rid)
        out += "</td>"

        # MFA Code
        out += ("<td style='padding:6px 8px;'>"
                "<input name='{name}' placeholder='6-digit code' style='width:100%;max-width:160px;'/>"
                "</td>".format(name=_esc(k["mfa"])))

        # Secret button (calls THIS Lambda; handler invokes secret target)
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn'>Secret</a>"
        out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "secret", "rowId": {rid} }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn), rid=rid)
        out += "</td>"

        out += "</tr>"

    out += "</tbody></table>"
    out += "</div>"
    return out

def _render_ok(title: str, details: Dict[str, Any], endpoint_arn: str) -> str:
    out  = "<div style='padding:10px;'>"
    out += f"<h3 style='margin:0 0 8px 0;'>{_esc(title)}</h3>"
    out += "<div style='line-height:1.7;'>"
    for k, v in details.items():
        out += f"<div><b>{_esc(k)}</b>: <code>{_esc(v)}</code></div>"
    out += "</div><div style='height:8px;'></div>"
    out += "<a class='btn'>Back</a>"
    out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "back" }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn))
    out += "</div>"
    return out

# ---------------- Entrypoint ----------------
def lambda_handler(event: Dict[str, Any], context: Any):
    # Docs for the widget’s “Get documentation” button
    if event.get("describe"):
        return {
            "markdown": (
                "### Dynamic Request/Secret Widget\n"
                "- Client & Account are text but also mirrored as hidden inputs so they reach forms.all.\n"
                "- Request invokes the Request Lambda; Secret invokes the Secret Lambda.\n"
                "- This Lambda renders HTML; target Lambdas do the work."
            )
        }

    wc      = (event or {}).get("widgetContext", {}) or {}
    params  = wc.get("params") or {}
    forms   = (wc.get("forms") or {}).get("all") or {}
    action  = params.get("action")
    rid     = params.get("rowId")
    endpoint_arn = getattr(context, "invoked_function_arn", "")

    # Initial/back → render
    if not action or action == "back" or rid is None:
        return _render_table(endpoint_arn)

    # Read the clicked row’s values from forms.all
    dicts = _normalize_forms_all(forms)
    client, account, email, approver, mfa = _extract_row(dicts, rid)

    if action == "request":
        payload = {
            "client": client,
            "account": account,
            "requester_email": email,
            "approver_email": approver,
        }
        _invoke_lambda(TARGET_REQUEST_LAMBDA_ARN, payload)
        return _render_ok("Request sent", payload, endpoint_arn)

    if action == "secret":
        payload = {
            "client": client,
            "account": account,
            "requester_email": email,
            "approver_email": approver,
            "mfa_code": mfa,
        }
        _invoke_lambda(TARGET_SECRET_LAMBDA_ARN, payload)
        return _render_ok("Secret request sent", payload, endpoint_arn)

    # Fallback
    return _render_table(endpoint_arn)
