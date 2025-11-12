@echo off
chcp 65001 >nul
echo ========================================
echo Starting Audit Processor...
echo ========================================
echo.

REM Check if Ollama is running
echo [1/3] Checking Ollama status...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama is not running. Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
    echo Ollama started.
) else (
    echo Ollama is already running.
)

echo.
echo [2/3] Checking model llama3.2...
ollama list | findstr llama3.2 >nul 2>&1
if %errorlevel% neq 0 (
    echo Model llama3.2 not found. Downloading...
    echo This may take 3-5 minutes (~2GB download)
    echo Please wait...
    ollama pull llama3.2:latest
    if %errorlevel% neq 0 (
        echo.
        echo WARNING: Failed to download model llama3.2
        echo You can try alternative models:
        echo   - ollama pull qwen2.5:latest
        echo   - ollama pull mistral:latest
        echo.
        echo The application will start in DEMO mode without AI analysis.
        timeout /t 5 /nobreak
    ) else (
        echo Model llama3.2 downloaded successfully!
    )
) else (
    echo Model llama3.2 found.
)

echo.
echo [3/3] Starting application...
python audit_processor.py

if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to start application
    echo Please check that Python is installed and audit_processor.py exists
    pause
) else (
    echo.
    echo Application closed successfully.
)
