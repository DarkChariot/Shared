# lambda_function.py
import html

# --------------------------
# Static data (sample rows)
# --------------------------
# You can fetch/generate these dynamically; this is just an example.
ROWS = [
    {"id": 1001, "client": "Acme Corp",  "user": "jsmith", "email": "jsmith@acme.com"},
    {"id": 1002, "client": "Globex LLC", "user": "adoe",   "email": ""},
    {"id": 1003, "client": "Initech",    "user": "mpeter", "email": ""},
]

# Approvers are the SAME for all rows.
# Show the 'name' to users, submit the 'email' as the <option value>.
APPROVERS = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]

# Build a quick lookup to resolve email -> name for confirmations
APPROVER_NAME_BY_EMAIL = {a["email"]: a["name"] for a in APPROVERS}


# --------------------------
# Helpers
# --------------------------
def _esc(s) -> str:
    return html.escape("" if s is None else str(s))

def _normalize_forms_all(forms_all):
    """Normalize forms['all'] into a list of dicts to search uniformly."""
    if isinstance(forms_all, dict):
        return [forms_all]
    if isinstance(forms_all, list):
        return [d for d in forms_all if isinstance(d, dict)]
    return []

def _get_row_values(dicts, rid):
    """
    Extract this row's values from the form payload.
    We gather CLIENT, USER, EMAIL, and APPROVER (email as value).
    """
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

    # Resolve approver name if provided
    approver_name = APPROVER_NAME_BY_EMAIL.get(approver_email) if approver_email else None

    return client, user, email, approver_email, approver_name


# --------------------------
# Rendering
# --------------------------
def _render_confirm(endpoint_arn: str, rid: int, client: str, user: str, email: str,
                    approver_email: str | None, approver_name: str | None) -> str:
    out = ""
    out += "<div style='padding:10px;'>"
    out += f"<h3 style='margin:0 0 8px 0;'>Email Saved (Row {rid})</h3>"
    out += f"<p><b>CLIENT</b> = <code>{_esc(client)}</code></p>"
    out += f"<p><b>USER</b>   = <code>{_esc(user)}</code></p>"
    out += f"<p><b>EMAIL</b>  = <code>{_esc(email)}</code></p>"
    if approver_email:
        shown = f"{approver_name} ({approver_email})" if approver_name else approver_email
        out += f"<p><b>APPROVER</b> = <code>{_esc(shown)}</code></p>"

    out += "<div style='height:8px;'></div>"
    out += "<a class='btn'>Back</a>"
    # NOTE: double braces {{ }} to emit literal JSON in an f-string
    out += f"""
<cwdb-action action="call" display="widget" endpoint="{_esc(endpoint_arn)}">
  {{ "action": "back" }}
</cwdb-action>
""".strip()
    out += "</div>"
    return out


def _render_table(endpoint_arn: str) -> str:
    out = ""
    out += "<div style='padding:10px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>CLIENT • USER • APPROVER • EMAIL</h3>"
    out += "<table style='border-collapse:collapse;width:100%;max-width:1200px;'>"
    out += "<thead><tr>"
    out += "<th style='text-align:left;padding:6px 8px;'>Row</th>"
    out += "<th style='text-align:left;padding:6px 8px;'>CLIENT</th>"
    out += "<th style='text-align:left;padding:6px 8px;'>USER</th>"
    out += "<th style='text-align:left;padding:6px 8px;'>Approver</th>"
    out += "<th style='text-align:left;padding:6px 8px;'>EMAIL</th>"
    out += "<th style='text-align:left;padding:6px 8px;'>Actions</th>"
    out += "</tr></thead><tbody>"

    for r in ROWS:
        rid     = r["id"]
        client  = r.get("client", "")
        user    = r.get("user", "")
        email   = r.get("email", "")

        n_client   = f"r_{rid}_client"
        n_user     = f"r_{rid}_user"
        n_email    = f"r_{rid}_email"
        n_approver = f"r_{rid}_approver"

        out += "<tr>"

        # Row label (id)
        out += f"<td style='padding:6px 8px;'><b>{_esc(rid)}</b></td>"

        # CLIENT (prefill from sample data)
        out += (
            f"<td style='padding:6px 8px;'>"
            f"<input name='{_esc(n_client)}' value='{_esc(client)}' "
            f"placeholder='CLIENT' style='width:100%;max-width:240px;'/>"
            f"</td>"
        )

        # USER (prefill)
        out += (
            f"<td style='padding:6px 8px;'>"
            f"<input name='{_esc(n_user)}' value='{_esc(user)}' "
            f"placeholder='USER account' style='width:100%;max-width:220px;'/>"
            f"</td>"
        )

        # Approver dropdown (names visible, email hidden as value)
        out += f"<td style='padding:6px 8px;'><select name='{_esc(n_approver)}' style='width:100%;max-width:260px;'>"
        out += "<option value='' selected>-- select approver --</option>"
        for opt in APPROVERS:
            out += f"<option value='{_esc(opt['email'])}'>{_esc(opt['name'])}</option>"
        out += "</select></td>"

        # EMAIL (type=email; prefill if any)
        out += (
            f"<td style='padding:6px 8px;'>"
            f"<input type='email' name='{_esc(n_email)}' value='{_esc(email)}' "
            f"placeholder='name@example.com' required style='width:100%;max-width:280px;'/>"
            f"</td>"
        )

        # Actions: Save Email (row-scoped)
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn btn-primary'>Save Email</a>"
        out += f"""
<cwdb-action action="call" display="widget" endpoint="{_esc(endpoint_arn)}">
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
    """
    CloudWatch Custom Widget Lambda:
      - Renders a table of rows (CLIENT, USER, APPROVER, EMAIL) with a per-row Save button.
      - On Save, extracts CLIENT, USER, EMAIL (and approver email/name) for that row.
      - Supports "describe" for the widget docs panel.
    """
    # Docs for the widget's "Get documentation" button
    if event.get("describe"):
        return {
            "markdown": (
                "## Client/User/Email Widget\n"
                "- Each row includes CLIENT, USER account, Approver (name-only dropdown), and Email.\n"
                "- Approver `<option>` displays the name, but the `value` is their email (hidden).\n"
                "- Clicking **Save Email** re-invokes this Lambda, sending:\n"
                "  - `widgetContext.params` → `{ action: 'save_email', rowId: <RID> }`\n"
                "  - `widgetContext.forms.all` → all inputs (e.g. `r_<RID>_client`, `r_<RID>_user`, `r_<RID>_approver`, `r_<RID>_email`).\n"
            )
        }

    wc      = (event or {}).get("widgetContext", {}) or {}
    params  = wc.get("params") or {}
    forms   = wc.get("forms") or {}
    allvals = forms.get("all") or {}
    action  = params.get("action")
    rid     = params.get("rowId")

    endpoint_arn = getattr(context, "invoked_function_arn", "")

    # Handle Save Email click
    if action == "save_email" and rid is not None:
        dicts = _normalize_forms_all(allvals)
        client, user, email, approver_email, approver_name = _get_row_values(dicts, rid)
        return _render_confirm(endpoint_arn, rid, client, user, email, approver_email, approver_name)

    # Initial / Back render
    return _render_table(endpoint_arn)
