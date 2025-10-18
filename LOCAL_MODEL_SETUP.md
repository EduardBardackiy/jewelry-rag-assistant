# 🤖 Настройка локальной модели Llama 3

## ⚠️ Системные требования

### Минимальные:
- **RAM:** 16GB (рекомендуется 32GB)
- **Диск:** 15GB свободного места
- **Процессор:** Современный CPU (желательно с AVX2)

### Рекомендуемые:
- **GPU:** NVIDIA с 8GB+ VRAM
- **CUDA:** 11.8 или выше
- **RAM:** 32GB+

## 📦 Установка зависимостей для локальной модели

### Windows (без GPU):

```bash
# 1. Удалите старое окружение
rmdir /s /q venv

# 2. Создайте новое
python -m venv venv

# 3. Активируйте
venv\Scripts\activate

# 4. Обновите pip
python -m pip install --upgrade pip

# 5. Установите зависимости
pip install -r requirements-local.txt
```

### Linux/Windows с CUDA:

```bash
# 1. Установите PyTorch с CUDA
pip install torch --index-url https://download.pytorch.org/whl/cu118

# 2. Установите остальные зависимости
pip install -r requirements-local.txt

# 3. Установите bitsandbytes (опционально, для квантизации)
pip install bitsandbytes
```

## 🔑 Настройка .env файла

Откройте `.env` и настройте:

```env
# Выбор локальной модели
MODEL_TYPE=local

# HuggingFace Token (ОБЯЗАТЕЛЬНО!)
# Получить: https://huggingface.co/settings/tokens
HUGGINGFACE_TOKEN=hf_ваш_токен_здесь

# OpenAI можно оставить пустым (не будет использоваться)
OPENAI_API_KEY=

# Unstructured API (опционально)
UNSTRUCTURED_API_KEY=
```

## 🚀 Первый запуск

### Шаг 1: Получите HuggingFace токен

1. Зайдите на: https://huggingface.co/settings/tokens
2. Создайте новый токен (Read токена достаточно)
3. Скопируйте его в `.env` файл

### Шаг 2: Примите лицензию модели

1. Зайдите на: https://huggingface.co/IlyaGusev/saiga_llama3_8b
2. Нажмите "Agree and access repository" (если требуется)

### Шаг 3: Запустите приложение

```bash
run.bat
```

**ВНИМАНИЕ:** Первый запуск займёт **20-30 минут**, так как:
- Модель скачается (~8GB)
- Модель загрузится в память (~10-16GB RAM)

## ⚡ Оптимизация производительности

### Для Windows без GPU:

Модель будет работать на CPU. Это **медленно** (~30-60 секунд на ответ).

**Рекомендации:**
- Закройте все другие программы
- Используйте SSD (не HDD)
- Имейте терпение 😊

### Для систем с GPU:

Если у вас NVIDIA GPU с CUDA:

1. Установите CUDA Toolkit:
   - https://developer.nvidia.com/cuda-downloads

2. Установите PyTorch с CUDA:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

3. (Опционально) Установите bitsandbytes для квантизации:
   ```bash
   pip install bitsandbytes
   ```

Это ускорит работу в **10-20 раз**!

## 🔧 Решение проблем

### "Out of memory" / "Не хватает памяти"

**Причина:** Модель требует много RAM

**Решение:**
1. Закройте все программы
2. Увеличьте файл подкачки Windows
3. Используйте OpenAI API вместо локальной модели:
   ```env
   MODEL_TYPE=openai
   OPENAI_API_KEY=ваш_ключ
   ```

### "CUDA not available"

**Причина:** PyTorch не видит GPU

**Решение:**
1. Установите CUDA Toolkit
2. Переустановите PyTorch с CUDA:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

### Модель работает очень медленно

**Нормально для CPU!** Локальная модель на CPU медленная.

**Варианты:**
1. Используйте GPU (если есть)
2. Переключитесь на OpenAI API:
   ```env
   MODEL_TYPE=openai
   OPENAI_API_KEY=ваш_ключ
   ```

### "bitsandbytes not available"

**Это нормально для Windows!** Квантизация не критична.

Модель загрузится без квантизации (потребуется больше памяти, но будет работать).

## 📊 Сравнение: Локальная vs OpenAI

| Параметр | Локальная модель | OpenAI API |
|----------|------------------|------------|
| **Скорость** | Медленно (CPU) / Быстро (GPU) | Очень быстро |
| **Стоимость** | Бесплатно | ~$0.15-0.60 за 1000 запросов |
| **Требования** | 16GB+ RAM, GPU желательно | Только интернет |
| **Приватность** | 100% локально | Данные отправляются в OpenAI |
| **Качество** | Хорошее (русский язык) | Отличное |
| **Установка** | Сложная | Простая |

## 💡 Рекомендации

### Используйте локальную модель если:
- ✅ У вас мощный ПК (16GB+ RAM)
- ✅ Есть NVIDIA GPU
- ✅ Важна приватность данных
- ✅ Не хотите платить за API

### Используйте OpenAI API если:
- ✅ Нужна скорость
- ✅ Нет мощного ПК
- ✅ Хотите лучшее качество ответов
- ✅ Готовы платить небольшую сумму

## 🔄 Переключение между моделями

Просто измените в `.env`:

```env
# Для локальной модели:
MODEL_TYPE=local

# Для OpenAI:
MODEL_TYPE=openai
```

И перезапустите приложение!

## 📝 Дополнительная информация

**Используемая модель:** IlyaGusev/saiga_llama3_8b
- Основана на Llama 3 8B
- Дообучена на русском языке
- Размер: ~8GB
- Лицензия: Meta Llama 3

**Больше информации:**
- https://huggingface.co/IlyaGusev/saiga_llama3_8b
- https://github.com/IlyaGusev/saiga

---

**Успешной работы с локальной моделью! 🚀**

