import html

# ---- Example data ----
ROWS = [
    {"id": 1001, "client": "Acme Corp",   "user": "jsmith",  "approvers": ["alice", "bob", "carol"]},
    {"id": 1002, "client": "Globex LLC",  "user": "adoe",    "approvers": ["dave", "erin"]},
    {"id": 1003, "client": "Initech",     "user": "mpeter",  "approvers": ["mike", "samir", "peter"]},
]

def _normalize_forms_all(forms_all):
    if isinstance(forms_all, dict):
        return [forms_all]
    if isinstance(forms_all, list):
        return [d for d in forms_all if isinstance(d, dict)]
    return []

def _get_row_values(dicts, rid):
    """
    Pull this row's CLIENT, USER, EMAIL (and approver if you want it too).
    """
    k_client   = f"r_{rid}_client"
    k_user     = f"r_{rid}_user"
    k_email    = f"r_{rid}_email"
    k_approver = f"r_{rid}_approver"

    client = user = email = approver = None
    for d in dicts:
        if k_client in d:   client   = d.get(k_client)
        if k_user   in d:   user     = d.get(k_user)
        if k_email  in d:   email    = d.get(k_email)
        if k_approver in d: approver = d.get(k_approver)

    return client, user, email, approver

def lambda_handler(event, context):
    # Optional docs
    if event.get("describe"):
        return {
            "markdown": (
                "### Client/User/Email Widget\n"
                "- Each row has CLIENT, USER account, Approver (dropdown), and Email input.\n"
                "- Clicking **Save Email** sends `rowId` in `widgetContext.params` and all inputs in `widgetContext.forms.all`.\n"
                "- Lambda extracts CLIENT, USER, EMAIL for the clicked row."
            )
        }

    wc      = (event or {}).get("widgetContext", {}) or {}
    params  = wc.get("params") or {}
    forms   = wc.get("forms") or {}
    allvals = forms.get("all") or {}
    action  = params.get("action")
    rid     = params.get("rowId")

    endpoint = getattr(context, "invoked_function_arn", "")

    # ---------- Handle Email button ----------
    if action == "save_email" and rid is not None:
        dicts = _normalize_forms_all(allvals)
        client, user, email, approver = _get_row_values(dicts, rid)

        out  = "<div style='padding:10px;'>"
        out += f"<h3>Email Saved (Row {rid})</h3>"
        out += f"<p><b>CLIENT</b> = <code>{html.escape(str(client or ''))}</code></p>"
        out += f"<p><b>USER</b>   = <code>{html.escape(str(user   or ''))}</code></p>"
        out += f"<p><b>EMAIL</b>  = <code>{html.escape(str(email  or ''))}</code></p>"
        # approver is available if you want to show/store it:
        # out += f"<p><b>APPROVER</b> = <code>{html.escape(str(approver or ''))}</code></p>"

        out += "<a class='btn'>Back</a>"
        out += f"""
<cwdb-action action="call" display="widget" endpoint="{html.escape(endpoint)}">
  {{ "action": "back" }}
</cwdb-action>
""".strip()
        out += "</div>"
        return out

    # ---------- Render table ----------
    output  = "<div style='padding:10px;'>"
    output += "<h3 style='margin:0 0 8px 0;'>CLIENT • USER • EMAIL</h3>"
    output += "<table style='border-collapse:collapse;width:100%;max-width:1100px;'>"
    output += "<thead><tr>"
    output += "<th style='text-align:left;padding:6px 8px;'>Row</th>"
    output += "<th style='text-align:left;padding:6px 8px;'>CLIENT</th>"
    output += "<th style='text-align:left;padding:6px 8px;'>USER</th>"
    output += "<th style='text-align:left;padding:6px 8px;'>Approver</th>"
    output += "<th style='text-align:left;padding:6px 8px;'>EMAIL</th>"
    output += "<th style='text-align:left;padding:6px 8px;'>Actions</th>"
    output += "</tr></thead><tbody>"

    for r in ROWS:
        row_id   = r["id"]
        approver_options = r.get("approvers", [])

        n_client   = f"r_{row_id}_client"
        n_user     = f"r_{row_id}_user"
        n_email    = f"r_{row_id}_email"
        n_approver = f"r_{row_id}_approver"

        # One row
        output += "<tr>"

        # Row label (you can also show current values here if you prefill)
        output += f"<td style='padding:6px 8px;'><b>{html.escape(str(row_id))}</b></td>"

        # CLIENT (text)
        output += (
            f"<td style='padding:6px 8px;'>"
            f"<input name='{html.escape(n_client)}' placeholder='CLIENT' style='width:100%;max-width:220px;'/>"
            f"</td>"
        )

        # USER (text)
        output += (
            f"<td style='padding:6px 8px;'>"
            f"<input name='{html.escape(n_user)}' placeholder='USER account' style='width:100%;max-width:220px;'/>"
            f"</td>"
        )

        # Approver (dropdown)
        output += f"<td style='padding:6px 8px;'><select name='{html.escape(n_approver)}' style='width:100%;max-width:220px;'>"
        output += "<option value='' selected>-- select approver --</option>"
        for opt in approver_options:
            output += f"<option value='{html.escape(opt)}'>{html.escape(opt)}</option>"
        output += "</select></td>"

        # EMAIL (email input)
        output += (
            f"<td style='padding:6px 8px;'>"
            f"<input type='email' name='{html.escape(n_email)}' placeholder='name@example.com' required style='width:100%;max-width:260px;'/>"
            f"</td>"
        )

        # Actions: Email button (calls back with this rowId)
        output += "<td style='padding:6px 8px;'>"
        output += "<a class='btn btn-primary'>Save Email</a>"
        output += f"""
<cwdb-action action="call" display="widget" endpoint="{html.escape(endpoint)}">
  {{ "action": "save_email", "rowId": {row_id} }}
</cwdb-action>
""".strip()
        output += "</td>"

        output += "</tr>"

    output += "</tbody></table>"
    output += "</div>"
    return output
