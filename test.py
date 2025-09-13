# lambda_function.py
import html

# --------------------------
# Sample rows
# --------------------------
# Pre-fill only CLIENT and USER if you want. Email starts blank.
ROWS = [
    {"id": 1001, "client": "Acme Corp",  "user": "jsmith"},
    {"id": 1002, "client": "Globex LLC", "user": "adoe"},
    {"id": 1003, "client": "Initech",    "user": "mpeter"},
]

# Static approvers — names shown, emails hidden as values
APPROVERS = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]

APPROVER_NAME_BY_EMAIL = {a["email"]: a["name"] for a in APPROVERS}


# --------------------------
# Helpers
# --------------------------
def _esc(s) -> str:
    return html.escape("" if s is None else str(s))

def _normalize(forms_all):
    if isinstance(forms_all, dict):
        return [forms_all]
    if isinstance(forms_all, list):
        return [d for d in forms_all if isinstance(d, dict)]
    return []

def _get_row_values(dicts, rid):
    """Extract CLIENT, USER, EMAIL (typed by user), APPROVER (email hidden value)."""
    k_client   = f"r_{rid}_client"
    k_user     = f"r_{rid}_user"
    k_email    = f"r_{rid}_email"
    k_approver = f"r_{rid}_approver"

    client = user = email = approver_email = None
    for d in dicts:
        if k_client in d:   client         = d.get(k_client)
        if k_user   in d:   user           = d.get(k_user)
        if k_email  in d:   email          = d.get(k_email)
        if k_approver in d: approver_email = d.get(k_approver)

    approver_name = APPROVER_NAME_BY_EMAIL.get(approver_email) if approver_email else None
    return client, user, email, approver_email, approver_name


# --------------------------
# Rendering
# --------------------------
def _render_confirm(endpoint, rid, client, user, email, approver_email, approver_name):
    out  = "<div style='padding:10px;'>"
    out += f"<h3>Email Saved (Row {rid})</h3>"
    out += f"<p><b>CLIENT</b> = <code>{_esc(client)}</code></p>"
    out += f"<p><b>USER</b>   = <code>{_esc(user)}</code></p>"
    out += f"<p><b>EMAIL</b>  = <code>{_esc(email)}</code></p>"
    if approver_email:
        shown = f"{approver_name} ({approver_email})" if approver_name else approver_email
        out += f"<p><b>APPROVER</b> = <code>{_esc(shown)}</code></p>"
    out += "<div style='height:8px;'></div>"
    out += "<a class='btn'>Back</a>"
    out += f"""
<cwdb-action action="call" display="widget" endpoint="{_esc(endpoint)}">
  {{ "action": "back" }}
</cwdb-action>
""".strip()
    out += "</div>"
    return out

def _render_table(endpoint):
    out  = "<div style='padding:10px;'>"
    out += "<h3>CLIENT • USER • APPROVER • EMAIL</h3>"
    out += "<table style='border-collapse:collapse;width:100%;max-width:1200px;'>"
    out += "<thead><tr>"
    out += "<th>Row</th><th>CLIENT</th><th>USER</th><th>Approver</th><th>EMAIL</th><th>Action</th>"
    out += "</tr></thead><tbody>"

    for r in ROWS:
        rid, client, user = r["id"], r["client"], r["user"]
        n_client, n_user  = f"r_{rid}_client", f"r_{rid}_user"
        n_email, n_approver = f"r_{rid}_email", f"r_{rid}_approver"

        out += "<tr>"

        # Row label
        out += f"<td><b>{_esc(rid)}</b></td>"

        # CLIENT + USER pre-filled
        out += f"<td><input name='{_esc(n_client)}' value='{_esc(client)}' placeholder='CLIENT'/></td>"
        out += f"<td><input name='{_esc(n_user)}' value='{_esc(user)}' placeholder='USER account'/></td>"

        # Approver dropdown
        out += f"<td><select name='{_esc(n_approver)}'>"
        out += "<option value='' selected>-- select approver --</option>"
        for a in APPROVERS:
            out += f"<option value='{_esc(a['email'])}'>{_esc(a['name'])}</option>"
        out += "</select></td>"

        # EMAIL field is always blank (user types it in)
        out += f"<td><input type='email' name='{_esc(n_email)}' placeholder='name@example.com' required/></td>"

        # Action button
        out += "<td><a class='btn btn-primary'>Save Email</a>"
        out += f"""
<cwdb-action action="call" display="widget" endpoint="{_esc(endpoint)}">
  {{ "action": "save_email", "rowId": {rid} }}
</cwdb-action>
""".strip()
        out += "</td>"

        out += "</tr>"

    out += "</tbody></table>"
    out += "</div>"
    return out


# --------------------------
# Lambda entry
# --------------------------
def lambda_handler(event, context):
    if event.get("describe"):
        return {
            "markdown": (
                "### Client/User/Approver/Email Widget\n"
                "- User types CLIENT, USER, and EMAIL directly.\n"
                "- Approver dropdown shows **names**, submits **emails** as values.\n"
                "- Clicking **Save Email** sends `{action:'save_email', rowId:<RID>}` in params and all inputs in forms.all.\n"
            )
        }

    wc      = (event or {}).get("widgetContext", {}) or {}
    params  = wc.get("params") or {}
    forms   = wc.get("forms") or {}
    allvals = forms.get("all") or {}
    action  = params.get("action")
    rid     = params.get("rowId")
    endpoint = getattr(context, "invoked_function_arn", "")

    if action == "save_email" and rid is not None:
        dicts = _normalize(allvals)
        client, user, email, approver_email, approver_name = _get_row_values(dicts, rid)
        return _render_confirm(endpoint, rid, client, user, email, approver_email, approver_name)

    # Initial or Back
    return _render_table(endpoint)
