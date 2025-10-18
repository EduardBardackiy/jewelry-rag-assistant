# 📤 Загрузка проекта на GitHub

## 🎯 Пошаговая инструкция

### Шаг 1: Создайте репозиторий на GitHub

1. Перейдите на https://github.com/new
2. Заполните информацию:
   - **Repository name**: `jewelry-rag-assistant` (или свое название)
   - **Description**: `RAG-powered assistant for jewelry store with local document processing`
   - **Public** или **Private** (на ваш выбор)
   - ❌ **НЕ** создавайте README, .gitignore, license (они уже есть)
3. Нажмите **"Create repository"**

---

### Шаг 2: Инициализируйте Git локально

Откройте PowerShell в папке проекта и выполните:

```bash
# Инициализация репозитория
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Jewelry RAG Assistant v1.1"
```

---

### Шаг 3: Свяжите с GitHub

Замените `YOUR_USERNAME` и `YOUR_REPO` на свои:

```bash
# Добавление удаленного репозитория
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Переименование ветки в main (если нужно)
git branch -M main

# Загрузка на GitHub
git push -u origin main
```

**Пример:**
```bash
git remote add origin https://github.com/ivanov/jewelry-rag-assistant.git
git branch -M main
git push -u origin main
```

---

### Шаг 4: Введите учетные данные

При первой загрузке Git попросит авторизоваться:

**Вариант 1: Personal Access Token (рекомендуется)**
1. Перейдите: https://github.com/settings/tokens
2. **Generate new token (classic)**
3. Выберите scopes: `repo`
4. Скопируйте токен
5. При запросе пароля вставьте токен

**Вариант 2: GitHub Desktop**
- Скачайте: https://desktop.github.com/
- Авторизуйтесь через интерфейс

---

### Шаг 5: Проверьте загрузку

1. Обновите страницу репозитория на GitHub
2. Убедитесь, что все файлы загружены
3. Проверьте, что README отображается корректно

---

## ✅ Что было загружено

### Основные файлы:
- ✅ `app.py` - главное приложение
- ✅ `requirements.txt` - зависимости
- ✅ `README.md` - документация
- ✅ `.gitignore` - исключения

### Документация:
- ✅ `QUICKSTART.md` - быстрый старт
- ✅ `INSTALL_GUIDE.md` - установка
- ✅ `CHANGELOG_v1.1.md` - история изменений
- ✅ `ЛОКАЛЬНАЯ_ОБРАБОТКА_ДОКУМЕНТОВ.md` - локальная обработка
- ✅ `УСТАНОВКА_POPPLER_WINDOWS.md` - установка Poppler

### Утилиты:
- ✅ `utils/` - вспомогательные модули
- ✅ Установочные скрипты (.bat, .ps1)
- ✅ `run.bat` - запуск приложения

---

## ❌ Что НЕ было загружено (по .gitignore)

### Автоматически исключены:
- ❌ `venv/` - виртуальное окружение
- ❌ `.env` - ваши приватные ключи
- ❌ `chroma_db/` - база данных
- ❌ `faiss_index/` - индексы
- ❌ `output/` - временные файлы
- ❌ `__pycache__/` - Python кэш
- ❌ `catalog.json` - сгенерированный файл

**Это правильно!** Эти файлы генерируются локально и не должны быть в Git.

---

## 🔄 Последующие обновления

После внесения изменений в код:

```bash
# Проверить изменения
git status

# Добавить все измененные файлы
git add .

# Создать коммит с описанием
git commit -m "Описание ваших изменений"

# Загрузить на GitHub
git push
```

**Примеры хороших коммитов:**
- `git commit -m "Fix: исправлена ошибка обработки PDF"`
- `git commit -m "Feature: добавлена поддержка Excel файлов"`
- `git commit -m "Docs: обновлена документация по установке"`

---

## 📝 Рекомендации

### 1. Создайте хорошее описание репозитория

На странице репозитория нажмите "Edit" и добавьте:

**Topics (теги):**
- `rag`
- `langchain`
- `streamlit`
- `openai`
- `faiss`
- `chromadb`
- `python`
- `nlp`
- `document-processing`

**Website:** (если есть демо)

### 2. Добавьте бейджи в README

Вы можете добавить бейджи в начало README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
```

### 3. Создайте Releases

После стабильной версии:
1. Перейдите в раздел "Releases"
2. **"Create a new release"**
3. Tag: `v1.1.0`
4. Title: `Jewelry RAG Assistant v1.1.0`
5. Опишите изменения
6. **"Publish release"**

### 4. Добавьте GitHub Actions (опционально)

Создайте `.github/workflows/test.yml` для автоматического тестирования:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements-simple.txt
      - name: Run tests
        run: |
          python -m pytest tests/
```

---

## 🔒 Безопасность

### ⚠️ ВАЖНО: Проверьте, что не загружены секреты!

Перед загрузкой убедитесь:

```bash
# Проверьте .env не добавлен
git status

# Если случайно добавили .env
git rm --cached .env
git commit -m "Remove .env from git"
```

### Если секреты уже загружены:

1. **Немедленно смените все ключи API!**
2. Используйте `git filter-branch` или BFG Repo-Cleaner
3. Force push с новой историей

**Лучше предотвратить!** Всегда проверяйте `git status` перед `git add .`

---

## 🎯 Пример полного процесса

```bash
# 1. Перейдите в папку проекта
cd C:\FAISS_ChromaDB

# 2. Инициализация
git init
git add .
git commit -m "Initial commit: Jewelry RAG Assistant v1.1"

# 3. Связь с GitHub
git remote add origin https://github.com/YOUR_USERNAME/jewelry-rag-assistant.git
git branch -M main

# 4. Загрузка
git push -u origin main

# При запросе введите токен GitHub
```

---

## 🐛 Решение проблем

### Проблема: "failed to push some refs"

**Решение:**
```bash
git pull origin main --rebase
git push origin main
```

### Проблема: "src refspec main does not match any"

**Решение:**
```bash
# Убедитесь что есть коммиты
git log

# Если нет, сделайте коммит
git commit -m "Initial commit"
```

### Проблема: Большой размер репозитория

**Решение:**
```bash
# Проверьте что в .gitignore есть venv/ и другие большие папки
# Удалите из индекса
git rm -r --cached venv/
git commit -m "Remove venv from git"
git push
```

### Проблема: "Permission denied"

**Решение:**
- Используйте Personal Access Token вместо пароля
- Или настройте SSH ключи

---

## 📚 Полезные ссылки

- **GitHub Docs:** https://docs.github.com/en/get-started
- **Git Tutorial:** https://git-scm.com/docs/gittutorial
- **GitHub Desktop:** https://desktop.github.com/
- **Personal Access Tokens:** https://github.com/settings/tokens

---

## 🎊 Готово!

После загрузки ваш проект будет доступен на GitHub! 

**Поделитесь ссылкой:**
```
https://github.com/YOUR_USERNAME/jewelry-rag-assistant
```

**Приглашайте contributors:**
- Создайте `CONTRIBUTING.md`
- Добавьте Issues для задач
- Настройте Pull Requests

---

**Удачи с вашим проектом на GitHub! 🚀**

