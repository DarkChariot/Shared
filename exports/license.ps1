<#
.SYNOPSIS
  Export M365 license assignments for all users via Microsoft Graph and email the results.

.DESCRIPTION
  - Connects to Graph with read-only directory scopes + Mail.Send
  - Pulls tenant subscribed SKUs (SkuId -> SkuPartNumber)
  - Exports:
      * M365_User_Licenses_yyyyMMdd_HHmmss.csv
      * M365_Tenant_SKUs_yyyyMMdd_HHmmss.csv
  - (Optional) Emails the files to a group/DL/recipients

.PARAMETER OutputFolder
  Target folder for CSVs (default: ./exports)

.PARAMETER IncludeServicePlans
  Include per-user plan enablement lists (EnabledPlans, DisabledPlans)

.PARAMETER OnlyLicensed
  Only include users with at least one license

.PARAMETER EmailTo
  One or more SMTP addresses (DL, M365 group, or individuals). If omitted, no email is sent.

.PARAMETER EmailCc
  Optional CC recipients

.PARAMETER EmailSubject
  Custom subject; default includes timestamp

.PARAMETER SendAsUpn
  Send as a specific mailbox (shared mailbox, etc.). Requires Send As / Mail.Send for that user.
#>

[CmdletBinding()]
param(
  [Parameter()][string]$OutputFolder = (Join-Path -Path $PSScriptRoot -ChildPath "exports"),
  [Parameter()][switch]$IncludeServicePlans,
  [Parameter()][switch]$OnlyLicensed,

  # Email params (optional)
  [Parameter()][string[]]$EmailTo,
  [Parameter()][string[]]$EmailCc,
  [Parameter()][string]$EmailSubject,
  [Parameter()][string]$SendAsUpn
)

#---------------------------#
# Utility: Logging
#---------------------------#
function Write-Log {
  param(
    [Parameter(Mandatory)][ValidateSet('INFO','WARN','ERROR','OK')][string]$Level,
    [Parameter(Mandatory)][string]$Message
  )
  $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  $c = switch ($Level) {
    'INFO'  { 'Cyan' }
    'WARN'  { 'Yellow' }
    'ERROR' { 'Red' }
    'OK'    { 'Green' }
  }
  Write-Host "[$ts][$Level] $Message" -ForegroundColor $c
}

#---------------------------#
# Email helpers
#---------------------------#
function Get-MimeType {
  param([Parameter(Mandatory)][string]$FilePath)
  switch ([IO.Path]::GetExtension($FilePath).ToLower()) {
    '.csv' { 'text/csv' }
    '.txt' { 'text/plain' }
    '.zip' { 'application/zip' }
    default { 'application/octet-stream' }
  }
}

function New-GraphFileAttachment {
  param([Parameter(Mandatory)][string]$FilePath)
  if (-not (Test-Path -LiteralPath $FilePath)) { throw "Attachment not found: $FilePath" }
  $bytes = [System.IO.File]::ReadAllBytes($FilePath)
  $b64   = [Convert]::ToBase64String($bytes)
  [ordered]@{
    "@odata.type" = "#microsoft.graph.fileAttachment"
    name          = [IO.Path]::GetFileName($FilePath)
    contentType   = Get-MimeType -FilePath $FilePath
    contentBytes  = $b64
  }
}

function Send-LicenseReportEmail {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][string[]]$To,
    [Parameter()][string[]]$Cc,
    [Parameter(Mandatory)][string]$Subject,
    [Parameter(Mandatory)][string]$BodyHtml,
    [Parameter(Mandatory)][string[]]$Attachments,
    [Parameter()][string]$SendAsUpn
  )
  if (-not $To -or $To.Count -eq 0) { throw "Parameter -To requires at least one recipient." }

  $toObjs = $To | ForEach-Object { @{ emailAddress = @{ address = $_ } } }

  $ccObjs = @()
  if ($Cc) { $ccObjs = $Cc | ForEach-Object { @{ emailAddress = @{ address = $_ } } } }

  # Validate and create attachment objects; simple fileAttachment has ~3 MB limit
  $attObjs = @()
  if ($Attachments) { Write-Log INFO "Preparing attachments..." }
  foreach ($p in ($Attachments | Where-Object { $_ })) {
    if (-not (Test-Path -LiteralPath $p)) { throw "Attachment not found: $p" }
    $size = (Get-Item -LiteralPath $p).Length
    Write-Log INFO "Attachment found: $(Split-Path -Leaf $p) - $size bytes"
    if ($size -gt 3MB) { throw "Attachment too large for simple Graph fileAttachment (>3MB): $p" }
    $attObjs += New-GraphFileAttachment -FilePath $p
  }

  $msg = @{ subject = $Subject; body = @{ contentType = 'HTML'; content = $BodyHtml }; toRecipients = $toObjs }
  if ($ccObjs.Count -gt 0)  { $msg.ccRecipients  = $ccObjs }
  if ($attObjs.Count -gt 0) { $msg.attachments   = $attObjs }

  try {
    Write-Log INFO "Sending mail (SaveToSentItems=$true) as: $([string]::IsNullOrEmpty($SendAsUpn) ? 'me' : $SendAsUpn) to $($To -join ', ')"
    if ($SendAsUpn) {
      Send-MgUserMail -UserId $SendAsUpn -Message $msg -SaveToSentItems:$true -ErrorAction Stop
    } else {
      Send-MgUserMail -UserId 'me' -Message $msg -SaveToSentItems:$true -ErrorAction Stop
    }
    Write-Log OK "Email successfully sent to: $($To -join ', ')"
    return $true
  } catch {
    Write-Log ERROR "Failed to send message via Microsoft Graph: $($_.Exception.Message)"
    throw "Failed to send message via Microsoft Graph: $($_.Exception.Message)"
  }
}

#---------------------------#
# Prep
#---------------------------#
if (-not (Test-Path -LiteralPath $OutputFolder)) {
  New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

$stamp  = (Get-Date).ToString('yyyyMMdd_HHmmss')
$userCsv = Join-Path $OutputFolder "M365_User_Licenses_${stamp}.csv"
$skuCsv  = Join-Path $OutputFolder "M365_Tenant_SKUs_${stamp}.csv"

#---------------------------#
# Graph module + connect
#---------------------------#
if (-not (Get-Module -ListAvailable -Name Microsoft.Graph)) {
  Write-Log INFO "Microsoft.Graph module not found. Installing..."
  try {
    Install-Module Microsoft.Graph -Scope CurrentUser -Force -ErrorAction Stop
    Write-Log OK "Installed Microsoft.Graph."
  } catch {
    Write-Log ERROR "Failed to install Microsoft.Graph: $($_.Exception.Message)"
    throw
  }
}
Import-Module Microsoft.Graph -ErrorAction Stop

# Add Mail.Send for email support
$scopes = @('User.Read.All','Directory.Read.All','Organization.Read.All','Mail.Send')

Write-Log INFO "Connecting to Microsoft Graph..."
try {
  Connect-MgGraph -Scopes $scopes -NoWelcome
  $ctx = Get-MgContext
  Write-Log OK "Connected to Graph. Tenant: $($ctx.TenantId)"
} catch {
  Write-Log ERROR "Graph connection failed: $($_.Exception.Message)"
  throw
}

#---------------------------#
# Get tenant SKUs
#---------------------------#
Write-Log INFO "Fetching tenant subscribed SKUs..."
try { $skus = Get-MgSubscribedSku -All } catch {
  Write-Log ERROR "Failed to retrieve subscribed SKUs: $($_.Exception.Message)"; throw
}
if (-not $skus) { Write-Log WARN "No subscribed SKUs found."; $skus = @() }

# Build SkuId -> details map
$SkuMap = @{}
foreach ($s in $skus) {
  $skuIdStr = [string]$s.SkuId
  $SkuMap[$skuIdStr] = [PSCustomObject]@{
    SkuId         = $skuIdStr
    SkuPartNumber = $s.SkuPartNumber
    AppliesTo     = $s.AppliesTo
    ConsumedUnits = $s.ConsumedUnits
    PrepaidUnits  = $s.PrepaidUnits
    ServicePlans  = $s.ServicePlans
  }
}

# Precompute planId -> planName map (used if IncludeServicePlans)
$PlanNameById = @{}
foreach ($kv in $SkuMap.GetEnumerator()) {
  foreach ($sp in ($kv.Value.ServicePlans | Where-Object { $_.ServicePlanId })) {
    $PlanNameById[[string]$sp.ServicePlanId] = $sp.ServicePlanName
  }
}

Write-Log INFO "Built SkuMap with $($SkuMap.Count) SKUs and PlanNameById with $($PlanNameById.Count) service plans"

# Export SKU inventory
Write-Log INFO "Exporting SKU inventory -> $skuCsv"
$skus | ForEach-Object {
  [PSCustomObject]@{
    SkuId             = $_.SkuId
    SkuPartNumber     = $_.SkuPartNumber
    AppliesTo         = $_.AppliesTo
    ConsumedUnits     = $_.ConsumedUnits
    Prepaid_Enabled   = $_.PrepaidUnits.Enabled
    Prepaid_Suspended = $_.PrepaidUnits.Suspended
    Prepaid_Warning   = $_.PrepaidUnits.Warning
    ServicePlans      = ($_.ServicePlans | ForEach-Object { $_.ServicePlanName } | Sort-Object -Unique) -join '; '
  }
} | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $skuCsv
Write-Log OK "SKU inventory exported."

#---------------------------#
# Get users + license fields
#---------------------------#
Write-Log INFO "Fetching users..."
$props = @(
  'id','displayName','userPrincipalName','mail','userType','accountEnabled',
  'createdDateTime','assignedLicenses','assignedPlans'
) -join ','
try { $allUsers = Get-MgUser -All -Property $props } catch {
  Write-Log ERROR "Failed to retrieve users: $($_.Exception.Message)"; throw
}
Write-Log OK "Retrieved $($allUsers.Count) users."

if ($OnlyLicensed) {
  $allUsers = $allUsers | Where-Object { $_.AssignedLicenses -and $_.AssignedLicenses.Count -gt 0 }
  Write-Log INFO "Filtered to licensed users: $($allUsers.Count)"
}

#---------------------------#
# Build user license rows
#---------------------------#
Write-Log INFO "Processing license data per user..."
$userCounter = 0
$progressInterval = 100
$results = foreach ($u in $allUsers) {
  $userCounter++
  if ($userCounter % $progressInterval -eq 0) {
    Write-Log INFO "Processed $userCounter / $($allUsers.Count) users..."
  }
  $userSkuIds = @()
  if ($u.AssignedLicenses) {
    $userSkuIds = $u.AssignedLicenses | ForEach-Object { [string]$_.SkuId } | Sort-Object -Unique
  }

  $userSkuNames = foreach ($sid in $userSkuIds) {
    if ($SkuMap.ContainsKey($sid)) { $SkuMap[$sid].SkuPartNumber } else { $sid }
  }

  $enabledPlans = @()
  $disabledPlans = @()
  if ($IncludeServicePlans -and $u.AssignedPlans) {
    foreach ($ap in $u.AssignedPlans) {
      $pid = [string]$ap.ServicePlanId
      $pname = $PlanNameById[$pid]; if (-not $pname) { $pname = $pid }
      switch ([string]$ap.CapabilityStatus) {
        'Enabled'   { $enabledPlans  += $pname }
        'Suspended' { $disabledPlans += "$pname (Suspended)" }
        'Deleted'   { $disabledPlans += "$pname (Deleted)" }
        default     { $disabledPlans += "$pname ($($ap.CapabilityStatus))" }
      }
    }
    $enabledPlans  = $enabledPlans  | Sort-Object -Unique
    $disabledPlans = $disabledPlans | Sort-Object -Unique
  }

  [PSCustomObject]@{
    DisplayName            = $u.DisplayName
    UserPrincipalName      = $u.UserPrincipalName
    Mail                   = $u.Mail
    UserType               = $u.UserType
    AccountEnabled         = $u.AccountEnabled
    CreatedDateTime        = $u.CreatedDateTime
    Licensed               = ($userSkuIds.Count -gt 0)
    LicenseSkuIds          = ($userSkuIds -join '; ')
    LicenseSkuPartNumbers  = ($userSkuNames -join '; ')
    EnabledPlans           = if ($IncludeServicePlans) { ($enabledPlans -join '; ') } else { $null }
    DisabledPlans          = if ($IncludeServicePlans) { ($disabledPlans -join '; ') } else { $null }
  }
}

# Export users
Write-Log INFO "Writing user license export -> $userCsv"
$results | Sort-Object UserPrincipalName | Export-Csv -Path $userCsv -NoTypeInformation -Encoding UTF8
Write-Log OK "Done. Rows exported: $($results.Count)"
Write-Host " - User licenses: $userCsv"
Write-Host " - SKU inventory: $skuCsv"

#---------------------------#
# Email (optional)
#---------------------------#
if ($EmailTo -and $EmailTo.Count -gt 0) {
  $subject = if ($EmailSubject) { $EmailSubject } else { "M365 License Export — $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
  $body = @"
<p>Hi team,</p>
<p>Attached are the latest Microsoft 365 license reports:</p>
<ul>
  <li><b>User Licenses</b> — one row per user with assigned SKUs$(if ($IncludeServicePlans) { ' and service plan enablement' } else { '' }).</li>
  <li><b>Tenant SKU Inventory</b> — counts and available service plans per SKU.</li>
</ul>
<p>Generated on <code>$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')</code>.</p>
"@

  Write-Log INFO "Sending email to: $($EmailTo -join ', ')"
  try {
    Send-LicenseReportEmail `
      -To $EmailTo `
      -Cc $EmailCc `
      -Subject $subject `
      -BodyHtml $body `
      -Attachments @($userCsv, $skuCsv) `
      -SendAsUpn $SendAsUpn
    Write-Log OK "Email sent."
  } catch {
    Write-Log ERROR "Failed to send email: $($_.Exception.Message)"
  }
} else {
  Write-Log INFO "No EmailTo specified; skipping email."
}

# Optionally:
# Disconnect-MgGraph
