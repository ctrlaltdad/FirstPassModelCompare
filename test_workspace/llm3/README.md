# File Safety Analyzer

A comprehensive PowerShell solution for identifying files that are safe to delete.

## Features

- **Multi-criteria analysis**: Considers file age, type, size, and usage patterns
- **Safety scoring**: Provides scores from 0-100 indicating deletion safety
- **Detailed reporting**: Includes file metadata and reasoning for scores
- **Flexible parameters**: Configurable age thresholds and target paths

## Usage

```powershell
# Basic usage
.\FileSafetyAnalyzer.ps1

# Analyze specific directory with custom age threshold
.\FileSafetyAnalyzer.ps1 -Path "C:\Temp" -MinDays 30

# Verbose output
.\FileSafetyAnalyzer.ps1 -Verbose
```

## Safety Criteria

- **Temporary files** (.tmp): High safety score (40 points)
- **Log files** (.log): High safety score (35 points)  
- **Backup files** (.bak): Medium safety score (25 points)
- **Cache files** (.cache): High safety score (30 points)
- **Age factor**: Files older than threshold get 30 points
- **Size factor**: Small files get bonus, large files get penalty

## Output

The script generates:
- Console display of top 10 safest files
- CSV export with complete analysis results
- Detailed reasoning for each safety score

## Safety Note

This script only analyzes and reports - it never deletes any files. All deletion decisions remain with the user.
