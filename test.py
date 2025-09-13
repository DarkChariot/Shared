# lambda_function.py
import html
from typing import Optional, List, Dict, Any, Tuple

# --------------------------
# Sample rows (prefill Client + Account; user supplies the rest)
# --------------------------
ROWS: List[Dict[str, Any]] = [
    {"id": 3001, "client": "TestClient A", "account": "TestUserA"},
    {"id": 3002, "client": "TestClient B", "account": "TestUserB"},
    {"id": 3003, "client": "TestClient C", "account": "TestUserC"},
]

# Approvers are the same for all rows:
# Visible to user: name
# Submitted value: email (hidden)
APPROVERS: List[Dict[str, str]] = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]
APPROVER_NAME_BY_EMAIL: Dict[str, str] = {a["email"]: a["name"] for a in APPROVERS}

# --------------------------
# Helpers
# --------------------------
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
    """Namespaced input names per row."""
    return {
        "client":   "r_{rid}_client".format(rid=rid),
        "account":  "r_{rid}_account".format(rid=rid),
        "email":    "r_{rid}_email".format(rid=rid),
        "approver": "r_{rid}_approver".format(rid=rid),  # dropdown value = approver email
        "mfa":      "r_{rid}_mfa".format(rid=rid),
    }

def _extract_row_values(dicts: List[Dict[str, Any]], rid: int) -> Tuple[
    Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]
]:
    """
    Pull this row's values from forms['all'].
    Returns: client, account, email, approver_email, approver_name, mfa
    """
    k = _keys_for_row(rid)
    client = account = email = approver_email = mfa = None  # type: Optional[str]

    for d in dicts:
        if k["client"]   in d: client         = d.get(k["client"])
        if k["account"]  in d: account        = d.get(k["account"])
        if k["email"]    in d: email          = d.get(k["email"])
        if k["approver"] in d: approver_email = d.get(k["approver"])
        if k["mfa"]      in d: mfa            = d.get(k["mfa"])

    approver_name: Optional[str] = (
        APPROVER_NAME_BY_EMAIL.get(approver_email) if approver_email else None
    )
    return client, account, email, approver_email, approver_name, mfa

# --------------------------
# Renderers
# --------------------------
def _render_table(endpoint_arn: str) -> str:
    """
    Main widget view: columns
    Client | Account Name | Requester Email | Approver | Request | MFA Code | Secret
    """
    out  = "<div style='padding:10px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>Client • Account • Email • Approver • Request • MFA • Secret</h3>"
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

        # Client (prefilled)
        out += (
            "<td style='padding:6px 8px;'>"
            "<input name='{name}' value='{val}' placeholder='Client' style='width:100%;max-width:220px;'/>"
            "</td>".format(name=_esc(k["client"]), val=_esc(client))
        )

        # Account Name (prefilled)
        out += (
            "<td style='padding:6px 8px;'>"
            "<input name='{name}' value='{val}' placeholder='Account Name' style='width:100%;max-width:220px;'/>"
            "</td>".format(name=_esc(k["account"]), val=_esc(account))
        )

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

        # Request button → calls Lambda in the widget area
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

        # Secret button → opens popup for this row
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn'>Secret</a>"
        out += """
<cwdb-action action="call" display="popup" endpoint="{endpoint}">
  {{ "action": "secret_popup", "rowId": {rid} }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn), rid=rid)
        out += "</td>"

        out += "</tr>"

    out += "</tbody></table>"
    out += "</div>"
    return out

def _render_request_confirmation(
    endpoint_arn: str,
    rid: int,
    client: Optional[str],
    account: Optional[str],
    email: Optional[str],
    approver_email: Optional[str],
    approver_name: Optional[str],
) -> str:
    """
    After clicking 'Request', show a confirmation summary in the widget.
    """
    out  = "<div style='padding:10px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>Request Submitted (Row {rid})</h3>".format(rid=rid)
    out += "<p><b>Client</b> = <code>{v}</code></p>".format(v=_esc(client))
    out += "<p><b>Account</b> = <code>{v}</code></p>".format(v=_esc(account))
    out += "<p><b>Requester Email</b> = <code>{v}</code></p>".format(v=_esc(email))
    if approver_email:
        shown = "{name} ({email})".format(name=approver_name or "", email=approver_email) if approver_name else approver_email
        out += "<p><b>Approver</b> = <code>{v}</code></p>".format(v=_esc(shown))

    out += "<div style='height:8px;'></div>"
    out += "<a class='btn'>Back</a>"
    out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "back" }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn))
    out += "</div>"
    return out

def _render_secret_popup(
    rid: int,
    client: Optional[str],
    account: Optional[str],
    email: Optional[str],
    approver_email: Optional[str],
    approver_name: Optional[str],
    mfa: Optional[str],
) -> str:
    """
    Popup content for 'Secret' button (display='popup').
    """
    out  = "<div style='padding:10px; max-width: 560px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>Secret Details (Row {rid})</h3>".format(rid=rid)
    out += "<div style='line-height:1.7;'>"
    out += "<div><b>Client</b>: {v}</div>".format(v=_esc(client))
    out += "<div><b>Account</b>: {v}</div>".format(v=_esc(account))
    out += "<div><b>Requester Email</b>: {v}</div>".format(v=_esc(email))
    if approver_email:
        shown = "{name} ({email})".format(name=approver_name or "", email=approver_email) if approver_name else approver_email
        out += "<div><b>Approver</b>: {v}</div>".format(v=_esc(shown))
    out += "<div><b>MFA Code</b>: {v}</div>".format(v=_esc(mfa))
    out += "</div>"
    out += "</div>"
    return out

# --------------------------
# Lambda entry
# --------------------------
def lambda_handler(event: Dict[str, Any], context: Any) -> str:
    """
    CloudWatch Custom Widget Lambda:

    Columns:
      Client | Account Name | Requester Email | Approver | Request | MFA Code | Secret

    Actions:
      - 'request'      -> capture Client, Account, Requester Email, Approver (email) for that row
      - 'secret_popup' -> open a popup showing Client, Account, Requester Email, Approver, MFA code
      - 'back'         -> re-render the table
      - 'describe'     -> widget docs panel
    """
    # Docs panel
    if event.get("describe"):
        return {
            "markdown": (
                "### Client/Account/Email/Approver/Request/MFA/Secret Widget\n"
                "- **Request** button re-invokes Lambda (display=widget) and shows a summary using current inputs.\n"
                "- **Secret** button opens a **popup** (display=popup) with row details (including MFA Code).\n"
                "- Approver dropdown shows names; submitted value is the approver's **email**.\n"
                "- Inputs arrive in `widgetContext.forms.all`; button JSON arrives in `widgetContext.params`.\n"
            )
        }

    wc      = (event or {}).get("widgetContext", {}) or {}
    params  = wc.get("params") or {}
    forms   = wc.get("forms") or {}
    allvals = forms.get("all") or {}
    action  = params.get("action")
    rid     = params.get("rowId")

    endpoint_arn = getattr(context, "invoked_function_arn", "")

    # Normalize inputs for easy extraction
    dicts = _normalize_forms_all(allvals)

    # Handle Request (widget display)
    if action == "request" and rid is not None:
        client, account, email, approver_email, approver_name, _mfa = _extract_row_values(dicts, rid)
        return _render_request_confirmation(endpoint_arn, rid, client, account, email, approver_email, approver_name)

    # Handle Secret (popup display)
    if action == "secret_popup" and rid is not None:
        client, account, email, approver_email, approver_name, mfa = _extract_row_values(dicts, rid)
        return _render_secret_popup(rid, client, account, email, approver_email, approver_name, mfa)

    # Back or initial load -> render the table
    return _render_table(endpoint_arn)
