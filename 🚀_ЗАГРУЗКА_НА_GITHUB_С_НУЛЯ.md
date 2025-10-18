# 🚀 Загрузка проекта на GitHub с нуля

## ✅ Вы удалили старый репозиторий - отлично!

Эта инструкция для **чистой загрузки нового проекта**.

---

## 📋 Пошаговая инструкция

### Шаг 1: Создайте новый репозиторий на GitHub

1. Откройте: **https://github.com/new**
2. Заполните:
   - **Repository name**: `jewelry-rag-assistant` (или своё название)
   - **Description**: `RAG-powered assistant for jewelry store with local document processing`
   - **Public** или **Private** (на ваш выбор)
   - ❌ **НЕ** ставьте галочки:
     - [ ] Add a README file
     - [ ] Add .gitignore
     - [ ] Choose a license
3. Нажмите **"Create repository"**

GitHub покажет инструкции - **НЕ ЗАКРЫВАЙТЕ эту страницу!**

---

### Шаг 2: Откройте PowerShell в папке проекта

```powershell
# Перейдите в папку проекта
cd C:\FAISS_ChromaDB
```

Или просто откройте PowerShell прямо в папке проекта.

---

### Шаг 3: Инициализируйте Git

```bash
# Инициализация нового Git репозитория
git init

# Проверьте что .env НЕ в списке (должен быть в .gitignore)
git status
```

**⚠️ КРИТИЧНО:** Проверьте вывод `git status`

**НЕ должно быть:**
- ❌ `.env` (ваши секреты!)
- ❌ `venv/` (виртуальное окружение)
- ❌ `chroma_db/` (база данных)
- ❌ `faiss_index/` (индексы)

Если видите `.env` - **СТОП!** Проверьте `.gitignore` перед продолжением.

---

### Шаг 4: Добавьте файлы

```bash
# Добавить все файлы
git add .

# Проверить что добавилось
git status
```

Вы должны увидеть список файлов в зелёном цвете (staged).

---

### Шаг 5: Создайте первый коммит

```bash
git commit -m "Initial commit: Jewelry RAG Assistant v1.1"
```

---

### Шаг 6: Свяжите с GitHub

**На странице GitHub (которую вы НЕ закрывали) скопируйте URL вашего репозитория.**

Он выглядит так: `https://github.com/YOUR_USERNAME/YOUR_REPO.git`

Выполните:

```bash
# Замените на ВАШУ ссылку!
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Переименуйте ветку в main
git branch -M main
```

**Пример:**
```bash
git remote add origin https://github.com/ivanov/jewelry-rag-assistant.git
git branch -M main
```

---

### Шаг 7: Загрузите на GitHub

```bash
git push -u origin main
```

**Система попросит авторизоваться!**

---

### Шаг 8: Авторизация

#### Вариант 1: Personal Access Token (рекомендуется)

1. Откройте: **https://github.com/settings/tokens**
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Настройки:
   - **Note**: `Jewelry RAG Assistant`
   - **Expiration**: `90 days` (или больше)
   - **Select scopes**: ✅ `repo` (поставьте галочку)
4. Нажмите **"Generate token"**
5. **СКОПИРУЙТЕ токен** (он больше не покажется!)
6. В PowerShell:
   - **Username**: ваш GitHub username
   - **Password**: вставьте токен (НЕ пароль!)

#### Вариант 2: GitHub Desktop (проще для новичков)

1. Скачайте: https://desktop.github.com/
2. Авторизуйтесь
3. File → Add local repository → выберите `C:\FAISS_ChromaDB`
4. Publish repository

---

## ✅ Готово!

После выполнения `git push` перейдите на GitHub и обновите страницу.

Вы должны увидеть все файлы проекта! 🎉

---

## 📝 Полная последовательность команд

```bash
# 1. Перейти в папку проекта
cd C:\FAISS_ChromaDB

# 2. Инициализация
git init

# 3. Проверка (убедитесь что .env НЕ в списке!)
git status

# 4. Добавление файлов
git add .

# 5. Первый коммит
git commit -m "Initial commit: Jewelry RAG Assistant v1.1"

# 6. Связь с GitHub (ВСТАВЬТЕ СВОЮ ССЫЛКУ!)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 7. Переименование ветки
git branch -M main

# 8. Загрузка
git push -u origin main

# При запросе введите username и токен
```

---

## 🔧 Проверка перед загрузкой

### Чеклист:

- [ ] Создан репозиторий на GitHub
- [ ] `git status` НЕ показывает `.env`
- [ ] `git status` НЕ показывает `venv/`
- [ ] `.gitignore` существует
- [ ] `.env.example` создан (без реальных ключей)
- [ ] Personal Access Token готов
- [ ] Скопирована ссылка на репозиторий

---

## ⚠️ Важные предупреждения

### 🔴 Если `git status` показывает `.env`:

```bash
# НЕ ДЕЛАЙТЕ git add!
# Проверьте .gitignore
cat .gitignore | Select-String ".env"

# Если .env случайно добавлен:
git rm --cached .env
git add .gitignore
git commit -m "Fix: ensure .env is ignored"
```

### 🔴 Если загрузили `.env` по ошибке:

1. **НЕМЕДЛЕННО смените все API ключи!**
2. Удалите `.env` из репозитория:
   ```bash
   git rm .env
   git commit -m "Remove .env with secrets"
   git push
   ```
3. Очистите историю (если нужно)

---

## 🐛 Решение проблем

### Проблема: "Permission denied (publickey)"

**Решение:** Используйте HTTPS вместо SSH или настройте SSH ключи.

Для HTTPS ссылка должна быть:
```
https://github.com/USERNAME/REPO.git
```

Не `git@github.com:...`

### Проблема: "Authentication failed"

**Решение:** 
1. Убедитесь что используете **токен**, а не пароль
2. Проверьте что токен имеет scope `repo`
3. Создайте новый токен

### Проблема: "src refspec main does not match any"

**Решение:** Сделайте хотя бы один коммит перед push:
```bash
git commit -m "Initial commit"
```

### Проблема: "fatal: remote origin already exists"

**Решение:** Удалите старый remote:
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Проблема: Репозиторий слишком большой

**Решение:** Проверьте что `venv/` в `.gitignore`:
```bash
# Если venv уже добавлен:
git rm -r --cached venv/
git commit -m "Remove venv from repository"
```

---

## 🎯 После успешной загрузки

### 1. Проверьте на GitHub:

- [ ] Все файлы загружены
- [ ] `.env` НЕ виден (должен быть скрыт!)
- [ ] README отображается правильно
- [ ] Документация на месте

### 2. Настройте репозиторий:

1. **About** (справа сверху):
   - Добавьте описание
   - Добавьте website (если есть)
   - Добавьте топики: `rag`, `langchain`, `streamlit`, `openai`, `python`, `nlp`

2. **Settings** → **General**:
   - Features: ✅ Issues, ✅ Projects
   - Pull Requests: настройте по желанию

3. **Releases**:
   - Create a new release
   - Tag: `v1.1.0`
   - Title: `Jewelry RAG Assistant v1.1.0`
   - Описание: скопируйте из `CHANGELOG_v1.1.md`
   - Publish release

### 3. Поделитесь:

```
🎉 Я опубликовал свой RAG-проект на GitHub!

Ювелирный Ассистент с локальной обработкой документов
- 🆓 Бесплатная обработка PDF/DOCX
- 🤖 Поддержка OpenAI и локальной Llama 3
- 📊 FAISS и ChromaDB
- 🎨 Streamlit интерфейс

https://github.com/YOUR_USERNAME/jewelry-rag-assistant

#Python #RAG #LangChain #OpenAI #OpenSource
```

---

## 📚 Полезные ссылки

- **GitHub Desktop:** https://desktop.github.com/
- **Personal Access Tokens:** https://github.com/settings/tokens
- **Git Documentation:** https://git-scm.com/doc
- **GitHub Docs:** https://docs.github.com/

---

## 🔄 Последующие обновления

После загрузки, для обновления кода:

```bash
# Проверить изменения
git status

# Добавить изменённые файлы
git add .

# Коммит с описанием
git commit -m "Описание ваших изменений"

# Загрузить на GitHub
git push
```

**Примеры хороших коммитов:**
- `git commit -m "Fix: исправлена ошибка обработки PDF"`
- `git commit -m "Feature: добавлена поддержка Excel файлов"`
- `git commit -m "Docs: обновлён README"`
- `git commit -m "Refactor: улучшена обработка ошибок"`

---

## 🎊 Готово!

Следуйте этой инструкции шаг за шагом, и ваш проект будет успешно загружен на GitHub!

**Начните прямо сейчас! ⬇️**

```bash
cd C:\FAISS_ChromaDB
git init
```

**Удачи! 🚀💎**

