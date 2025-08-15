# Part of a LLM test. This one against GPT-4.1
#First prompt:
#Create for me a script that can run on windows that identifies files that are safe to delete. 
#It doesn't delete them itself, but provides a ranking of safety. In the report, include the safety-score, 
#parameters that went into the score consideration, file name, size, date created, and date updated. 
#
# SafeDeleteReport.ps1
# Scans a directory and ranks files by safety for deletion (does not delete files)
# Usage: .\SafeDeleteReport.ps1 -Path "C:\Path\To\Scan" -ReportFile "C:\Path\To\Report.csv"

param(
    [string]$Path = '.',
    [string]$ReportFile = 'SafeDeleteReport.csv'
)

function Get-SafetyScore {
    param(
        [System.IO.FileInfo]$File
    )
    $now = Get-Date
    $ageDays = ($now - $File.CreationTime).TotalDays
    $lastModDays = ($now - $File.LastWriteTime).TotalDays
    $sizeMB = [math]::Round($File.Length / 1MB, 2)
    $ext = $File.Extension.ToLower()
    $isTemp = $ext -in @('.tmp', '.temp', '.bak', '.log', '.old')
    $isSystem = $File.Attributes -band [System.IO.FileAttributes]::System
    $isReadOnly = $File.IsReadOnly

    # Scoring
    $score = 0
    $params = @()
    if ($isTemp) { $score += 40; $params += 'TempExt' }
    if ($ageDays -gt 180) { $score += 20; $params += 'OldFile' }
    elseif ($ageDays -gt 90) { $score += 10; $params += 'ModeratelyOld' }
    if ($lastModDays -gt 180) { $score += 20; $params += 'NotModifiedLong' }
    elseif ($lastModDays -gt 90) { $score += 10; $params += 'NotModifiedModerate' }
    if ($sizeMB -gt 100) { $score += 5; $params += 'LargeFile' }
    if ($isSystem) { $score -= 50; $params += 'SystemFile' }
    if ($isReadOnly) { $score -= 10; $params += 'ReadOnly' }
    if ($File.Name -match 'backup|copy|old|temp|log') { $score += 10; $params += 'NamePattern' }
    if ($score -gt 100) { $score = 100 }
    if ($score -lt 0) { $score = 0 }
    return @{ Score = $score; Params = ($params -join ',') }
}

$files = Get-ChildItem -Path $Path -File -Recurse -ErrorAction SilentlyContinue
$report = @()
foreach ($file in $files) {
    $result = Get-SafetyScore -File $file
    $report += [PSCustomObject]@{
        SafetyScore = $result.Score
        Parameters = $result.Params
        FileName = $file.FullName
        SizeMB = [math]::Round($file.Length / 1MB, 2)
        DateCreated = $file.CreationTime
        DateUpdated = $file.LastWriteTime
    }
}
$report | Sort-Object -Property SafetyScore -Descending | Export-Csv -Path $ReportFile -NoTypeInformation
Write-Host "Report generated: $ReportFile"
