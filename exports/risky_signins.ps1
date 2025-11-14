<#
.SYNOPSIS
  Email a single HTML report of ALL risky sign-ins (Low/Medium/High; interactive + non-interactive)
  using Microsoft Graph. Handles empty results cleanly and auto-falls back to client-side filtering.

.REQUIREMENTS
  - Microsoft.Graph PowerShell SDK
  - Scopes: AuditLog.Read.All, Mail.Send
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$To,

  [int]$LookbackHours = 24,

  # Attach a CSV of the same rows
  [switch]$AttachCsv,

  # Force client-side filter (skip server-side risk filter entirely)
  [switch]$ClientSideFilter
)

#region Helpers
function Write-Log {
  param([string]$Msg, [ValidateSet('INFO','OK','WARN','ERR')]$Level='INFO')
  $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  $tag = @{INFO='[INFO] ';OK='[ OK ] ';WARN='[WARN] ';ERR='[ERR ] '}[$Level]
  Write-Host "$ts $tag$Msg"
}

function Ensure-GraphModules {
  try {
    if (-not (Get-Module Microsoft.Graph -ListAvailable)) {
      Write-Log "Microsoft.Graph not found. Installing (CurrentUser)..." 'WARN'
      Install-Module Microsoft.Graph -Scope CurrentUser -Force -AllowClobber
    }
    if (-not (Get-Module Microsoft.Graph.Reports -ListAvailable)) {
      Write-Log "Microsoft.Graph.Reports not found. Installing (CurrentUser)..." 'WARN'
      Install-Module Microsoft.Graph.Reports -Scope CurrentUser -Force -AllowClobber
    }
    Import-Module Microsoft.Graph -ErrorAction Stop
    Import-Module Microsoft.Graph.Reports -ErrorAction Stop
    Write-Log "Microsoft.Graph modules loaded." 'OK'
  } catch {
    Write-Log "Failed loading Microsoft.Graph modules: $($_.Exception.Message)" 'ERR'
    throw
  }
}

function Connect-GraphSafe {
  $scopes = @('AuditLog.Read.All','Mail.Send')
  Write-Log "Connecting to Graph (scopes: $($scopes -join ', '))..."
  Connect-MgGraph -Scopes $scopes -NoWelcome
  $ctx = Get-MgContext
  Write-Log "Connected as $($ctx.Account) (Tenant $($ctx.TenantId))." 'OK'
}

# HTML table helper that tolerates empty data
function Convert-ObjectsToHtmlTable {
  param(
    [AllowEmptyCollection()][object[]]$Data,
    [string]$Title = 'All Risky Sign-ins',
    [string]$WindowMeta = ''
  )
  $style = @"
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:12px}
h2,h3{margin-bottom:6px}
.meta{font-size:12px;color:#555;margin-top:0}
table{border-collapse:collapse;width:100%;margin:10px 0 20px 0}
th,td{border:1px solid #ddd;padding:6px 8px;font-size:12px}
th{background:#f3f3f3;text-align:left}
tr:nth-child(even){background:#fafafa}
</style>
"@
  $header = "<h2>$Title</h2><p class='meta'>$WindowMeta</p>"

  if (-not $Data -or $Data.Count -eq 0) {
    return ($style + $header + "<p><i>No risky sign-ins found for this window.</i></p>")
  }

  $Data | ConvertTo-Html -As Table -PreContent ($style + $header) `
    -Property WhenUTC,RiskLevel,RiskAgg,RiskDuring,IsInteractive,User,UPN,App,ClientApp,IP,City,State,Country,RiskDetail,RiskEvents,ErrorCode,FailureReason,SignInId `
    | Out-String
}
#endregion Helpers

#region Main
try {
  Ensure-GraphModules
  Connect-GraphSafe

  $sinceIso = (Get-Date).AddHours(-1 * $LookbackHours).ToUniversalTime().ToString("o")
  Write-Log "Time window: last $LookbackHours hour(s) since $sinceIso"

  $useClientFilter = $ClientSideFilter.IsPresent

  # Preferred server-side risk filter
  $serverFilter = "(riskLevelAggregated ne 'none' or riskLevelDuringSignIn ne 'none') and createdDateTime ge $sinceIso"

  Write-Log ("Querying sign-ins " + ($(if($useClientFilter){"(client-side filtering)"}else{"(server-side risk filter)"})) + "...")

  $raw = @()
  if (-not $useClientFilter) {
    try {
      $raw = Get-MgAuditLogSignIn -Filter $serverFilter -All
      if (-not $raw -or $raw.Count -eq 0) {
        Write-Log "Server-side returned 0 rows. Double-checking via client-side filter..." 'WARN'
        $timeFilter = "createdDateTime ge $sinceIso"
        $raw = Get-MgAuditLogSignIn -Filter $timeFilter -All
        $useClientFilter = $true
      }
    } catch {
      Write-Log "Server-side filter failed: $($_.Exception.Message)" 'WARN'
      Write-Log "Falling back to client-side filter for this run." 'WARN'
      $useClientFilter = $true
    }
  }

  if ($useClientFilter) {
    if (-not $raw -or $raw.Count -eq 0) {
      $timeFilter = "createdDateTime ge $sinceIso"
      $raw = Get-MgAuditLogSignIn -Filter $timeFilter -All
    }
  }

  # Flatten & (optionally) filter in memory
  $rows = @()
  if ($raw) {
    $rows = $raw | ForEach-Object {
      $risk = $_.riskLevelAggregated
      if ([string]::IsNullOrWhiteSpace($risk)) { $risk = $_.riskLevelDuringSignIn }

      if ($useClientFilter -and ($risk -eq $null -or $risk -eq '' -or $risk -eq 'none')) {
        return
      }

      $loc    = $_.location
      $status = $_.status
      [pscustomobject]@{
        WhenUTC       = $_.createdDateTime
        RiskLevel     = $risk
        RiskAgg       = $_.riskLevelAggregated
        RiskDuring    = $_.riskLevelDuringSignIn
        IsInteractive = $_.isInteractive
        User          = $_.userDisplayName
        UPN           = $_.userPrincipalName
        App           = $_.appDisplayName
        ClientApp     = $_.clientAppUsed
        IP            = $_.ipAddress
        City          = if ($loc) { $loc.city } else { $null }
        State         = if ($loc) { $loc.state } else { $null }
        Country       = if ($loc) { $loc.countryOrRegion } else { $null }
        RiskDetail    = $_.riskDetail
        RiskEvents    = ($_.riskEventTypes -join ', ')
        ErrorCode     = if ($status) { $status.errorCode } else { $null }
        FailureReason = if ($status) { $status.failureReason } else { $null }
        SignInId      = $_.id
      }
    }

    # Sort High > Medium > Low, then newest
    $rank = @{ high=3; medium=2; low=1 }
    $rows = $rows | Sort-Object `
      @{ e = { if($_.RiskLevel -and $rank.ContainsKey($_.RiskLevel)) { $rank[$_.RiskLevel] } else { 0 } }; Descending = $true }, `
      @{ e = 'WhenUTC'; Descending = $true }
  }

  Write-Log ("Rows after filtering: " + ($rows.Count))

  # Summaries (work even if empty)
  $summaryRisk = if ($rows.Count) {
    ($rows | Group-Object RiskLevel | Sort-Object Name -Descending | ForEach-Object { "{0}: {1}" -f ($_.Name ?? 'unknown'), $_.Count }) -join ' • '
  } else { 'None' }
  $summaryInt  = if ($rows.Count) {
    ($rows | Group-Object IsInteractive | ForEach-Object { if ($_.Name -eq $true) { "Interactive: $($_.Count)" } else { "Non-Interactive: $($_.Count)" } }) -join ' • '
  } else { 'Interactive: 0 • Non-Interactive: 0' }

  $windowMeta = "Window: last $LookbackHours h (since $sinceIso)<br/>Total rows: $($rows.Count)<br/>Risk: $summaryRisk<br/>Mode: $summaryInt"

  # HTML (now tolerant of empty $rows)
  $html = Convert-ObjectsToHtmlTable -Data $rows -Title 'All Risky Sign-ins (Low/Medium/High)' -WindowMeta $windowMeta

  # Optional CSV
  $attachments = @()
  $tempCsv = $null
  if ($AttachCsv -and $rows.Count -gt 0) {
    $tempCsv = Join-Path $env:TEMP ("risky_signins_{0:yyyyMMddHHmmss}.csv" -f (Get-Date))
    $rows | Export-Csv -Path $tempCsv -NoTypeInformation -Encoding UTF8
    $attachments += @{
      "@odata.type" = "#microsoft.graph.fileAttachment"
      name          = [IO.Path]::GetFileName($tempCsv)
      contentType   = "text/csv"
      contentBytes  = [Convert]::ToBase64String([IO.File]::ReadAllBytes($tempCsv))
    }
    Write-Log "Prepared CSV attachment: $tempCsv" 'OK'
  }

  # Send mail
  $from = (Get-MgContext).Account
  $msg  = @{
    subject      = "All Risky Sign-ins | Last $LookbackHours h | Total=$($rows.Count)"
    body         = @{ contentType = "HTML"; content = $html }
    toRecipients = @(@{ emailAddress = @{ address = $To } })
  }
  if ($attachments.Count) { $msg['attachments'] = $attachments }

  Write-Log "Sending report email to $To…"
  Send-MgUserMail -UserId $from -Message $msg -SaveToSentItems
  Write-Log "Email sent." 'OK'
}
catch {
  Write-Log ("Fatal error: " + $_.Exception.Message) 'ERR'
  throw
}
finally {
  if ($tempCsv -and (Test-Path $tempCsv)) { Remove-Item $tempCsv -Force -ErrorAction SilentlyContinue }
  Disconnect-MgGraph | Out-Null
}
#endregion Main
