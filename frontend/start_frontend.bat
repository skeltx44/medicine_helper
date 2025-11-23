@echo off
echo 프론트엔드 서버 시작 중...
echo.
echo 브라우저에서 http://localhost:8080 접속하세요.
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo.
cd /d %~dp0
python -m http.server 8080

