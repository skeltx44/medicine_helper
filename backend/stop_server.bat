@echo off
echo 포트 5000에서 실행 중인 프로세스를 종료합니다...
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo 프로세스 ID %%a 종료 중...
    taskkill /F /PID %%a
)

echo.
echo 완료! 이제 서버를 다시 시작할 수 있습니다.
pause

