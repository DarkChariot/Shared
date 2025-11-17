<#
.SYNOPSIS
  Generic parser to transform structured data (CSV/JSON) into a new shape with selected fields.

.DESCRIPTION
  Reads an input file (CSV or JSON), extracts properties defined via -SelectFields, and emits either
  CSV or JSON. Useful for quickly reshaping exports without writing dedicated scripts.

.EXAMPLE
  .\Convert-StructuredData.ps1 -InputPath .\data\users.json -SelectFields DisplayName,Mail,Department `
                               -OutputFormat Csv -OutputPath .\data\users-trimmed.csv
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$InputPath,

  [string[]]$SelectFields,

  [ValidateSet('Csv','Json')]
  [string]$OutputFormat = 'Json',

  [string]$OutputPath = ".\exports\converted-data"
)

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

$data = Import-StructuredData -Path $InputPath
if (-not $data) {
  Write-Warning "No records found in $InputPath."
  return
}

if ($SelectFields -and $SelectFields.Count -gt 0) {
  $data = $data | Select-Object $SelectFields
}

$finalPath = Resolve-OutputPath -Path $OutputPath -Format $OutputFormat
$finalDir = Split-Path -Path $finalPath -Parent
if ($finalDir -and -not (Test-Path $finalDir)) {
  New-Item -ItemType Directory -Path $finalDir -Force | Out-Null
}

if ($OutputFormat -eq 'Json') {
  $data | ConvertTo-Json -Depth 6 | Out-File -FilePath $finalPath -Encoding utf8
} else {
  $data | Export-Csv -Path $finalPath -NoTypeInformation -Encoding UTF8
}

Write-Host "Converted data saved to: $finalPath" -ForegroundColor Green
