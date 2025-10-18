@echo off
chcp 65001 >nul

REM Переход в директорию скрипта
cd /d "%~dp0"

REM Установка переменной окружения для UTF-8
set PYTHONIOENCODING=utf-8

echo ========================================
echo 💎 Запуск Ювелирного Ассистента
echo ========================================
echo.

REM Проверка виртуального окружения
if not exist "venv\" (
    echo ⚠️  Виртуальное окружение не найдено!
    echo.
    echo Запустите сначала install.bat или install-simple.bat
    echo.
    pause
    exit /b 1
)

REM Активация виртуального окружения
echo 🔄 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Проверка зависимостей
echo 🔄 Проверка зависимостей...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit не установлен!
    echo.
    echo Запустите install.bat или install-simple.bat
    echo.
    pause
    exit /b 1
)
echo ✅ Зависимости установлены
echo.

REM Настройка .env
if not exist ".env" (
    echo ⚠️  Файл .env не найден!
    echo 📝 Создание .env из примера...
    copy env_example.txt .env >nul
    echo ✅ Файл .env создан
    echo.
    echo ⚠️  ВАЖНО: Откройте .env и укажите ваш OPENAI_API_KEY!
    echo.
    echo Нажмите любую клавишу, чтобы открыть .env в блокноте...
    pause >nul
    notepad .env
    echo.
    echo После настройки ключа запустите этот файл снова!
    echo.
    pause
    exit /b 0
)

REM Запуск приложения
echo ========================================
echo 🚀 Запуск приложения...
echo ========================================
echo.
echo 🌐 Приложение откроется в браузере
echo 💡 Для остановки нажмите Ctrl+C
echo.

timeout /t 2 >nul

streamlit run app.py

pause

