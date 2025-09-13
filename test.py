import html
import json
import re
from typing import Any, Dict, List, Optional, Tuple

import boto3

# =========================
# CONFIG — set your targets
# =========================
TARGET_REQUEST_LAMBDA_ARN = "arn:aws:lambda:us-west-2:222222222222:function:my-request-lambda"
TARGET_SECRET_LAMBDA_ARN  = "arn:aws:lambda:eu-central-1:333333333333:function:my-secret-lambda"
TARGET_INVOKE_ROLE_ARN: Optional[str] = None

# =========================
# SAMPLE DATA
# =========================
ROWS: List[Dict[str, Any]] = [
    {"id": 3001, "client": "TestClient A", "account": "TestUserA"},
    {"id": 3002, "client": "TestClient B", "account": "TestUserB"},
    {"id": 3003, "client": "TestClient C", "account": "TestUserC"},
]

APPROVERS: List[Dict[str, str]] = [
    {"name": "Alice Smith", "email": "alice@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
    {"name": "Carol White", "email": "carol@example.com"},
]
APPROVER_NAME_BY_EMAIL: Dict[str, str] = {a["email"]: a["name"] for a in APPROVERS}

# =========================
# Helpers
# =========================
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
        "client":   f"r_{rid}_client",
        "account":  f"r_{rid}_account",
        "email":    f"r_{rid}_email",
        "approver": f"r_{rid}_approver",
        "mfa":      f"r_{rid}_mfa",
    }

def _extract_row(dicts: List[Dict[str, Any]], rid: int) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    k = _keys_for_row(rid)
    client = account = email = approver_email = mfa = None
    for d in dicts:
        if client is None and k["client"] in d:       client = d.get(k["client"])
        if account is None and k["account"] in d:     account = d.get(k["account"])
        if email is None and k["email"] in d:         email = d.get(k["email"])
        if approver_email is None and k["approver"] in d:
            approver_email = d.get(k["approver"])
        if mfa is None and k["mfa"] in d:             mfa = d.get(k["mfa"])
    approver_name = APPROVER_NAME_BY_EMAIL.get(approver_email) if approver_email else None
    return client, account, email, approver_email, approver_name, mfa

def _parse_region_from_lambda_arn(arn: str) -> str:
    m = re.match(r"arn:aws:lambda:([a-z0-9-]+):\d+:function:.+", arn)
    if not m:
        raise ValueError(f"Not a Lambda ARN: {arn}")
    return m.group(1)

def _lambda_client_for_target(arn: str):
    region = _parse_region_from_lambda_arn(arn)
    if TARGET_INVOKE_ROLE_ARN:
        sts = boto3.client("sts")
        creds = sts.assume_role(RoleArn=TARGET_INVOKE_ROLE_ARN, RoleSessionName="WidgetInvoke")["Credentials"]
        return boto3.client(
            "lambda",
            region_name=region,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )
    return boto3.client("lambda", region_name=region)

def _invoke_lambda(function_arn: str, payload: Dict[str, Any]) -> None:
    client = _lambda_client_for_target(function_arn)
    client.invoke(
        FunctionName=function_arn,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )

# =========================
# Renderers
# =========================
def _banner(endpoint_arn: str) -> str:
    return (
        "<div style='padding:8px 12px;margin:0 0 10px 0;background:#f3f4f6;"
        "border:1px solid #e5e7eb;border-radius:8px;'>"
        f"<b>Serving from Lambda ARN:</b> <code>{_esc(endpoint_arn)}</code>"
        "</div>"
    )

def _render_table(endpoint_arn: str) -> str:
    out  = _banner(endpoint_arn)
    out += "<div style='padding:10px;'>"
    out += "<h3>Client • Account • Requester Email • Approver • Request • MFA • Secret</h3>"
    out += "<table style='border-collapse:collapse;width:100%;max-width:1600px;'>"
    out += ("<thead><tr>"
            "<th style='text-align:left;padding:6px 8px;'>Client</th>"
            "<th style='text-align:left;padding:6px 8px;'>Account</th>"
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

        # Client TEXT + hidden mirror
        out += "<td style='padding:6px 8px;'><span>{txt}</span>".format(txt=_esc(client))
        out += "<input type='hidden' name='{name}' value='{val}'/></td>".format(
            name=_esc(k["client"]), val=_esc(client)
        )

        # Account TEXT + hidden mirror
        out += "<td style='padding:6px 8px;'><span>{txt}</span>".format(txt=_esc(account))
        out += "<input type='hidden' name='{name}' value='{val}'/></td>".format(
            name=_esc(k["account"]), val=_esc(account)
        )

        # Requester Email
        out += (
            "<td style='padding:6px 8px;'>"
            "<input type='email' name='{name}' placeholder='name@example.com' "
            "style='width:100%;max-width:260px;'/>"
            "</td>".format(name=_esc(k["email"]))
        )

        # Approver dropdown
        out += "<td style='padding:6px 8px;'><select name='{name}' style='width:100%;max-width:260px;'>".format(
            name=_esc(k["approver"])
        )
        out += "<option value='' selected>-- select approver --</option>"
        for a in APPROVERS:
            out += "<option value='{val}'>{label}</option>".format(val=_esc(a["email"]), label=_esc(a["name"]))
        out += "</select></td>"

        # Request button
        out += "<td style='padding:6px 8px;'>"
        out += "<a class='btn btn-primary'>Request</a>"
        out += """
<cwdb-action action="call" display="popup" endpoint="{endpoint}">
  {{ "action": "request_popup", "rowId": {rid} }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn), rid=rid)
        out += "</td>"

        # MFA input
        out += (
            "<td style='padding:6px 8px;'>"
            "<input name='{name}' placeholder='6-digit code' style='width:100%;max-width:160px;'/>"
            "</td>".format(name=_esc(k["mfa"]))
        )

        # Secret button
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

def _render_verify_popup(kind: str, rid: int,
                         client: Optional[str], account: Optional[str],
                         email: Optional[str], approver_email: Optional[str],
                         approver_name: Optional[str], mfa: Optional[str],
                         endpoint_arn: str) -> str:
    title = "Verify Request" if kind == "request" else "Verify Secret"
    out  = "<div style='padding:12px;max-width:640px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>{}</h3>".format(_esc(title))
    out += "<div style='line-height:1.7;'>"
    out += "<div><b>Client</b>: {}</div>".format(_esc(client))
    out += "<div><b>Account</b>: {}</div>".format(_esc(account))
    out += "<div><b>Requester Email</b>: {}</div>".format(_esc(email))
    if approver_email:
        shown = "{} ({})".format(approver_name or "", approver_email) if approver_name else approver_email
        out += "<div><b>Approver</b>: {}</div>".format(_esc(shown))
    else:
        out += "<div><b>Approver</b>: (none)</div>"
    out += "<div><b>MFA Code</b>: {}</div>".format(_esc(mfa))
    out += "</div><div style='height:10px;'></div>"

    # Confirm button
    confirm_action = "request_confirm" if kind == "request" else "secret_confirm"
    out += "<a class='btn btn-primary' style='margin-right:8px;'>Confirm</a>"
    out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "{confirm}", "rowId": {rid} }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn), confirm=_esc(confirm_action), rid=rid)

    # Close button
    out += "<a class='btn'>Close</a>"
    out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "back" }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn))

    out += "</div>"
    return out

def _render_ok(title: str, details: Dict[str, Any], endpoint_arn: str) -> str:
    out  = _banner(endpoint_arn)
    out += "<div style='padding:12px;'>"
    out += "<h3 style='margin:0 0 8px 0;'>{}</h3>".format(_esc(title))
    for k, v in details.items():
        out += "<div><b>{}</b>: <code>{}</code></div>".format(_esc(k), _esc(v))
    out += "<div style='height:8px;'></div><a class='btn'>Back</a>"
    out += """
<cwdb-action action="call" display="widget" endpoint="{endpoint}">
  {{ "action": "back" }}
</cwdb-action>
""".strip().format(endpoint=_esc(endpoint_arn))
    out += "</div>"
    return out

# =========================
# Entry point
# =========================
def lambda_handler(event: Dict[str, Any], context: Any):
    if event.get("describe"):
        return {
            "markdown": (
                "### Dynamic Request/Secret Widget (cross-region proxy)\n"
                "- Dashboard and THIS lambda must be in the same account/region.\n"
                "- Buttons call this lambda; this lambda invokes remote target lambdas.\n"
                "- Text columns (Client/Account) are mirrored as hidden inputs so they arrive in forms.all."
            )
        }

    wc      = (event or {}).get("widgetContext", {}) or {}
    params  = wc.get("params") or {}
    forms   = (wc.get("forms") or {}).get("all") or {}
    action  = params.get("action")
    rid     = params.get("rowId")
    endpoint_arn = getattr(context, "invoked_function_arn", "")

    # Initial/back -> render table
    if not action or action == "back" or rid is None:
        return _render_table(endpoint_arn)

    # Extract row values from forms
    dicts = _normalize_forms_all(forms)
    client, account, email, approver_email, approver_name, mfa = _extract_row(dicts, rid)

    # POPUP verification flows
    if action == "request_popup":
        return _render_verify_popup("request", rid, client, account, email, approver_email, approver_name, mfa, endpoint_arn)
    if action == "secret_popup":
        return _render_verify_popup("secret", rid, client, account, email, approver_email, approver_name, mfa, endpoint_arn)

    # Confirm → actually invoke target lambdas
    if action == "request_confirm":
        payload = {
            "client": client,
            "account": account,
            "requester_email": email,
            "approver_email": approver_email,
            "mfa_code": mfa,
        }
        _invoke_lambda(TARGET_REQUEST_LAMBDA_ARN, payload)
        return _render_ok("Request sent", payload, endpoint_arn)

    if action == "secret_confirm":
        payload = {
            "client": client,
            "account": account,
            "requester_email": email,
            "approver_email": approver_email,
            "mfa_code": mfa,
        }
        _invoke_lambda(TARGET_SECRET_LAMBDA_ARN, payload)
        return _render_ok("Secret request sent", payload, endpoint_arn)

    # Fallback
    return _render_table(endpoint_arn)