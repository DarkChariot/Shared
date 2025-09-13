# lambda_function.py
import html
import json
from typing import Optional, List, Dict, Any, Tuple

import boto3

# --------------------------------------------------------------------
# CONFIG: set the ARNs of the two target Lambdas your buttons should call
# --------------------------------------------------------------------
TARGET_REQUEST_LAMBDA_ARN = "arn:aws:lambda:us-east-1:123456789012:function:my-request-lambda"
TARGET_SECRET_LAMBDA_ARN  = "arn:aws:lambda:us-east-1:123456789012:function:my-secret-lambda"

lambda_client = boto3.client("lambda")

# --------------------------------------------------------------------
# DATA
# --------------------------------------------------------------------
# Client + Account are TEXT ONLY (not inputs). Email / Approver / MFA are inputs.
ROWS: List[Dict[str, Any]] = [
    {"id": 3001, "client": "TestClient A", "account": "TestUserA"},
    {"id": 3002, "client": "TestClient B", "account": "TestUserB"},
    {"id": 3003, "client": "TestClient C", "account": "TestUserC"},
]

# Approvers are the same everywhere (name shown, email hidden as <option value>)
APPROVERS: List[Dict[str, str]] = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]
APPROVER_NAME_BY_EMAIL: Dict[str, str] = {a["email"]: a["name"] for a in APPROVERS}

# --------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------
def _esc(v: Any) -> str:
    return html.escape("" if v is None else str(v))

def _normalize_forms_all(forms_all: Any) -> List[Dict[str, Any]]:
    """Normalize widgetContext.forms.all -> list[dict]."""
    if isinstance(forms_all, dict):
        return [forms_all]
    if isinstance(forms_all, list):
        return [d for d in forms_all if isinstance(d, dict)]
    return []

def _keys_for_row(rid: int) -> Dict[str, str]:
    """Input names that DO exist per row."""
    return {
        "email":    f"r_{rid}_email",     # Requester Email
        "approver": f"r_{rid}_approver",  # dropdown value = approver email
        "mfa":      f"r_{rid}_mfa",       # MFA code
    }

def _row_static_values(rid: int) -> Tuple[Optional[str], Optional[str]]:
    """Return (client, account) for row id from ROWS."""
    for r in ROWS:
        if r["id"] == rid:
            return r.get("client"), r.get("account")
    return None, None

def _extract_dynamic_values(dicts: List[Dict[str, Any]], rid: int) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Extract Requester Email, Approver Email(+Name), MFA from forms['all'] for a row.
    Returns (requester_email, approver_email, approver_name, mfa_code)
    """
    k = _keys_for_row(rid)
    requester_email = approver_email = mfa = None
    for d in dicts:
        if k["email"] in d:
            requester_email = d.get(k["email"])
        if k["approver"] in d:
            approver_email = d.get(k["approver"])
        if k["mfa"] in d:
            mfa = d.get(k["mfa"])

    approver_name: Optional[str] = APPROVER_NAME_BY_EMAIL.get(approver_email) if approver_email else None
    return requester_email, approver_email, approver_name, mfa

# --------------------------------------------------------------------
# INVOKERS
# --------------------------------------------------------------------
def _invoke_request_lambda(client_txt: Optional[str], account_txt: Optional[str],
                           requester_email: Optional[str], approver_email: Optional[str]) -> Dict[str, Any]:
    payload = {
        "client": client_txt,
        "account": account_txt,
        "requester_email": requester_email,
        "approver_email": approver_email,
    }
    # Fire-and-forget. Use "RequestResponse" if you need the response payload.
    lambda_client.invoke(
        FunctionName=TARGET_REQUEST_LAMBDA_ARN,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    return payload

def _invoke_secret_lambda(client_txt: Optional[str], account_txt: Optional[str],
                          requester_email: Optional[str], approver_email: Optional[str],
                          mfa_code: Optional[str]) -> Dict[str, Any]:
    payload = {
        "client": client_txt,
        "account": account_txt,
        "requester_email": requester_email,
        "approver_email": approver_email,
        "mfa_code": mfa_code,
    }
    lambda_client.invoke(
        FunctionName=TARGET_SECRET_LAMBDA_ARN,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    return payload

# --------------------------------------------------------------------
# RENDERERS
# --------------------------------------------------------------------
def _render_table(endpoint_arn: str) -> str:
    """
    Columns:
      Client (text) | Account Name (text) | Requester Email (input) | Approver (dropdown)
      | Request (button) | MFA Code (input) | Secret (button)
    """
    out  = "<div style='padding:10px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>Client • Account • Requester Email • Approver • Request • MFA Code • Secret</h3>"
    out += "<table style='border-collapse:collapse;width:100%;max-width:1600px;'>"
    out += (
        "<thead><tr>"
        "<th style='text-align:left;padding:6px 8px;'>Client</th>"
        "<th style='text-align:left;padding:6px 8px;'>Account Name</th>"
        "<th style='text-align:left;padding:6px 8px;'>Requester Email</th>"
        "<th style='text-align:left;padding:6px 8px;'>Approver</th>"
        "<th style='text-align:left;padding:6px 8px;'>Request</th>"
        "<th style='text-align:left;padding:6px 8px;'>MFA Code</th>"
        "<th style='text-align:left;padding:6px 8px;'>Secret</th>"
        "</tr></thead><tbody>"
    )

    for r in ROWS:
        rid     = r["id"]
        client  = r.get("client", "")
        account = r.get("account", "")
        k       = _keys_for_row(rid)

        out += "<tr>"

        # Client (TEXT ONLY)
        out += f"<td style='padding:6px 8px;'><span>{_esc(client)}</span></td>"

        # Account (TEXT ONLY)
        out += f"<td style='padding:6px 8px;'><span>{_esc(account)}</span></td>"

        # Requester Email (user types)
        out += (
            "<td style='padding:6px 8px;'>"
            "<input type='email' name='{name}' placeholder='name@example.com' required "
            "style='width:100%;max-width:260px;'/>"
            "</td>".format(name=_esc(k["email"]))
        )

        # Approver (dropdown: name shown, email as value)
        out += "<td style='padding:6px 8px;'><select name='{name}' style='width:100%;max-width:260px;'>".format(
            name=_esc(k["approver"])
        )
        out += "<option value='' selected>-- select approver --</option>"
        for a in APPROVERS:
            out += "<option value='{val}'>{label}</option>".format(
                val=_esc(a["email"]), label=_esc(a["name"])
            )
        out += "</select></td>"

        # Request button → calls THIS Lambda; handler will invoke request target Lambda
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn btn-primary'>Request</a>"
        out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "request", "rowId": {rid} }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn), rid=rid)
        out += "</td>"

        # MFA Code (user types)
        out += (
            "<td style='padding:6px 8px;'>"
            "<input name='{name}' placeholder='6-digit code' style='width:100%;max-width:160px;'/>"
            "</td>".format(name=_esc(k["mfa"]))
        )

        # Secret button → calls THIS Lambda; handler will invoke secret target Lambda
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

def _render_confirmation(title: str, details: Dict[str, Any], endpoint_arn: str) -> str:
    out  = "<div style='padding:10px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>{}</h3>".format(_esc(title))
    out += "<div style='line-height:1.7;'>"
    for k, v in details.items():
        out += "<div><b>{}</b>: <code>{}</code></div>".format(_esc(k), _esc(v))
    out += "</div>"
    out += "<div style='height:8px;'></div>"
    out += "<a class='btn'>Back</a>"
    out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "back" }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn))
    out += "</div>"
    return out

# --------------------------------------------------------------------
# LAMBDA ENTRY
# --------------------------------------------------------------------
def lambda_handler(event: Dict[str, Any], context: Any):
    """
    Widget columns:
      Client (text) | Account Name (text) | Requester Email (input) | Approver (dropdown)
      | Request (button) | MFA Code (input) | Secret (button)

    Actions handled in this Lambda:
      - 'request' -> collect row values; invoke TARGET_REQUEST_LAMBDA_ARN
      - 'secret'  -> collect row values; invoke TARGET_SECRET_LAMBDA_ARN
      - 'back'    -> re-render table
      - 'describe'-> docs panel
    """
    # Docs panel for "Get documentation"
    if event.get("describe"):
        return {
            "markdown": (
                "### Client/Account/Email/Approver + Request/Secret Buttons\n"
                "- **Request** invokes the configured Request Lambda with client/account/requester_email/approver_email.\n"
                "- **Secret** invokes the configured Secret Lambda with client/account/requester_email/approver_email/mfa_code.\n"
                "- Inputs come via `widgetContext.forms.all`; button JSON via `widgetContext.params`.\n"
            )
        }

    wc      = (event or {}).get("widgetContext", {}) or {}
    params  = wc.get("params") or {}
    forms   = wc.get("forms") or {}
    allvals = forms.get("all") or {}
    action  = params.get("action")
    rid     = params.get("rowId")
    endpoint_arn = getattr(context, "invoked_function_arn", "")

    # Initial/back -> just render
    if not action or action == "back" or rid is None:
        return _render_table(endpoint_arn)

    # Normalize forms for extraction
    dicts = _normalize_forms_all(allvals)
    requester_email, approver_email, approver_name, mfa = _extract_dynamic_values(dicts, rid)
    client_txt, account_txt = _row_static_values(rid)

    # Route actions
    if action == "request":
        sent = _invoke_request_lambda(client_txt, account_txt, requester_email, approver_email)
        return _render_confirmation(
            "Request sent",
            {
                "client": sent.get("client"),
                "account": sent.get("account"),
                "requester_email": sent.get("requester_email"),
                "approver_email": sent.get("approver_email"),
            },
            endpoint_arn,
        )

    if action == "secret":
        sent = _invoke_secret_lambda(client_txt, account_txt, requester_email, approver_email, mfa)
        return _render_confirmation(
            "Secret request sent",
            {
                "client": sent.get("client"),
                "account": sent.get("account"),
                "requester_email": sent.get("requester_email"),
                "approver_email": sent.get("approver_email"),
                "mfa_code": sent.get("mfa_code"),
            },
            endpoint_arn,
        )

    # Fallback
    return _render_table(endpoint_arn)
