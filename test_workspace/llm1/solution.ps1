# Test LLM1 Solution
# Creates a simple file analysis script

param(
    [string]$Path = "."
)

function Get-SafeToDeleteFiles {
    param([string]$TargetPath)
    
    Get-ChildItem -Path $TargetPath -File -Recurse | Where-Object {
        $_.Extension -eq ".tmp" -or $_.Extension -eq ".log"
    } | ForEach-Object {
        [PSCustomObject]@{
            Name = $_.Name
            Path = $_.FullName
            Size = $_.Length
            SafetyScore = 85
            LastWriteTime = $_.LastWriteTime
            CreationTime = $_.CreationTime
        }
    }
}

# Main execution
$results = Get-SafeToDeleteFiles -TargetPath $Path
$results | Export-Csv -Path "SafeFiles.csv" -NoTypeInformation
Write-Host "Analysis complete. Found $($results.Count) potentially safe files."
