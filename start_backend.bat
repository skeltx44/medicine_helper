@echo off
echo 백엔드 서버 시작 중...
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo.
cd /d %~dp0\backend
call venv\Scripts\activate
python app.py

