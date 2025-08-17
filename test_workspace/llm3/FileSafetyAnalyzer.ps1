# Test LLM3 Solution
# A comprehensive approach with documentation

<#
.SYNOPSIS
    Identifies files that are safe to delete based on multiple criteria.

.DESCRIPTION
    This script analyzes files in a specified directory and provides safety scores
    for potential deletion. It considers file age, type, size, and usage patterns.

.PARAMETER Path
    The path to analyze. Defaults to current directory.

.PARAMETER MinDays
    Minimum age in days for files to be considered for deletion.

.EXAMPLE
    .\FileSafetyAnalyzer.ps1 -Path "C:\Temp" -MinDays 30
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$Path = $PWD,
    
    [Parameter()]
    [int]$MinDays = 7
)

function Analyze-FilesSafety {
    [CmdletBinding()]
    param(
        [string]$TargetPath,
        [int]$MinimumDays
    )
    
    begin {
        Write-Verbose "Starting file safety analysis..."
        $safetyThreshold = (Get-Date).AddDays(-$MinimumDays)
        $results = @()
    }
    
    process {
        try {
            $files = Get-ChildItem -Path $TargetPath -File -Recurse -ErrorAction Stop
            
            foreach ($file in $files) {
                $safetyScore = 0
                $reasons = @()
                
                # Age-based scoring
                if ($file.LastWriteTime -lt $safetyThreshold) {
                    $safetyScore += 30
                    $reasons += "Old file (>{0} days)" -f $MinimumDays
                }
                
                # Extension-based scoring
                switch ($file.Extension.ToLower()) {
                    '.tmp' { $safetyScore += 40; $reasons += "Temporary file" }
                    '.log' { $safetyScore += 35; $reasons += "Log file" }
                    '.bak' { $safetyScore += 25; $reasons += "Backup file" }
                    '.cache' { $safetyScore += 30; $reasons += "Cache file" }
                    default { $safetyScore += 0 }
                }
                
                # Size-based scoring (large files might be important)
                if ($file.Length -lt 1KB) {
                    $safetyScore += 10
                    $reasons += "Small file"
                } elseif ($file.Length -gt 100MB) {
                    $safetyScore -= 15
                    $reasons += "Large file (caution)"
                }
                
                # Create result object
                if ($safetyScore -gt 20) {  # Only include files with some safety score
                    $results += [PSCustomObject]@{
                        Name = $file.Name
                        Path = $file.FullName
                        Size = $file.Length
                        SizeFormatted = Format-FileSize -Bytes $file.Length
                        SafetyScore = [Math]::Min($safetyScore, 100)
                        Reasons = ($reasons -join "; ")
                        DateCreated = $file.CreationTime
                        DateModified = $file.LastWriteTime
                        LastAccessed = $file.LastAccessTime
                    }
                }
            }
        }
        catch {
            Write-Error "Error analyzing path: $($_.Exception.Message)"
        }
    }
    
    end {
        return ($results | Sort-Object SafetyScore -Descending)
    }
}

function Format-FileSize {
    param([long]$Bytes)
    
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    elseif ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    elseif ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    else { return "{0} bytes" -f $Bytes }
}

# Main execution
Write-Host "File Safety Analyzer v1.0" -ForegroundColor Cyan
Write-Host "Analyzing: $Path" -ForegroundColor Yellow

$analysisResults = Analyze-FilesSafety -TargetPath $Path -MinimumDays $MinDays

if ($analysisResults.Count -gt 0) {
    Write-Host "`nFound $($analysisResults.Count) files for potential deletion:" -ForegroundColor Green
    
    # Display top 10 safest files
    $analysisResults | Select-Object -First 10 | Format-Table Name, SafetyScore, SizeFormatted, DateModified -AutoSize
    
    # Export all results
    $csvPath = Join-Path $Path "SafetyAnalysis.csv"
    $analysisResults | Export-Csv -Path $csvPath -NoTypeInformation
    Write-Host "Complete results exported to: $csvPath" -ForegroundColor Green
} else {
    Write-Host "No files meet the safety criteria for deletion." -ForegroundColor Yellow
}
