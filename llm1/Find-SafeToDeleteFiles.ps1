<#
.SYNOPSIS
    Analyzes files in a specified directory and ranks them by how safe they might be to delete.

.DESCRIPTION
    This script recursively scans a directory to identify files that could be candidates for deletion.
    It calculates a "Safety Score" based on criteria such as file age (LastWriteTime), file type (e.g., .log, .tmp),
    and location (e.g., Temp folders).

    The script does NOT delete any files. It produces a report that includes:
    - SafetyScore: A calculated score. Higher is "safer".
    - ScoreParameters: The reasons contributing to the score.
    - Name: The file's name.
    - FullName: The file's full path.
    - Size(KB): The file's size in kilobytes.
    - CreationTime: The date the file was created.
    - LastWriteTime: The date the file was last modified.

.PARAMETER Path
    The directory path to scan for files. Defaults to the user's home directory ('~').

.PARAMETER Top
    The number of files to include in the final report, ranked by safety score. Defaults to 50.

.EXAMPLE
    PS C:\> .\Find-SafeToDeleteFiles.ps1 -Path "C:\Users\YourUser\Downloads" -Top 20

    This command scans the "Downloads" folder and lists the top 20 files considered safest to delete.

.EXAMPLE
    PS C:\> .\Find-SafeToDeleteFiles.ps1 | Export-Csv -Path "C:\Reports\SafeToDelete.csv" -NoTypeInformation

    This command scans the user's home directory and exports the full report to a CSV file.
#>
[CmdletBinding()]
param (
    [Parameter(Mandatory = $false, ValueFromPipeline = $true, Position = 0)]
    [string]$Path = "~",

    [Parameter(Mandatory = $false)]
    [int]$Top = 50
)

# Resolve the path to an absolute path
$targetPath = Resolve-Path -Path $Path

Write-Host "Starting analysis of files in: $targetPath" -ForegroundColor Green
Write-Host "This script only identifies files and does not perform any delete operations." -ForegroundColor Yellow

# Define criteria for the safety score
$tempExtensions = @('.tmp', '.log', '.bak', '.old', '.dmp', '._mp', '.chk', '.gid', '.syd')
$tempLocations = @(
    [System.IO.Path]::GetFullPath($env:TEMP),
    [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($env:windir, "Temp"))
)

try {
    # Get all files recursively, ignoring errors for paths that are too long or inaccessible
    $files = Get-ChildItem -Path $targetPath -Recurse -File -ErrorAction SilentlyContinue

    $report = foreach ($file in $files) {
        $safetyScore = 0
        $scoreParameters = [System.Collections.Generic.List[string]]@()

        # 1. Score based on LastWriteTime (Age)
        $ageInDays = (Get-Date) - $file.LastWriteTime | Select-Object -ExpandProperty Days
        if ($ageInDays -gt 365) {
            $safetyScore += 50
            $scoreParameters.Add("Over 1 year old")
        }
        elseif ($ageInDays -gt 180) {
            $safetyScore += 25
            $scoreParameters.Add("Over 6 months old")
        }
        elseif ($ageInDays -gt 30) {
            $safetyScore += 10
            $scoreParameters.Add("Over 1 month old")
        }

        # 2. Score based on file extension
        if ($tempExtensions -contains $file.Extension) {
            $safetyScore += 30
            $scoreParameters.Add("Temp Extension ($($file.Extension))")
        }

        # 3. Score based on file location
        foreach ($loc in $tempLocations) {
            if ($file.FullName.StartsWith($loc, [System.StringComparison]::OrdinalIgnoreCase)) {
                $safetyScore += 40
                $scoreParameters.Add("In Temp Location")
                break # Stop after first match
            }
        }
        
        # 4. Score based on file attributes (e.g., temporary)
        if ($file.Attributes -band [System.IO.FileAttributes]::Temporary) {
            $safetyScore += 20
            $scoreParameters.Add("Temporary Attribute")
        }

        # Create a custom object for the report
        [PSCustomObject]@{
            SafetyScore     = $safetyScore
            ScoreParameters = $scoreParameters -join ', '
            Name            = $file.Name
            "Size(KB)"      = [math]::Round($file.Length / 1KB, 2)
            CreationTime    = $file.CreationTime
            LastWriteTime   = $file.LastWriteTime
            FullName        = $file.FullName
        }
    }

    # Sort the report by safety score (descending) and select the top results
    $sortedReport = $report | Sort-Object -Property SafetyScore -Descending | Select-Object -First $Top

    Write-Host "`nAnalysis Complete. Top $Top files ranked by deletion safety score:`n" -ForegroundColor Green
    
    # Display the report in a formatted table
    $sortedReport | Format-Table -AutoSize

    Write-Host "`nTo export the full report to a CSV file, you can pipe the script's output to Export-Csv." -ForegroundColor Cyan
    Write-Host "Example: .\Find-SafeToDeleteFiles.ps1 -Path '$targetPath' | Export-Csv -Path '.\FileReport.csv' -NoTypeInformation" -ForegroundColor Cyan

}
catch {
    Write-Error "An error occurred: $_"
}
