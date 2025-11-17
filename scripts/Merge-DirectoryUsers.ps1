<#
.SYNOPSIS
  Merges on-prem AD user data with Microsoft 365 user data to create a single record per identity.

.DESCRIPTION
  Accepts two data exports (CSV or JSON) – one for Active Directory users and one for Microsoft 365 users –
  and attempts to match records based on user principal name (UPN) or SAM account name. The resulting merged
  dataset retains key information from both sources so you can compare identity state.

.EXAMPLE
  .\Merge-DirectoryUsers.ps1 -AdInputPath .\exports\ad-users-report.csv `
                             -M365InputPath .\exports\m365-users-report.csv `
                             -OutputPath .\exports\directory-merge.csv
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$AdInputPath,

  [Parameter(Mandatory)]
  [string]$M365InputPath,

  [ValidateSet('Csv','Json')]
  [string]$OutputFormat = 'Csv',

  [string]$OutputPath = ".\exports\directory-merge"
)

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

function Import-StructuredData {
  param([string]$Path)

  if (-not (Test-Path $Path)) {
    throw "Input file not found: $Path"
  }

  $ext = [System.IO.Path]::GetExtension($Path).ToLowerInvariant()
  switch ($ext) {
    '.json' { return (Get-Content -Raw -Path $Path | ConvertFrom-Json) }
    '.csv'  { return Import-Csv -Path $Path }
    default { throw "Unsupported file type '$ext'. Use CSV or JSON." }
  }
}

function Get-NormalizedKey {
  param($Record)
  $possible = @()
  foreach ($prop in @('UserPrincipalName','userPrincipalName','UPN','Mail','mail','PrimaryEmail','SamAccountName','samAccountName')) {
    if ($Record.PSObject.Properties[$prop] -and $Record.$prop) {
      $possible += $Record.$prop.ToString().ToLowerInvariant()
    }
  }
  $possible = $possible | Where-Object { $_ -ne '' }
  if ($possible) { return $possible[0] }
  return $null
}

function Select-Value {
  param([Parameter(ValueFromRemainingArguments=$true)][object[]]$Values)
  foreach ($value in $Values) {
    if ($value -ne $null -and $value -ne '') { return $value }
  }
  return $null
}

$adRecords = Import-StructuredData -Path $AdInputPath
$m365Records = Import-StructuredData -Path $M365InputPath

Write-Host "Loaded $($adRecords.Count) AD records and $($m365Records.Count) M365 records." -ForegroundColor Cyan

$combinedMap = @{}

foreach ($record in $adRecords) {
  $key = Get-NormalizedKey -Record $record
  if (-not $key) { continue }
  $combinedMap[$key] = [ordered]@{
    MatchKey               = $key
    DisplayName            = $record.DisplayName
    AdSamAccountName       = $record.SamAccountName
    AdUserPrincipalName    = Select-Value $record.UserPrincipalName $record.Mail
    AdMail                 = $record.Mail
    Department             = $record.Department
    Title                  = Select-Value $record.Title $record.JobTitle
    Company                = $record.Company
    Office                 = $record.Office
    Phone                  = Select-Value $record.OfficePhone $record.MobilePhone
    AdEnabled              = $record.Enabled
    AdLastLogon            = $record.LastLogonDate
    AdWhenCreated          = $record.whenCreated
    M365UserPrincipalName  = $null
    M365Mail               = $null
    M365AccountEnabled     = $null
    M365UserType           = $null
    M365LastSignIn         = $null
    Source                 = 'AD only'
  }
}

foreach ($record in $m365Records) {
  $key = Get-NormalizedKey -Record $record
  if (-not $key) { continue }
  if (-not $combinedMap.ContainsKey($key)) {
    $combinedMap[$key] = [ordered]@{
      MatchKey               = $key
      DisplayName            = $record.DisplayName
      AdSamAccountName       = $null
      AdUserPrincipalName    = $null
      AdMail                 = $null
      Department             = $record.Department
      Title                  = Select-Value $record.JobTitle
      Company                = $record.CompanyName
      Office                 = $record.OfficeLocation
      Phone                  = Select-Value $record.BusinessPhones $record.MobilePhone
      AdEnabled              = $null
      AdLastLogon            = $null
      AdWhenCreated          = $null
      M365UserPrincipalName  = Select-Value $record.UserPrincipalName $record.Mail
      M365Mail               = $record.Mail
      M365AccountEnabled     = Select-Value $record.AccountEnabled
      M365UserType           = $record.UserType
      M365LastSignIn         = $record.LastInteractiveSignIn
      Source                 = 'M365 only'
    }
  } else {
    $entry = $combinedMap[$key]
    $entry.DisplayName           = Select-Value $entry.DisplayName $record.DisplayName
    $entry.Department            = Select-Value $entry.Department $record.Department
    $entry.Title                 = Select-Value $entry.Title $record.JobTitle
    $entry.Company               = Select-Value $entry.Company $record.CompanyName
    $entry.Office                = Select-Value $entry.Office $record.OfficeLocation
    $entry.Phone                 = Select-Value $entry.Phone ($record.BusinessPhones -join '; ') $record.MobilePhone
    $entry.M365UserPrincipalName = Select-Value $entry.M365UserPrincipalName $record.UserPrincipalName $record.Mail
    $entry.M365Mail              = Select-Value $entry.M365Mail $record.Mail
    $entry.M365AccountEnabled    = Select-Value $entry.M365AccountEnabled $record.AccountEnabled
    $entry.M365UserType          = Select-Value $entry.M365UserType $record.UserType
    $entry.M365LastSignIn        = Select-Value $entry.M365LastSignIn $record.LastInteractiveSignIn
    $entry.Source                = 'Matched'
  }
}

$mergedList = $combinedMap.Values |
  Sort-Object DisplayName, MatchKey |
  ForEach-Object {
    [pscustomobject]$_
  }

$finalPath = Resolve-OutputPath -Path $OutputPath -Format $OutputFormat
$finalDir = Split-Path -Path $finalPath -Parent
if ($finalDir -and -not (Test-Path $finalDir)) {
  New-Item -ItemType Directory -Path $finalDir -Force | Out-Null
}

if ($OutputFormat -eq 'Json') {
  $mergedList | ConvertTo-Json -Depth 6 | Out-File -FilePath $finalPath -Encoding utf8
} else {
  $mergedList | Export-Csv -Path $finalPath -Encoding UTF8 -NoTypeInformation
}

Write-Host "Merged report created: $finalPath" -ForegroundColor Green
Write-Host "Matched users: $(@($mergedList | Where-Object { $_.Source -eq 'Matched' }).Count)" -ForegroundColor Green
