@echo off
setlocal enabledelayedexpansion

REM Safe Delete Analyzer - Batch Version
REM This script provides a simplified version that calls the PowerShell script

echo =========================================
echo Safe Delete Analyzer - Windows Edition
echo =========================================
echo.

REM Check if PowerShell script exists
if not exist "%~dp0Safe-Delete-Analyzer.ps1" (
    echo ERROR: PowerShell script not found!
    echo Please ensure Safe-Delete-Analyzer.ps1 is in the same directory.
    pause
    exit /b 1
)

REM Get user input for path to analyze
set /p "TARGET_PATH=Enter path to analyze (or press Enter for current directory): "
if "%TARGET_PATH%"=="" set "TARGET_PATH=%CD%"

REM Get minimum file size
set /p "MIN_SIZE=Enter minimum file size in KB (or press Enter for 1KB): "
if "%MIN_SIZE%"=="" set "MIN_SIZE=1"

REM Ask about excluding system directories
set /p "EXCLUDE_SYSTEM=Exclude system directories? (y/n, default=y): "
if "%EXCLUDE_SYSTEM%"=="" set "EXCLUDE_SYSTEM=y"

echo.
echo Starting analysis...
echo Target Path: %TARGET_PATH%
echo Minimum Size: %MIN_SIZE% KB
echo Exclude System: %EXCLUDE_SYSTEM%
echo.

REM Build PowerShell command
set "PS_COMMAND=& '%~dp0Safe-Delete-Analyzer.ps1' -Path '%TARGET_PATH%' -MinSizeKB %MIN_SIZE%"

if /i "%EXCLUDE_SYSTEM%"=="y" (
    set "PS_COMMAND=!PS_COMMAND! -ExcludeSystem"
)

REM Execute PowerShell script
powershell.exe -ExecutionPolicy Bypass -Command "!PS_COMMAND!"

echo.
echo Analysis complete! Check the generated CSV report.
pause
