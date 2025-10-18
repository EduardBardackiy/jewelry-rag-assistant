# ========================================
# 🤖 Установка локальной модели (PowerShell)
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 Установка локальной модели Llama 3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
Write-Host "🔍 Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python не найден!" -ForegroundColor Red
    Write-Host "Установите Python 3.9+ с https://www.python.org" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# Удаление старого окружения
if (Test-Path "venv") {
    Write-Host "🗑️  Удаление старого окружения..." -ForegroundColor Yellow
    Remove-Item -Path venv -Recurse -Force
    Write-Host "✅ Старое окружение удалено" -ForegroundColor Green
}

Write-Host ""

# Создание виртуального окружения
Write-Host "🔧 Создание виртуального окружения..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Виртуальное окружение создано" -ForegroundColor Green
} else {
    Write-Host "❌ Ошибка создания окружения" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# Активация окружения
Write-Host "🔄 Активация окружения..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Обновление pip
Write-Host ""
Write-Host "📦 Обновление pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Установка зависимостей
Write-Host ""
Write-Host "📦 Установка зависимостей для локальной модели..." -ForegroundColor Yellow
Write-Host "⚠️  Это займёт несколько минут!" -ForegroundColor Yellow
Write-Host ""

pip install -r requirements-local.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ Установка завершена успешно!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Ошибка установки зависимостей" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# Создание .env файла
if (-not (Test-Path ".env")) {
    Write-Host "📝 Создание файла .env..." -ForegroundColor Yellow
    Copy-Item env_example.txt .env
    Write-Host "✅ Файл .env создан" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 СЛЕДУЮЩИЕ ШАГИ:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Получите HuggingFace токен:" -ForegroundColor White
Write-Host "   https://huggingface.co/settings/tokens" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Примите лицензию модели:" -ForegroundColor White
Write-Host "   https://huggingface.co/IlyaGusev/saiga_llama3_8b" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Откройте .env в блокноте:" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Укажите в .env:" -ForegroundColor White
Write-Host "   MODEL_TYPE=local" -ForegroundColor Gray
Write-Host "   HUGGINGFACE_TOKEN=hf_ваш_токен" -ForegroundColor Gray
Write-Host ""
Write-Host "5️⃣  Запустите приложение:" -ForegroundColor White
Write-Host "   run.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  ВАЖНО: Первый запуск займёт 20-30 минут!" -ForegroundColor Yellow
Write-Host "   Модель скачается (~8GB) и загрузится в память" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Подробнее: LOCAL_MODEL_SETUP.md" -ForegroundColor Cyan
Write-Host ""

pause

