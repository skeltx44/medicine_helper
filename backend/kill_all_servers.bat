@echo off
echo 포트 5000에서 실행 중인 모든 프로세스를 종료합니다...
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo 프로세스 ID %%a 종료 중...
    taskkill /F /PID %%a 2>nul
    if errorlevel 1 (
        echo   프로세스 %%a를 종료할 수 없습니다 (이미 종료되었거나 권한이 없습니다)
    ) else (
        echo   프로세스 %%a 종료 완료
    )
)

echo.
echo 모든 프로세스 종료 완료!
echo.
echo 잠시 대기 중...
timeout /t 2 /nobreak >nul

echo.
echo 남아있는 프로세스 확인:
netstat -ano | findstr :5000 | findstr LISTENING
if errorlevel 1 (
    echo   포트 5000이 비어있습니다. 이제 서버를 시작할 수 있습니다.
) else (
    echo   경고: 여전히 포트 5000에서 프로세스가 실행 중입니다!
)

pause

