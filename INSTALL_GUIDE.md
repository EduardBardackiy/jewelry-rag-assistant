# 🔧 Руководство по устранению ошибок установки

## ❌ Проблема: Конфликт зависимостей

Если вы видите ошибку:
```
ERROR: Cannot install ... because these package versions have conflicting dependencies
```

### ✅ Решение 1: Используйте упрощённую установку (РЕКОМЕНДУЕТСЯ)

```bash
# 1. Удалите старое виртуальное окружение
rmdir /s /q venv

# 2. Запустите install.bat и выберите вариант 1
install.bat
```

### ✅ Решение 2: Ручная установка

```bash
# 1. Создайте виртуальное окружение
python -m venv venv

# 2. Активируйте его
venv\Scripts\activate

# 3. Обновите pip
python -m pip install --upgrade pip

# 4. Установите упрощённую версию
pip install -r requirements-simple.txt
```

### ✅ Решение 3: Установка по одному пакету

Если и это не помогает, установите пакеты по одному:

```bash
venv\Scripts\activate
pip install --upgrade pip

pip install streamlit
pip install python-dotenv
pip install langchain
pip install langchain-community
pip install langchain-core
pip install openai
pip install sentence-transformers
pip install faiss-cpu
pip install "unstructured[pdf]"
pip install unstructured-ingest
```

## 🔍 После успешной установки

1. Создайте файл `.env`:
   ```bash
   copy env_example.txt .env
   ```

2. Откройте `.env` и добавьте ключи:
   ```env
   OPENAI_API_KEY=ваш_ключ_здесь
   UNSTRUCTURED_API_KEY=ваш_ключ_здесь
   MODEL_TYPE=openai
   ```

3. Запустите приложение:
   ```bash
   run.bat
   ```

## 💡 Важные замечания

### Упрощённая vs Полная версия

**Упрощённая версия (requirements-simple.txt):**
- ✅ Быстрая установка
- ✅ Меньше конфликтов
- ✅ Работает через OpenAI API
- ❌ Нет локальной модели

**Полная версия (requirements.txt):**
- ✅ Поддержка локальной модели Llama
- ❌ Долгая установка
- ❌ Требует много RAM (16GB+)
- ❌ Возможны конфликты на Windows

### Рекомендация для Windows

Используйте **упрощённую версию** с OpenAI API. Локальная модель:
- Требует мощное железо
- Сложнее в настройке на Windows
- Может не работать без CUDA

## 🐛 Другие частые ошибки

### "streamlit is not recognized"

**Причина:** Зависимости не установились из-за конфликта

**Решение:** Используйте `install.bat` с вариантом 1

### "No module named 'dotenv'"

**Причина:** Не установлен python-dotenv

**Решение:**
```bash
venv\Scripts\activate
pip install python-dotenv
```

### "CUDA not available" (для локальной модели)

**Причина:** Нет GPU или драйверов CUDA

**Решение:** Используйте OpenAI API:
```env
MODEL_TYPE=openai
```

## 📞 Нужна помощь?

1. Проверьте, что используете Python 3.9+:
   ```bash
   python --version
   ```

2. Обновите pip:
   ```bash
   python -m pip install --upgrade pip
   ```

3. Используйте упрощённую версию для начала

4. Убедитесь, что файл `.env` создан и заполнен

