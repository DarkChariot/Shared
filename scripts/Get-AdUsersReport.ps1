<#
.SYNOPSIS
  Generates a detailed Active Directory user inventory.

.DESCRIPTION
  Queries Active Directory for user accounts (enabled by default) and exports
  the most relevant attributes to CSV or JSON. Supports optional scoping via
  SearchBase / Server, includes additional attributes, and can resolve manager
  display names. Intended to be run by an administrator with the RSAT AD module.

.EXAMPLE
  .\Get-AdUsersReport.ps1 -OutputPath .\exports\users.csv

.EXAMPLE
  .\Get-AdUsersReport.ps1 -IncludeDisabled -ResolveManager -OutputFormat Json `
    -OutputPath .\exports\users.json
#>
[CmdletBinding()]
param(
  [string]$SearchBase,
  [string]$Server,
  [switch]$IncludeDisabled,
  [switch]$ResolveManager,
  [ValidateSet('Csv', 'Json')]
  [string]$OutputFormat = 'Csv',
  [string]$OutputPath = ".\exports\ad-users-report"
)

function Ensure-ActiveDirectoryModule {
  if (-not (Get-Module -Name ActiveDirectory)) {
    Try {
      Import-Module ActiveDirectory -ErrorAction Stop
    } Catch {
      Throw "Unable to load the ActiveDirectory module. Install RSAT tools or run on a domain-joined server."
    }
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

Ensure-ActiveDirectoryModule

$properties = @(
  'GivenName','Surname','DisplayName','Mail','UserPrincipalName','SamAccountName',
  'Enabled','Department','Title','Company','Office','OfficePhone','MobilePhone',
  'LastLogonDate','PasswordLastSet','AccountExpirationDate','whenCreated','Manager'
)

$filterString = if ($IncludeDisabled) { '*' } else { 'Enabled -eq $true' }
$getParams = @{
  Filter     = $filterString
  Properties = $properties
}
if ($SearchBase) { $getParams.SearchBase = $SearchBase }
if ($Server) { $getParams.Server = $Server }

Write-Host "Querying Active Directory users..." -ForegroundColor Cyan
$users = Get-ADUser @getParams | Sort-Object DisplayName

if ($ResolveManager) {
  Write-Host "Resolving manager display names..." -ForegroundColor DarkCyan
  foreach ($user in $users) {
    if ($user.Manager) {
      try {
        $manager = Get-ADUser -Identity $user.Manager -Properties DisplayName -Server $Server
        $user | Add-Member -NotePropertyName ManagerDisplayName -NotePropertyValue $manager.DisplayName -Force
      } catch {
        $user | Add-Member -NotePropertyName ManagerDisplayName -NotePropertyValue $user.Manager -Force
      }
    } else {
      $user | Add-Member -NotePropertyName ManagerDisplayName -NotePropertyValue $null -Force
    }
  }
}

$outputObjects = $users | Select-Object `
  SamAccountName, DisplayName, GivenName, Surname,
  UserPrincipalName, Mail, Enabled,
  Department, Title, Company, Office,
  OfficePhone, MobilePhone,
  @{ Name = 'Manager'; Expression = { if ($ResolveManager) { $_.ManagerDisplayName } else { $_.Manager } } },
  LastLogonDate, PasswordLastSet, AccountExpirationDate, whenCreated

$finalPath = Resolve-OutputPath -Path $OutputPath -Format $OutputFormat
$finalDirectory = Split-Path -Path $finalPath -Parent
if ($finalDirectory -and -not (Test-Path $finalDirectory)) {
  New-Item -ItemType Directory -Path $finalDirectory -Force | Out-Null
}

if ($OutputFormat -eq 'Json') {
  $outputObjects | ConvertTo-Json -Depth 5 | Out-File -FilePath $finalPath -Encoding utf8
} else {
  $outputObjects | Export-Csv -Path $finalPath -NoTypeInformation -Encoding UTF8
}

Write-Host "Export complete: $finalPath" -ForegroundColor Green
Write-Host "Total users exported: $($outputObjects.Count)" -ForegroundColor Green
