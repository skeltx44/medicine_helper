@echo off
echo PID 14584 프로세스 종료 시도...
taskkill /F /PID 14584
if %errorlevel% == 0 (
    echo 프로세스 종료 성공!
) else (
    echo 프로세스 종료 실패 또는 이미 종료됨
)
timeout /t 2 /nobreak >nul
netstat -ano | findstr :5000 | findstr LISTENING
pause

