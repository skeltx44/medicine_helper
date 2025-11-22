@echo off
echo 백엔드 서버 재시작 중...
echo.
echo 현재 실행 중인 서버를 중지하려면 Ctrl+C를 누르세요.
echo.
pause
echo.
echo 서버 시작 중...
cd /d %~dp0
call venv\Scripts\activate
python app.py

