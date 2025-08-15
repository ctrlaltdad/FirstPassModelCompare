# Safe Delete Analyzer

A Windows PowerShell script that analyzes files and provides safety rankings for potential deletion. The script doesn't delete any files but generates a comprehensive report to help you identify which files are safe to remove.

## Features

- **Safety Scoring System**: Files are scored from 0-100 based on multiple factors
- **Comprehensive Analysis**: Considers file type, age, location, size, and usage patterns
- **Detailed Reporting**: CSV output with safety scores, contributing factors, and file metadata
- **Flexible Configuration**: Customizable parameters for different analysis needs
- **System Protection**: Optional exclusion of system directories and files

## Safety Score Ranges

- **90-100: Very Safe** - Temporary files, browser cache, duplicates, old downloads
- **70-89: Safe** - Old cache files, log files, backup files
- **50-69: Moderate** - Old backups, old media files, archived documents
- **30-49: Caution** - Important documents, recent files, user data
- **0-29: Unsafe** - System files, executables, recently modified files

## Files Included

1. **Safe-Delete-Analyzer.ps1** - Main PowerShell script
2. **run-analyzer.bat** - Simple batch file wrapper for easy execution
3. **README.md** - This documentation file

## Quick Start

### Option 1: Using the Batch File (Easiest)
1. Double-click `run-analyzer.bat`
2. Follow the prompts to specify:
   - Path to analyze (or press Enter for current directory)
   - Minimum file size in KB
   - Whether to exclude system directories
3. The script will run and generate a report

### Option 2: Using PowerShell Directly

#### Basic Usage
```powershell
.\Safe-Delete-Analyzer.ps1
```

#### Analyze Specific Directory
```powershell
.\Safe-Delete-Analyzer.ps1 -Path "C:\Users\Username\Downloads"
```

#### Multiple Directories
```powershell
.\Safe-Delete-Analyzer.ps1 -Path @("C:\Temp", "C:\Users\Username\Desktop", "C:\Users\Username\Downloads")
```

#### With Custom Parameters
```powershell
.\Safe-Delete-Analyzer.ps1 -Path "C:\Users\Username" -MinSizeKB 100 -ExcludeSystem -MaxDepth 3
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `Path` | String[] | Current directory | Path(s) to analyze |
| `MinSizeKB` | Integer | 1 | Minimum file size in KB to include |
| `ExcludeSystem` | Switch | False | Exclude system directories and files |
| `OutputPath` | String | Auto-generated | Custom path for CSV report |
| `MaxDepth` | Integer | Unlimited | Maximum directory depth to scan |

## Safety Scoring Factors

The script evaluates files based on these criteria:

### File Extension Categories
- **Very High Risk**: `.exe`, `.dll`, `.sys`, `.bat`, `.cmd`, `.ps1`, `.vbs`, `.com`, `.scr`, `.msi`, `.reg`
- **High Risk**: `.docx`, `.xlsx`, `.pptx`, `.pdf`, `.txt`, `.doc`, `.xls`, `.ppt`
- **Moderate Risk**: `.jpg`, `.png`, `.mp4`, `.mp3`, `.avi`, `.mov`, `.zip`, `.rar`, `.7z`
- **Low Risk**: `.log`, `.bak`, `.old`, `.cache`, `.tmp`
- **Very Low Risk**: `.temp`, `.~tmp`, `.crdownload`, `.part`, `.partial`

### Age Analysis
- Files not modified in over a year: +15 points
- Files not modified in 6+ months: +10 points
- Files not modified in 1+ month: +5 points
- Files modified within a week: -10 points

### Location Analysis
- Temp directories (Downloads, Temp, Cache): +20 points
- System directories (Windows, Program Files): -30 points

### Special Patterns
- Backup/temp filename patterns: +15 points
- Duplicate files (numbered copies): +10 points
- Browser cache files: +25 points
- Zero-byte files: +20 points
- Large files (>100MB): +10 points

## Output Report

The CSV report includes the following columns:

- **SafetyScore**: Numerical score (0-100)
- **SafetyLevel**: Text classification (Very Safe, Safe, Moderate, Caution, Unsafe)
- **FileName**: Name of the file
- **FullPath**: Complete file path
- **SizeKB**: File size in kilobytes
- **SizeMB**: File size in megabytes
- **DateCreated**: File creation timestamp
- **DateModified**: Last modification timestamp
- **DateAccessed**: Last access timestamp
- **Extension**: File extension
- **Directory**: Parent directory path
- **SafetyFactors**: Detailed explanation of scoring factors

## Example Output

```
SafetyScore SafetyLevel FileName              SizeMB DateModified
----------- ----------- --------              ------ ------------
98          Very Safe   temp_download.tmp     15.2   2023-01-15
95          Very Safe   cache_file.cache      2.1    2023-02-20
87          Safe        old_backup.bak        156.7  2023-03-10
72          Safe        system.log            0.8    2023-06-15
45          Caution     document.docx         0.5    2024-08-01
15          Unsafe      important.exe         12.3   2024-08-10
```

## Safety Recommendations

### Very Safe Files (90-100)
- Review the list and consider deleting these files
- Usually temporary files, cache, or obvious duplicates
- Low risk of causing issues

### Safe Files (70-89)
- Good candidates for deletion
- Check if any are needed for specific purposes
- Generally old files that haven't been accessed recently

### Moderate Files (50-69)
- Review carefully before deleting
- May include old but potentially useful files
- Consider archiving instead of deleting

### Caution Files (30-49)
- Think twice before deleting
- Often contain important user data
- Consider backing up before deletion

### Unsafe Files (0-29)
- Do NOT delete without expert knowledge
- Usually system files or important executables
- Deletion could cause system instability

## System Requirements

- Windows 7 or later
- PowerShell 5.1 or later (included in Windows 10+)
- Administrator privileges may be required for some system directories

## Security Notes

- The script only reads file metadata and never modifies or deletes files
- Use `ExcludeSystem` parameter to avoid analyzing sensitive system areas
- Always review the report before taking any deletion actions
- Test with small directories first to understand the scoring system

## Troubleshooting

### "Execution Policy" Error
If you get an execution policy error, run this command in PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Access Denied" Errors
- Run PowerShell as Administrator for system directories
- Use the `-ExcludeSystem` parameter to skip protected areas
- Some files may be locked by running processes

### Large Directory Analysis
For very large directories:
- Use `-MaxDepth` parameter to limit recursion
- Increase `-MinSizeKB` to focus on larger files
- Consider analyzing subdirectories separately

## License

This script is provided as-is for educational and utility purposes. Use at your own risk and always backup important data before deletion.

## Version History

- **v1.0** - Initial release with comprehensive safety scoring system
