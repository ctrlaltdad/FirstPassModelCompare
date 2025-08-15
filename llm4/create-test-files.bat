@echo off
echo Creating test files for Safe Delete Analyzer demo...

REM Create test directory structure
mkdir test_files 2>nul
cd test_files

mkdir temp 2>nul
mkdir downloads 2>nul
mkdir documents 2>nul
mkdir cache 2>nul

REM Create various test files with different characteristics

REM Very safe files (temp, cache, old)
echo This is a temporary file > temp\temp_file.tmp
echo Cache data > cache\browser.cache
echo Old backup > backup_2023.bak
echo Download part > downloads\video.part

REM Safe files (logs, old files)
echo Log entry > system.log
echo Old data > old_data.old

REM Moderate files (media, archives)
echo Image data > photo.jpg
echo Video data > movie.mp4
echo Archive > backup.zip

REM Caution files (documents)
echo Important document > documents\report.docx
echo Spreadsheet data > documents\budget.xlsx

REM Unsafe files (executables, system)
echo Executable > program.exe
echo System file > system.dll

REM Create files with different timestamps using PowerShell
powershell.exe -Command "Get-ChildItem *.bak | ForEach-Object { $_.CreationTime = (Get-Date).AddDays(-400); $_.LastWriteTime = (Get-Date).AddDays(-400) }"
powershell.exe -Command "Get-ChildItem *.log | ForEach-Object { $_.LastWriteTime = (Get-Date).AddDays(-100) }"

echo.
echo Test files created in 'test_files' directory!
echo You can now run the analyzer on this directory:
echo.
echo   .\Safe-Delete-Analyzer.ps1 -Path "%CD%"
echo.
echo Or use the batch file and specify this path when prompted:
echo   %CD%
echo.
pause
