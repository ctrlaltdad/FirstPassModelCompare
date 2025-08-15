#Requires -Version 5.1
<#
.SYNOPSIS
    Analyzes files and provides safety rankings for potential deletion.

.DESCRIPTION
    This script scans specified directories and analyzes files to determine how safe they are to delete.
    It generates a comprehensive report with safety scores, contributing factors, and file metadata.

.PARAMETER Path
    The path(s) to analyze. Defaults to current directory.

.PARAMETER MinSizeKB
    Minimum file size in KB to include in analysis. Defaults to 1KB.

.PARAMETER ExcludeSystem
    Exclude system directories and files from analysis.

.PARAMETER OutputPath
    Path for the output CSV report. Defaults to current directory.

.PARAMETER MaxDepth
    Maximum directory depth to scan. Defaults to unlimited.

.EXAMPLE
    .\Safe-Delete-Analyzer.ps1 -Path "C:\Users\Username\Downloads" -ExcludeSystem
    
.EXAMPLE
    .\Safe-Delete-Analyzer.ps1 -Path @("C:\Temp", "C:\Users\Username\Desktop") -MinSizeKB 100

.NOTES
    Author: GitHub Copilot
    Version: 1.0
    Safety Score Ranges:
    - 90-100: Very Safe (temp files, duplicates, old downloads)
    - 70-89:  Safe (old cache files, old logs)
    - 50-69:  Moderate (old backups, old media)
    - 30-49:  Caution (documents, important files)
    - 0-29:   Unsafe (system files, executables, recent files)
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromPipeline = $true)]
    [string[]]$Path = @((Get-Location).Path),
    
    [int]$MinSizeKB = 1,
    
    [switch]$ExcludeSystem,
    
    [string]$OutputPath = (Join-Path (Get-Location).Path "SafeDeleteReport_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"),
    
    [int]$MaxDepth = -1
)

# Define file safety categories and weights
$SafetyRules = @{
    # File extension categories (base scores)
    'VeryHighRisk' = @{
        'Extensions' = @('.exe', '.dll', '.sys', '.bat', '.cmd', '.ps1', '.vbs', '.com', '.scr', '.msi', '.reg')
        'BaseScore' = 5
    }
    'HighRisk' = @{
        'Extensions' = @('.docx', '.xlsx', '.pptx', '.pdf', '.txt', '.doc', '.xls', '.ppt')
        'BaseScore' = 25
    }
    'ModerateRisk' = @{
        'Extensions' = @('.jpg', '.png', '.mp4', '.mp3', '.avi', '.mov', '.zip', '.rar', '.7z')
        'BaseScore' = 50
    }
    'LowRisk' = @{
        'Extensions' = @('.log', '.bak', '.old', '.cache', '.tmp')
        'BaseScore' = 75
    }
    'VeryLowRisk' = @{
        'Extensions' = @('.temp', '.~tmp', '.crdownload', '.part', '.partial')
        'BaseScore' = 95
    }
}

# System directories to exclude
$SystemDirectories = @(
    'Windows', 'Program Files', 'Program Files (x86)', 'ProgramData',
    'System Volume Information', '$Recycle.Bin', 'Recovery'
)

# Temp directories (higher safety scores)
$TempDirectories = @(
    'Temp', 'Temporary Internet Files', 'Downloads', 'Recent', 'Prefetch'
)

function Get-FileSafetyScore {
    param(
        [System.IO.FileInfo]$File
    )
    
    $score = 50  # Base score
    $factors = @()
    
    # File extension analysis
    $extension = $File.Extension.ToLower()
    $categoryFound = $false
    
    foreach ($category in $SafetyRules.Keys) {
        if ($SafetyRules[$category].Extensions -contains $extension) {
            $score = $SafetyRules[$category].BaseScore
            $factors += "Extension category: $category"
            $categoryFound = $true
            break
        }
    }
    
    if (-not $categoryFound) {
        $factors += "Extension: Unknown category"
    }
    
    # Age analysis
    $daysSinceCreated = (Get-Date) - $File.CreationTime
    $daysSinceModified = (Get-Date) - $File.LastWriteTime
    $daysSinceAccessed = (Get-Date) - $File.LastAccessTime
    
    # Older files are generally safer to delete
    if ($daysSinceModified.Days -gt 365) {
        $score += 15
        $factors += "Very old file (>1 year since modified)"
    } elseif ($daysSinceModified.Days -gt 180) {
        $score += 10
        $factors += "Old file (>6 months since modified)"
    } elseif ($daysSinceModified.Days -gt 30) {
        $score += 5
        $factors += "Moderately old file (>1 month since modified)"
    } elseif ($daysSinceModified.Days -le 7) {
        $score -= 10
        $factors += "Recently modified (within 1 week)"
    }
    
    # Access time analysis
    if ($daysSinceAccessed.Days -gt 180) {
        $score += 10
        $factors += "Not accessed recently (>6 months)"
    } elseif ($daysSinceAccessed.Days -le 7) {
        $score -= 5
        $factors += "Recently accessed"
    }
    
    # Size analysis
    $sizeKB = $File.Length / 1KB
    if ($sizeKB -gt 100000) {  # > 100MB
        $score += 10
        $factors += "Large file (>100MB)"
    } elseif ($sizeKB -lt 1) {  # < 1KB
        $score += 5
        $factors += "Very small file (<1KB)"
    }
    
    # Directory location analysis
    $parentDir = $File.Directory.Name
    
    # Check if in temp directories
    foreach ($tempDir in $TempDirectories) {
        if ($File.FullName -like "*\$tempDir\*") {
            $score += 20
            $factors += "Located in temp directory: $tempDir"
            break
        }
    }
    
    # Check if in system directories (reduce score)
    foreach ($sysDir in $SystemDirectories) {
        if ($File.FullName -like "*\$sysDir\*") {
            $score -= 30
            $factors += "Located in system directory: $sysDir"
            break
        }
    }
    
    # Special filename patterns
    if ($File.Name -match '(?i)^(copy|backup|old|temp|~)') {
        $score += 15
        $factors += "Filename suggests temporary/backup file"
    }
    
    if ($File.Name -match '(?i)\(\d+\)\.') {
        $score += 10
        $factors += "Appears to be duplicate file (numbered copy)"
    }
    
    # Browser cache and temp files
    if ($File.FullName -match '(?i)(cache|cookies|history|temporary)') {
        $score += 25
        $factors += "Browser cache or temporary file"
    }
    
    # Zero-byte files
    if ($File.Length -eq 0) {
        $score += 20
        $factors += "Zero-byte file"
    }
    
    # Ensure score stays within bounds
    $score = [Math]::Max(0, [Math]::Min(100, $score))
    
    return @{
        'Score' = $score
        'Factors' = $factors -join '; '
        'SafetyLevel' = switch ($score) {
            { $_ -ge 90 } { 'Very Safe' }
            { $_ -ge 70 } { 'Safe' }
            { $_ -ge 50 } { 'Moderate' }
            { $_ -ge 30 } { 'Caution' }
            default { 'Unsafe' }
        }
    }
}

function Get-DirectoryFiles {
    param(
        [string]$DirectoryPath,
        [int]$CurrentDepth = 0
    )
    
    if ($MaxDepth -ge 0 -and $CurrentDepth -gt $MaxDepth) {
        return
    }
    
    try {
        $items = Get-ChildItem -Path $DirectoryPath -Force -ErrorAction SilentlyContinue
        
        foreach ($item in $items) {
            if ($item.PSIsContainer) {
                # Skip system directories if requested
                if ($ExcludeSystem) {
                    $skipDir = $false
                    foreach ($sysDir in $SystemDirectories) {
                        if ($item.Name -eq $sysDir -or $item.FullName -like "*\$sysDir" -or $item.FullName -like "*\$sysDir\*") {
                            $skipDir = $true
                            break
                        }
                    }
                    if ($skipDir) { continue }
                }
                
                # Recursively process subdirectory
                Get-DirectoryFiles -DirectoryPath $item.FullName -CurrentDepth ($CurrentDepth + 1)
            } else {
                # Filter by minimum size
                if (($item.Length / 1KB) -ge $MinSizeKB) {
                    $item
                }
            }
        }
    } catch {
        Write-Warning "Cannot access directory: $DirectoryPath - $($_.Exception.Message)"
    }
}

# Main execution
Write-Host "Safe Delete Analyzer - Starting analysis..." -ForegroundColor Green
Write-Host "Parameters:"
Write-Host "  Paths: $($Path -join ', ')"
Write-Host "  Minimum Size: $MinSizeKB KB"
Write-Host "  Exclude System: $ExcludeSystem"
Write-Host "  Max Depth: $(if ($MaxDepth -ge 0) { $MaxDepth } else { 'Unlimited' })"
Write-Host "  Output: $OutputPath"
Write-Host ""

$results = @()
$totalFiles = 0
$totalSize = 0

foreach ($scanPath in $Path) {
    if (-not (Test-Path $scanPath)) {
        Write-Warning "Path not found: $scanPath"
        continue
    }
    
    Write-Host "Scanning: $scanPath" -ForegroundColor Cyan
    
    if (Test-Path $scanPath -PathType Leaf) {
        # Single file
        $files = @(Get-Item $scanPath)
    } else {
        # Directory
        $files = Get-DirectoryFiles -DirectoryPath $scanPath
    }
    
    foreach ($file in $files) {
        $totalFiles++
        $totalSize += $file.Length
        
        if ($totalFiles % 100 -eq 0) {
            Write-Progress -Activity "Analyzing Files" -Status "Processed $totalFiles files" -PercentComplete -1
        }
        
        try {
            $safety = Get-FileSafetyScore -File $file
            
            $result = [PSCustomObject]@{
                'SafetyScore' = $safety.Score
                'SafetyLevel' = $safety.SafetyLevel
                'FileName' = $file.Name
                'FullPath' = $file.FullName
                'SizeKB' = [Math]::Round($file.Length / 1KB, 2)
                'SizeMB' = [Math]::Round($file.Length / 1MB, 2)
                'DateCreated' = $file.CreationTime
                'DateModified' = $file.LastWriteTime
                'DateAccessed' = $file.LastAccessTime
                'Extension' = $file.Extension
                'Directory' = $file.DirectoryName
                'SafetyFactors' = $safety.Factors
            }
            
            $results += $result
        } catch {
            Write-Warning "Error analyzing file $($file.FullName): $($_.Exception.Message)"
        }
    }
}

Write-Progress -Activity "Analyzing Files" -Completed

# Sort results by safety score (highest first)
$results = $results | Sort-Object SafetyScore -Descending

# Export to CSV
$results | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8

# Display summary
Write-Host ""
Write-Host "Analysis Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host "Total Files Analyzed: $totalFiles"
Write-Host "Total Size: $([Math]::Round($totalSize / 1MB, 2)) MB"
Write-Host "Report saved to: $OutputPath"
Write-Host ""

# Safety level breakdown
$breakdown = $results | Group-Object SafetyLevel | Sort-Object Name
Write-Host "Safety Level Breakdown:" -ForegroundColor Yellow
foreach ($group in $breakdown) {
    $totalSizeMB = ($group.Group | Measure-Object SizeMB -Sum).Sum
    Write-Host "  $($group.Name): $($group.Count) files ($([Math]::Round($totalSizeMB, 2)) MB)"
}

Write-Host ""
Write-Host "Top 10 Safest Files to Delete:" -ForegroundColor Yellow
$results | Select-Object -First 10 | Format-Table SafetyScore, SafetyLevel, FileName, SizeMB, DateModified -AutoSize

Write-Host ""
Write-Host "Files with Safety Score >= 90 (Very Safe):" -ForegroundColor Green
$verySafe = $results | Where-Object { $_.SafetyScore -ge 90 }
if ($verySafe) {
    $verySafeSizeMB = ($verySafe | Measure-Object SizeMB -Sum).Sum
    Write-Host "Count: $($verySafe.Count) files"
    Write-Host "Total Size: $([Math]::Round($verySafeSizeMB, 2)) MB"
} else {
    Write-Host "No files found with Very Safe rating."
}

Write-Host ""
Write-Host "Review the full report at: $OutputPath" -ForegroundColor Cyan
