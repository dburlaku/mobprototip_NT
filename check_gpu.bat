@echo off
chcp 65001 >nul
echo ========================================
echo Проверка GPU для Ollama
echo ========================================
echo.

echo [1/2] Проверка NVIDIA GPU...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ NVIDIA GPU найден!
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo.
    echo ✓ Ollama будет использовать GPU автоматически!
) else (
    echo ✗ NVIDIA GPU не найден
)

echo.
echo [2/2] Проверка AMD GPU...
where rocm-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ AMD GPU найден!
    rocm-smi
) else (
    echo ✗ AMD GPU не найден
)

echo.
echo ========================================
if %errorlevel% neq 0 (
    echo Результат: GPU не обнаружен
    echo Ollama будет работать на CPU
) else (
    echo Результат: GPU обнаружен и будет использоваться
)
echo ========================================
pause
