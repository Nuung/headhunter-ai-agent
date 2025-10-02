@echo off
echo ========================================
echo 헤드헌터 AI 챗봇 시작
echo ========================================
echo.

REM 가상환경 활성화 (존재하는 경우)
if exist venv\Scripts\activate.bat (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

echo 챗봇 실행 중...
echo.

python run_chatbot.py

pause
