<#
.SYNOPSIS
  Generates a Microsoft 365 user inventory via Microsoft Graph PowerShell.

.DESCRIPTION
  Connects to Microsoft Graph, queries cloud users, and exports key profile,
  org, and sign-in fields to CSV or JSON. Mirrors the on-prem AD report so you
  can compare both datasets.

.NOTES
  Requires the Microsoft Graph PowerShell SDK (Install-Module Microsoft.Graph).
  The account running this script needs at least User.Read.All (and optionally
  Directory.Read.All for extra properties).
#>
[CmdletBinding()]
param(
  [ValidateSet('Csv','Json')]
  [string]$OutputFormat = 'Csv',

  [string]$OutputPath = ".\exports\m365-users-report",

  [string[]]$Scopes = @('User.Read.All','Directory.Read.All'),

  [switch]$IncludeGuests,

  [switch]$IncludeBlocked,

  [switch]$ResolveManager,

  [switch]$SkipConnect
)

function Ensure-GraphModule {
  if (-not (Get-Module -Name Microsoft.Graph.Users -ListAvailable)) {
    throw "Microsoft.Graph PowerShell SDK not found. Install with: Install-Module Microsoft.Graph -Scope CurrentUser"
  }
  Import-Module Microsoft.Graph.Users -ErrorAction Stop | Out-Null
}

function Ensure-GraphConnection {
  param(
    [string[]]$Scopes,
    [switch]$SkipConnect
  )
  $ctx = Get-MgContext -ErrorAction SilentlyContinue
  $needsConnect = $false
  if (-not $ctx) {
    $needsConnect = $true
  } elseif ($Scopes) {
    $missingScopes = $Scopes | Where-Object { $_ -notin $ctx.Scopes }
    if ($missingScopes) { $needsConnect = $true }
  }

  if ($needsConnect -and -not $SkipConnect) {
    Connect-MgGraph -Scopes $Scopes -NoWelcome
  } elseif ($needsConnect -and $SkipConnect) {
    Write-Warning "No existing Graph connection detected. Remove -SkipConnect or connect manually."
  }
}

function Resolve-OutputPath {
  param(
    [string]$Path,
    [string]$Format
  )
  $extension = if ($Format -eq 'Json') { '.json' } else { '.csv' }
  if ([System.IO.Path]::GetExtension($Path)) {
    return $Path
  }
  return ([System.IO.Path]::ChangeExtension($Path, $extension.TrimStart('.')))
}

Ensure-GraphModule
Ensure-GraphConnection -Scopes $Scopes -SkipConnect:$SkipConnect

$graphProperties = @(
  'id','displayName','givenName','surname','userPrincipalName','mail',
  'mailNickname','jobTitle','department','companyName','officeLocation',
  'businessPhones','mobilePhone','usageLocation','city','state','country',
  'preferredLanguage','accountEnabled','userType','createdDateTime',
  'lastPasswordChangeDateTime','signInActivity'
)

$filterParts = @()
if (-not $IncludeGuests) { $filterParts += "userType eq 'Member'" }
if (-not $IncludeBlocked) { $filterParts += 'accountEnabled eq true' }
$filterClause = $null
if ($filterParts.Count -gt 0) {
  $filterClause = $filterParts -join ' and '
}

Write-Host "Pulling Microsoft 365 users from Graph..." -ForegroundColor Cyan
$users = Get-MgUser `
  -All `
  -Property $graphProperties `
  -Filter $filterClause `
  -ConsistencyLevel eventual

if ($ResolveManager) {
  Write-Host "Resolving manager names..." -ForegroundColor DarkCyan
  foreach ($user in $users) {
    try {
      $manager = Get-MgUserManager -UserId $user.Id -ErrorAction Stop
      $user | Add-Member -NotePropertyName ManagerDisplayName -NotePropertyValue $manager.AdditionalProperties.displayName -Force
    } catch {
      $user | Add-Member -NotePropertyName ManagerDisplayName -NotePropertyValue $null -Force
    }
  }
}

$ouputObjects = $users | Select-Object `
  UserPrincipalName, DisplayName, GivenName, Surname,
  Mail, MailNickname, userType,
  AccountEnabled,
  Department, JobTitle, CompanyName, OfficeLocation,
  @{Name='BusinessPhones';Expression={($_.BusinessPhones -join '; ')}},
  MobilePhone,
  UsageLocation, City, State, Country, PreferredLanguage,
  CreatedDateTime, LastPasswordChangeDateTime,
  @{Name='LastInteractiveSignIn';Expression={ $_.SignInActivity.lastSignInDateTime }},
  @{Name='Manager';Expression={ if ($ResolveManager) { $_.ManagerDisplayName } else { $null } }}

$finalPath = Resolve-OutputPath -Path $OutputPath -Format $OutputFormat
$finalDirectory = Split-Path -Path $finalPath -Parent
if ($finalDirectory -and -not (Test-Path $finalDirectory)) {
  New-Item -ItemType Directory -Path $finalDirectory -Force | Out-Null
}

if ($OutputFormat -eq 'Json') {
  $ouputObjects | ConvertTo-Json -Depth 6 | Out-File -FilePath $finalPath -Encoding utf8
} else {
  $ouputObjects | Export-Csv -Path $finalPath -NoTypeInformation -Encoding UTF8
}

Write-Host "Graph export complete: $finalPath" -ForegroundColor Green
Write-Host "Total users exported: $($ouputObjects.Count)" -ForegroundColor Green
