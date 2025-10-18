@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo 🆓 УСТАНОВКА ЛОКАЛЬНОЙ ОБРАБОТКИ ДОКУМЕНТОВ
echo ========================================
echo.
echo Эта установка позволит обрабатывать документы
echo БЕСПЛАТНО без использования Unstructured API!
echo.
echo ========================================

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo 💡 Установите Python 3.9+ с https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python найден
python --version
echo.

REM Проверка/создание виртуального окружения
if not exist "venv\" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
) else (
    echo ✅ Виртуальное окружение существует
)

echo.
echo ========================================
echo 📥 УСТАНОВКА ЗАВИСИМОСТЕЙ
echo ========================================
echo.
echo Устанавливаются пакеты для локальной обработки:
echo   • unstructured - основной пакет
echo   • PDF обработка (pypdf, pdf2image, pdfminer, pikepdf)
echo   • DOCX обработка (python-docx, python-pptx)
echo   • Изображения (Pillow)
echo   • Утилиты (langdetect, chardet)
echo.
echo Это может занять 3-5 минут...
echo.

REM Активация виртуального окружения и установка
call venv\Scripts\activate.bat

echo 📦 Обновление pip...
python -m pip install --upgrade pip --quiet

echo.
echo 📦 Установка основных зависимостей...
pip install unstructured>=0.11.0 --quiet
if errorlevel 1 (
    echo ⚠️ Ошибка установки unstructured, пробую без quiet...
    pip install unstructured>=0.11.0
)

echo 📦 Установка поддержки PDF...
pip install "unstructured[pdf]>=0.11.0" pypdf>=3.17.0 pdf2image>=1.16.0 pdfminer.six>=20221105 pikepdf>=8.0.0 --quiet
if errorlevel 1 (
    echo ⚠️ Ошибка установки PDF пакетов, пробую без quiet...
    pip install "unstructured[pdf]>=0.11.0" pypdf>=3.17.0 pdf2image>=1.16.0 pdfminer.six>=20221105 pikepdf>=8.0.0
)

echo 📦 Установка поддержки DOCX...
pip install "unstructured[docx]>=0.11.0" python-docx>=0.8.11 python-pptx>=0.6.21 --quiet
if errorlevel 1 (
    echo ⚠️ Ошибка установки DOCX пакетов, пробую без quiet...
    pip install "unstructured[docx]>=0.11.0" python-docx>=0.8.11 python-pptx>=0.6.21
)

echo 📦 Установка обработки изображений...
pip install Pillow>=10.0.0 --quiet

echo 📦 Установка утилит...
pip install langdetect>=1.0.9 chardet>=5.0.0 --quiet

echo.
echo ========================================
echo ✅ УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo 🎉 Локальная обработка документов готова!
echo.
echo 📋 Что установлено:
echo   ✅ unstructured - локальная обработка документов
echo   ✅ PDF поддержка - обработка PDF файлов
echo   ✅ DOCX поддержка - обработка Word документов
echo   ✅ Pillow - обработка изображений
echo   ✅ Утилиты для работы с текстом
echo.
echo ========================================
echo 🚀 СЛЕДУЮЩИЕ ШАГИ:
echo ========================================
echo.
echo 1. В файле .env удалите или закомментируйте UNSTRUCTURED_API_KEY
echo    (или оставьте как есть - будет автоматически использована локальная обработка)
echo.
echo 2. Выберите стратегию обработки в .env:
echo    UNSTRUCTURED_STRATEGY=fast      (быстро, ~10-30 сек на документ)
echo    UNSTRUCTURED_STRATEGY=hi_res    (качественно, ~1-3 мин на документ)
echo.
echo 3. Запустите приложение:
echo    run.bat
echo.
echo 4. В приложении нажмите "Обработать документы"
echo.
echo ========================================
echo 💡 ДОПОЛНИТЕЛЬНО:
echo ========================================
echo.
echo Для стратегии hi_res (высокое качество) может потребоваться:
echo   • Tesseract OCR для распознавания текста на изображениях
echo   • Скачать: https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo Для Windows также может потребоваться poppler:
echo   • Скачать: https://github.com/oschwartz10612/poppler-windows/releases/
echo   • Распаковать и добавить в PATH
echo.
echo Но для стратегии fast (рекомендуется) это не требуется!
echo.
echo ========================================
echo.
pause

