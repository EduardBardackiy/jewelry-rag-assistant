@echo off
chcp 65001 >nul
cls

REM Переход в директорию скрипта
cd /d "%~dp0"

echo ========================================
echo 💎 Установка Ювелирного Ассистента
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Установите Python 3.9+ с https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Удаление старого окружения
if exist "venv\" (
    echo 🗑️  Удаление старого окружения...
    rmdir /s /q venv
    echo ✅ Удалено
    echo.
)

REM Создание виртуального окружения
echo 🔧 Создание виртуального окружения...
python -m venv venv
if errorlevel 1 (
    echo ❌ Ошибка создания окружения
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение создано
echo.

REM Активация виртуального окружения
echo 🔄 Активация окружения...
call venv\Scripts\activate.bat
echo.

REM Обновление pip
echo 📦 Обновление pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip обновлён
echo.

REM Меню выбора
:menu
cls
echo ========================================
echo 💎 Выберите режим установки
echo ========================================
echo.
echo 1. Упрощённая (только OpenAI API)
echo    - Быстро и просто
echo    - Требует OpenAI ключ
echo.
echo 2. Локальная модель (Llama 3)
echo    - Бесплатно
echo    - Требует 16GB+ RAM
echo.
echo 3. Обе модели (полная версия)
echo    - Можно переключаться
echo    - Долгая установка
echo.
set /p choice="Ваш выбор (1, 2 или 3): "

if "%choice%"=="1" goto install_simple
if "%choice%"=="2" goto install_local
if "%choice%"=="3" goto install_full
echo.
echo ❌ Неверный выбор!
timeout /t 2 >nul
goto menu

:install_simple
echo.
echo ========================================
echo 📦 Установка упрощённой версии...
echo ========================================
echo.
pip install -r requirements-simple.txt
if errorlevel 1 goto install_error
echo.
echo ✅ Установка завершена!
echo.
echo 📝 Настройте .env:
echo    OPENAI_API_KEY=ваш_ключ
echo    MODEL_TYPE=openai
goto finish

:install_local
echo.
echo ========================================
echo 📦 Установка локальной модели...
echo ========================================
echo ⏳ Это займёт несколько минут...
echo.
pip install -r requirements-local.txt
if errorlevel 1 goto install_error
echo.
echo ✅ Установка завершена!
echo.
echo 📝 Настройте .env:
echo    HUGGINGFACE_TOKEN=hf_ваш_токен
echo    MODEL_TYPE=local
echo.
echo 📚 Читайте: LOCAL_MODEL_SETUP.md
goto finish

:install_full
echo.
echo ========================================
echo 📦 Установка полной версии...
echo ========================================
echo ⏳ Это займёт 5-10 минут...
echo.
echo Шаг 1/2: Установка базовых пакетов...
pip install -r requirements-simple.txt
if errorlevel 1 goto install_error
echo ✅ Базовые пакеты установлены
echo.
echo Шаг 2/2: Установка пакетов для локальной модели...
pip install transformers>=4.35.0 accelerate>=0.25.0 torch>=2.1.0
if errorlevel 1 (
    echo ⚠️  Не удалось установить пакеты для локальной модели
    echo Будет доступен только OpenAI режим
) else (
    echo ✅ Пакеты для локальной модели установлены
)
echo.
echo ✅ Полная установка завершена!
echo.
echo 📝 Настройте .env (оба ключа):
echo    OPENAI_API_KEY=ваш_ключ
echo    HUGGINGFACE_TOKEN=hf_ваш_токен
echo    MODEL_TYPE=openai
goto finish

:install_error
echo.
echo ========================================
echo ❌ ОШИБКА УСТАНОВКИ!
echo ========================================
echo.
echo Возможные причины:
echo - Нет интернета
echo - Конфликт версий
echo - Недостаточно прав
echo.
echo Попробуйте:
echo 1. Проверьте интернет
echo 2. Запустите от администратора
echo 3. Выберите вариант 1 (упрощённая)
echo.
pause
exit /b 1

:finish
echo.
REM Создание .env если его нет
if not exist ".env" (
    echo 📝 Создание файла .env...
    copy env_example.txt .env >nul
    echo ✅ Файл .env создан
    echo.
)

echo ========================================
echo ✅ УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Следующие шаги:
echo.
echo 1. Откройте файл .env в блокноте:
echo    notepad .env
echo.
echo 2. Укажите ваши API ключи
echo.
echo 3. Запустите приложение:
echo    run.bat
echo.
echo 📚 Документация: README.md
echo.
pause

