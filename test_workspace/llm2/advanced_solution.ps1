# Test LLM2 Solution
# A different approach to safe file deletion analysis

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$ScanPath = (Get-Location).Path,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "SafeDeleteReport.txt"
)

Write-Host "Starting safe file analysis..." -ForegroundColor Green

try {
    $safeFiles = @()
    
    # Find temporary files
    $tempFiles = Get-ChildItem -Path $ScanPath -Filter "*.tmp" -Recurse -ErrorAction SilentlyContinue
    foreach ($file in $tempFiles) {
        $safeFiles += [PSCustomObject]@{
            FileName = $file.Name
            FullPath = $file.FullName
            SizeBytes = $file.Length
            SafetyScore = 90
            Reason = "Temporary file"
            DateCreated = $file.CreationTime
            DateModified = $file.LastWriteTime
        }
    }
    
    # Find log files older than 30 days
    $oldLogs = Get-ChildItem -Path $ScanPath -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | 
               Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
    
    foreach ($file in $oldLogs) {
        $safeFiles += [PSCustomObject]@{
            FileName = $file.Name
            FullPath = $file.FullName
            SizeBytes = $file.Length
            SafetyScore = 75
            Reason = "Old log file"
            DateCreated = $file.CreationTime
            DateModified = $file.LastWriteTime
        }
    }
    
    # Output results
    $safeFiles | Sort-Object SafetyScore -Descending | Format-Table -AutoSize
    $safeFiles | Export-Csv -Path $OutputFile -NoTypeInformation
    
    Write-Host "Analysis completed. Results saved to $OutputFile" -ForegroundColor Green
    Write-Host "Total files analyzed: $($safeFiles.Count)" -ForegroundColor Yellow
}
catch {
    Write-Error "Error during analysis: $($_.Exception.Message)"
}
