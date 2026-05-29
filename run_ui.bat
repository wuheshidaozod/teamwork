@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ======================================================
echo   Mini Agent - Gradio Web UI
echo   The browser will open at http://127.0.0.1:7860
echo   Press Ctrl+C or close this window to stop.
echo ======================================================
echo.
echo (First run: if gradio is missing, run  pip install gradio)
echo.
python -X utf8 ui/gradio_app.py
pause
