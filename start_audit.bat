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
echo [2/3] Checking model qwen2.5...
ollama list | findstr qwen2.5 >nul 2>&1
if %errorlevel% neq 0 (
    echo Model qwen2.5 not found. Downloading...
    echo This may take 5-10 minutes (5GB download)
    ollama pull qwen2.5:latest
) else (
    echo Model qwen2.5 found.
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
