# lambda_function.py
import html

# --------------------------
# Sample rows (prefill Client + Account; user supplies the rest)
# --------------------------
ROWS = [
    {"id": 3001, "client": "TestClient A", "account": "TestUserA"},
    {"id": 3002, "client": "TestClient B", "account": "TestUserB"},
    {"id": 3003, "client": "TestClient C", "account": "TestUserC"},
]

# Approvers are the same for all rows:
# Visible to user: name
# Submitted value: email (hidden)
APPROVERS = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]
APPROVER_NAME_BY_EMAIL = {a["email"]: a["name"] for a in APPROVERS}


# --------------------------
# Helpers
# --------------------------
def _esc(v) -> str:
    return html.escape("" if v is None else str(v))

def _normalize_forms_all(forms_all):
    """Normalize widgetContext.forms.all -> list[dict]."""
    if isinstance(forms_all, dict):
        return [forms_all]
    if isinstance(forms_all, list):
        return [d for d in forms_all if isinstance(d, dict)]
    return []

def _keys_for_row(rid: int):
    """Namespaced input names per row."""
    return {
        "client":   f"r_{rid}_client",
        "account":  f"r_{rid}_account",
        "email":    f"r_{rid}_email",
        "approver": f"r_{rid}_approver",  # dropdown value = approver email
        "mfa":      f"r_{rid}_mfa",
    }

def _extract_row_values(dicts, rid: int):
    """
    Pull this row's values from forms['all'].
    Returns: client, account, email, approver_email, approver_name, mfa
    """
    k = _keys_for_row(rid)
    client = account = email = approver_email = mfa = None

    for d in dicts:
        if k["client"]   in d: client        = d.get(k["client"])
        if k["account"]  in d: account       = d.get(k["account"])
        if k["email"]    in d: email         = d.get(k["email"])
        if k["approver"] in d: approver_email = d.get(k["approver"])
        if k["mfa"]      in d: mfa           = d.get(k["mfa"])

    approver_name = APPROVER_NAME_BY_EMAIL.get(approver_email) if approver_email else None
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

    for r in ROWS if False else ROWS:  # keep simple; edit sentinel if you template
        rid     = r["id"]
        client  = r.get("client", "")
        account = r.get("account", "")
        k       = _keys_for_row(rid)

        out += "<tr>"

        # Client (prefilled)
        out += (
            f"<td style='padding:6px 8px;'>"
            f"<input name='{_esc(k['client'])}' value='{_esc(client)}' "
            f"placeholder='Client' style='width:100%;max-width:220px;'/>"
            f"</td>"
        )

        # Account Name (prefilled)
        out += (
            f"<td style='padding:6px 8px;'>"
            f"<input name='{_esc(k['account'])}' value='{_esc(account)}' "
            f"placeholder='Account Name' style='width:100%;max-width:220px;'/>"
            f"</td>"
        )

        # Requester Email (user types)
        out += (
            f"<td style='padding:6px 8px;'>"
            f"<input type='email' name='{_esc(k['email'])}' "
            f"placeholder='name@example.com' required style='width:100%;max-width:260px;'/>"
            f"</td>"
        )

        # Approver (dropdown: name shown, email as value)
        out += f"<td style='padding:6px 8px;'><select name='{_esc(k['approver'])}' style='width:100%;max-width:260px;'>"
        out += "<option value='' selected>-- select approver --</option>"
        for a in APPROVERS:
            out += f"<option value='{_esc(a['email'])}'>{_esc(a['name'])}</option>"
        out += "</select></td>"

        # Request button → calls Lambda in the widget area
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn btn-primary'>Request</a>"
        out += f"""
<cwdb-action action="call" display="widget" endpoint="{_esc(endpoint_arn)}">
  {{ "action": "request", "rowId": {rid} }}
</cwdb-action>
""".strip()
        out += "</td>"

        # MFA Code (user types)
        out += (
            f"<td style='padding:6px 8px;'>"
            f"<input name='{_esc(k['mfa'])}' placeholder='6-digit code' style='width:100%;max-width:160px;'/>"
            f"</td>"
        )

        # Secret button → opens popup for this row
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn'>Secret</a>"
        out += f"""
<cwdb-action action="call" display="popup" endpoint="{_esc(endpoint_arn)}">
  {{ "action": "secret_popup", "rowId": {rid} }}
</cwdb-action>
""".strip()
        out += "</td>"

        out += "</tr>"

    out += "</tbody></table>"
    out += "</div>"
    return out


def _render_request_confirmation(endpoint_arn: str, rid: int,
                                 client: str, account: str, email: str,
                                 approver_email: str | None, approver_name: str | None) -> str:
    """
    After clicking 'Request', show a confirmation summary in the widget.
    (We intentionally do not require MFA for Request; adjust if needed.)
    """
    out  = "<div style='padding:10px;'>"
    out += f"<h3 style='margin:0 0 8px 0;'>Request Submitted (Row {rid})</h3>"
    out += f"<p><b>Client</b> = <code>{_esc(client)}</code></p>"
    out += f"<p><b>Account</b> = <code>{_esc(account)}</code></p>"
    out += f"<p><b>Requester Email</b> = <code>{_esc(email)}</code></p>"
    if approver_email:
        shown = f"{approver_name} ({approver_email})" if approver_name else approver_email
        out += f"<p><b>Approver</b> = <code>{_esc(shown)}</code></p>"

    out += "<div style='height:8px;'></div>"
    out += "<a class='btn'>Back</a>"
    out += f"""
<cwdb-action action="call" display="widget" endpoint="{_esc(endpoint_arn)}">
  {{ "action": "back" }}
</cwdb-action>
""".strip()
    out += "</div>"
    return out


def _render_secret_popup(rid: int,
                         client: str, account: str, email: str,
                         approver_email: str | None, approver_name: str | None,
                         mfa: str | None) -> str:
    """
    Popup content for 'Secret' button (display='popup').
    """
    out  = "<div style='padding:10px; max-width: 560px;'>"
    out += f"<h3 style='margin:0 0 8px 0;'>Secret Details (Row {rid})</h3>"
    out += "<div style='line-height:1.7;'>"
    out += f"<div><b>Client</b>: {_esc(client)}</div>"
    out += f"<div><b>Account</b>: {_esc(account)}</div>"
    out += f"<div><b>Requester Email</b>: {_esc(email)}</div>"
    if approver_email:
        shown = f"{approver_name} ({approver_email})" if approver_name else approver_email
        out += f"<div><b>Approver</b>: {_esc(shown)}</div>"
    out += f"<div><b>MFA Code</b>: {_esc(mfa)}</div>"
    out += "</div>"
    out += "</div>"
    return out


# --------------------------
# Lambda entry
# --------------------------
def lambda_handler(event, context):
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
