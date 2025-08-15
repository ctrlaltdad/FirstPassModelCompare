@echo off
echo Running LLM Analysis...
echo.
python analyze_llm_solutions.py
echo.
echo Opening Analysis Dashboard...
start analysis_dashboard.html
echo.
echo Analysis files generated:
echo - analysis_report.md (Detailed markdown report)
echo - analysis_summary.csv (CSV data for spreadsheets)
echo - analysis_dashboard.html (Interactive web dashboard)
echo.
echo Dashboard opened in your default browser!
echo.
pause
