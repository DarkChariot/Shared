# PowerShell script to read IP addresses from a CSV file and cross-reference them against AWS IP ranges from https://ip-ranges.amazonaws.com/ip-ranges.json.

# Parameters:
# -CsvPath: Path to the input CSV file (required). Assumes the CSV has a column named 'IPAddress' containing the IPs.
# -JsonPath: Path to the AWS IP ranges JSON file (optional). If not provided or file doesn't exist, it will be downloaded automatically.
# -OutputPath: Optional path to save the results as a new CSV. If not provided, results are displayed in the console.

param (
    [Parameter(Mandatory=$true)]
    [string]$CsvPath,
    
    [string]$JsonPath = "ip-ranges.json",
    
    [string]$OutputPath
)

# Function to check if an IP is IPv6
function Is-IPv6 {
    param ([string]$ip)
    return $ip -match ':'
}

# Function to check if IPv4 is in CIDR
function Is-IPv4InCidr {
    param (
        [string]$ipStr,
        [string]$cidr
    )
    
    try {
        $ip = [System.Net.IPAddress]::Parse($ipStr)
        if ($ip.AddressFamily -ne [System.Net.Sockets.AddressFamily]::InterNetwork) { return $false }
        
        $parts = $cidr -split '/'
        $net = [System.Net.IPAddress]::Parse($parts[0])
        $maskLen = [int]$parts[1]
        
        # Create mask bytes
        $maskBytes = [byte[]]::new(4)
        $fullBytes = [math]::Floor($maskLen / 8)
        for ($i = 0; $i -lt $fullBytes; $i++) { $maskBytes[$i] = 255 }
        $remainder = $maskLen % 8
        if ($remainder -gt 0) { $maskBytes[$fullBytes] = [byte](255 -shl (8 - $remainder)) }
        
        # AND ip and net with mask
        $ipBytes = $ip.GetAddressBytes()
        $netBytes = $net.GetAddressBytes()
        $ipNet = [byte[]]::new(4)
        $calcNet = [byte[]]::new(4)
        for ($i = 0; $i -lt 4; $i++) {
            $ipNet[$i] = $ipBytes[$i] -band $maskBytes[$i]
            $calcNet[$i] = $netBytes[$i] -band $maskBytes[$i]
        }
        
        return [System.Linq.Enumerable]::SequenceEqual($ipNet, $calcNet)
    }
    catch {
        return $false
    }
}

# Function to check if IPv6 is in CIDR
function Is-IPv6InCidr {
    param (
        [string]$ipStr,
        [string]$cidr
    )
    
    try {
        $ip = [System.Net.IPAddress]::Parse($ipStr)
        if ($ip.AddressFamily -ne [System.Net.Sockets.AddressFamily]::InterNetworkV6) { return $false }
        
        $parts = $cidr -split '/'
        $net = [System.Net.IPAddress]::Parse($parts[0])
        $maskLen = [int]$parts[1]
        
        # Create mask bytes
        $maskBytes = [byte[]]::new(16)
        $fullBytes = [math]::Floor($maskLen / 8)
        for ($i = 0; $i -lt $fullBytes; $i++) { $maskBytes[$i] = 255 }
        $remainder = $maskLen % 8
        if ($remainder -gt 0) { $maskBytes[$fullBytes] = [byte](255 -shl (8 - $remainder)) }
        
        # AND ip and net with mask
        $ipBytes = $ip.GetAddressBytes()
        $netBytes = $net.GetAddressBytes()
        $ipNet = [byte[]]::new(16)
        $calcNet = [byte[]]::new(16)
        for ($i = 0; $i -lt 16; $i++) {
            $ipNet[$i] = $ipBytes[$i] -band $maskBytes[$i]
            $calcNet[$i] = $netBytes[$i] -band $maskBytes[$i]
        }
        
        return [System.Linq.Enumerable]::SequenceEqual($ipNet, $calcNet)
    }
    catch {
        return $false
    }
}

# Download JSON if not exists
if (-not (Test-Path $JsonPath)) {
    Write-Host "Downloading AWS IP ranges JSON..."
    Invoke-WebRequest -Uri "https://ip-ranges.amazonaws.com/ip-ranges.json" -OutFile $JsonPath
}

# Load JSON
$awsRanges = Get-Content $JsonPath | ConvertFrom-Json

# Import the CSV file
$ips = Import-Csv -Path $CsvPath

# Array to store results
$results = @()

# Loop through each IP in the CSV
foreach ($row in $ips) {
    $ip = $row.IP.Trim()  # Assuming column name is 'IPAddress'; adjust if different
    
    if (-not [string]::IsNullOrEmpty($ip)) {
        $isIPv6 = Is-IPv6 -ip $ip
        $matched = $false
        
        # Select the appropriate prefixes
        $prefixes = if ($isIPv6) { $awsRanges.ipv6_prefixes } else { $awsRanges.prefixes }
        
        foreach ($prefix in $prefixes) {
            $cidr = if ($isIPv6) { $prefix.ipv6_prefix } else { $prefix.ip_prefix }
            
            if ($cidr -and ((!$isIPv6 -and (Is-IPv4InCidr -ipStr $ip -cidr $cidr)) -or ($isIPv6 -and (Is-IPv6InCidr -ipStr $ip -cidr $cidr)))) {
                # Match found
                $result = [PSCustomObject]@{
                    IP                    = $ip
                    region                = $prefix.region
                    service               = $prefix.service
                    network_border_group  = $prefix.network_border_group
                    'non-aws-service'     = $false
                }
                $results += $result
                $matched = $true
                Write-Host "Matched IP: $ip - Region: $($prefix.region) - Service: $($prefix.service)"
                break  # Take the first match
            }
        }
        
        if (-not $matched) {
            # No match
            $result = [PSCustomObject]@{
                IP                    = $ip
                region                = "N/A"
                service               = "N/A"
                network_border_group  = "N/A"
                'non-aws-service'     = $true
            }
            $results += $result
            Write-Host "Non-AWS IP: $ip"
        }
    }
}

# If OutputPath is provided, export to CSV
if ($OutputPath) {
    $results | Export-Csv -Path $OutputPath -NoTypeInformation
    Write-Host "Results exported to $OutputPath"
}
else {
    $results | Format-Table -AutoSize
}