"""
Приложение RAG-ассистента для ювелирного магазина
"""
# Установка UTF-8 кодировки для Windows
import sys
import os

if os.name == 'nt':  # Windows
    import io
    # Установка переменной окружения для Python
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Установка UTF-8 для stdout (только если это еще не TextIOWrapper)
    try:
        if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
            if not sys.stdout.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (ValueError, AttributeError, OSError):
        pass
    
    # Установка UTF-8 для stderr (только если это еще не TextIOWrapper)
    try:
        if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
            if not sys.stderr.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (ValueError, AttributeError, OSError):
        pass

import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import json

# Загрузка переменных окружения
load_dotenv()

# Перезагрузка переменных окружения (для обновления при смене модели)
def reload_env():
    load_dotenv(override=True)

# Импорт модулей
from utils.document_processor import DocumentProcessor
from utils.rag_chain import RAGChain

# Настройка страницы
st.set_page_config(
    page_title="Ювелирный Ассистент",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные CSS стили
st.markdown("""
<style>
    /* Компактный sidebar */
    [data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 320px;
    }
    
    /* Компактные radio кнопки */
    .stRadio > div {
        gap: 0.3rem;
    }
    
    /* Компактные кнопки */
    .stButton button {
        padding: 0.4rem 0.8rem;
        font-size: 0.9rem;
    }
    
    /* Компактные заголовки */
    .sidebar .markdown-text-container h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
        font-size: 1.1rem;
    }
    
    /* Улучшенный чат */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    /* Компактные разделители */
    hr {
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация session state
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents_processed' not in st.session_state:
    st.session_state.documents_processed = False
if 'db_type' not in st.session_state:
    st.session_state.db_type = os.getenv("DB_TYPE", "faiss")
if 'processing_strategy' not in st.session_state:
    st.session_state.processing_strategy = os.getenv("UNSTRUCTURED_STRATEGY", "fast")
if 'processing_mode' not in st.session_state:
    st.session_state.processing_mode = os.getenv("UNSTRUCTURED_MODE", "local")

def init_rag_chain():
    """Инициализация RAG цепочки"""
    try:
        reload_env()  # Перезагрузка переменных окружения
        
        model_type = os.getenv("MODEL_TYPE", "openai")
        db_type = st.session_state.db_type
        
        with st.spinner(f'🔄 Инициализация {"локальной модели" if model_type == "local" else "OpenAI модели"} с {"ChromaDB" if db_type == "chroma" else "FAISS"}...'):
            if model_type == "local":
                st.info("⏳ Первая загрузка локальной модели может занять 20-30 минут...")
                st.info("💡 Модель скачается (~8GB) и загрузится в память")
            
            rag_chain = RAGChain(db_type=db_type)
            st.session_state.rag_chain = rag_chain
            
            db_name = "ChromaDB" if db_type == "chroma" else "FAISS"
            model_name = "Локальная Llama 3" if model_type == "local" else "OpenAI GPT-4o-mini"
            st.success(f'✅ Система готова! Модель: {model_name} | БД: {db_name}')
            return True
    except Exception as e:
        st.error(f'❌ Ошибка инициализации: {str(e)}')
        
        # Подсказки по ошибкам
        error_msg = str(e).lower()
        if "openai" in error_msg or "api" in error_msg:
            st.warning("💡 Проверьте OPENAI_API_KEY в файле .env")
        elif "huggingface" in error_msg or "token" in error_msg:
            st.warning("💡 Проверьте HUGGINGFACE_TOKEN в файле .env")
        elif "memory" in error_msg or "cuda" in error_msg:
            st.warning("💡 Недостаточно памяти для локальной модели. Попробуйте OpenAI API")
        elif "не найден" in error_msg or "not found" in error_msg:
            st.warning(f"💡 Индекс {st.session_state.db_type.upper()} не найден. Нажмите 'Обработать документы'")
        
        return False

def process_documents():
    """Обработка документов из папки Data"""
    try:
        db_type = st.session_state.db_type
        with st.spinner(f'📄 Обработка документов и создание {db_type.upper()} индекса...'):
            processor = DocumentProcessor(db_type=db_type)
            result = processor.process_files()
            st.session_state.documents_processed = True
            st.success(result)
            return True
    except Exception as e:
        st.error(f'❌ Ошибка обработки документов: {str(e)}')
        return False

# Sidebar
with st.sidebar:
    st.title("💎 Настройки")
    
    # Выбор модели и БД в две колонки
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Модель")
        current_model = os.getenv("MODEL_TYPE", "openai")
        
        model_choice = st.radio(
            "Выбор:",
            options=["openai", "local"],
            format_func=lambda x: "🌐 OpenAI" if x == "openai" else "🤖 Local",
            index=0 if current_model == "openai" else 1,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("### 🗄️ БД")
        db_choice = st.radio(
            "Выбор:",
            options=["faiss", "chroma"],
            format_func=lambda x: "📊 FAISS" if x == "faiss" else "🔮 Chroma",
            index=0 if st.session_state.db_type == "faiss" else 1,
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Выбор режима и стратегии обработки документов
    st.markdown("### 📄 Обработка документов")
    
    # Проверка наличия API ключа
    unstructured_key = os.getenv("UNSTRUCTURED_API_KEY", "")
    has_api = unstructured_key and unstructured_key != "your_unstructured_api_key_here"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Режим:**")
        
        # Если нет API ключа, показываем предупреждение
        if not has_api:
            mode_help = "⚠️ API ключ не найден в .env\nМожно использовать только локальную обработку"
            mode_options = ["local"]
            mode_disabled = True
        else:
            mode_help = "API: платно, быстро, качественно\nЛокально: бесплатно, конфиденциально"
            mode_options = ["local", "api"]
            mode_disabled = False
        
        mode_choice = st.radio(
            "Режим обработки:",
            options=mode_options,
            format_func=lambda x: "🆓 Локально" if x == "local" else "☁️ API",
            index=0 if st.session_state.processing_mode == "local" else (1 if "api" in mode_options else 0),
            label_visibility="collapsed",
            help=mode_help,
            disabled=mode_disabled
        )
    
    with col2:
        st.markdown("**Стратегия:**")
        
        # Стратегия доступна только для локальной обработки
        if mode_choice == "local":
            strategy_choice = st.radio(
                "Стратегия:",
                options=["fast", "hi_res"],
                format_func=lambda x: "⚡ Быстро" if x == "fast" else "🔍 Качество",
                index=0 if st.session_state.processing_strategy == "fast" else 1,
                label_visibility="collapsed",
                help="fast: быстрая обработка (~10-30 сек)\nhi_res: высокое качество (~1-3 мин, требует доп. пакеты)"
            )
        else:
            st.info("API использует\nсвои настройки")
            strategy_choice = st.session_state.processing_strategy
    
    # Сохранение выбора режима обработки
    if mode_choice != st.session_state.processing_mode:
        st.session_state.processing_mode = mode_choice
        os.environ["UNSTRUCTURED_MODE"] = mode_choice
        
        # Обновление .env файла
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            mode_found = False
            with open(env_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith("UNSTRUCTURED_MODE="):
                        f.write(f"UNSTRUCTURED_MODE={mode_choice}\n")
                        mode_found = True
                    else:
                        f.write(line)
                
                # Если UNSTRUCTURED_MODE не было в файле, добавляем
                if not mode_found:
                    f.write(f"\nUNSTRUCTURED_MODE={mode_choice}\n")
        
        mode_name = "Локальная" if mode_choice == "local" else "API"
        st.success(f"✅ Режим изменен: {mode_name} обработка")
        st.info("👉 Пересоздайте индексы для применения нового режима")
    
    # Сохранение выбора стратегии обработки
    if strategy_choice != st.session_state.processing_strategy:
        st.session_state.processing_strategy = strategy_choice
        os.environ["UNSTRUCTURED_STRATEGY"] = strategy_choice
        
        # Обновление .env файла
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            strategy_found = False
            with open(env_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith("UNSTRUCTURED_STRATEGY="):
                        f.write(f"UNSTRUCTURED_STRATEGY={strategy_choice}\n")
                        strategy_found = True
                    else:
                        f.write(line)
                
                # Если UNSTRUCTURED_STRATEGY не было в файле, добавляем
                if not strategy_found:
                    f.write(f"\nUNSTRUCTURED_STRATEGY={strategy_choice}\n")
        
        strategy_name = "Быстрая" if strategy_choice == "fast" else "Качественная"
        st.success(f"✅ Стратегия изменена: {strategy_name}")
        st.info("👉 Пересоздайте индексы для применения новой стратегии")
    
    # Сохранение выбора БД
    if db_choice != st.session_state.db_type:
        st.session_state.db_type = db_choice
        
        # Обновление .env файла
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            db_type_found = False
            with open(env_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith("DB_TYPE="):
                        f.write(f"DB_TYPE={db_choice}\n")
                        db_type_found = True
                    else:
                        f.write(line)
                
                # Если DB_TYPE не было в файле, добавляем
                if not db_type_found:
                    f.write(f"\nDB_TYPE={db_choice}\n")
        
        # Сброс RAG цепочки при смене БД
        st.session_state.rag_chain = None
        st.success(f"✅ БД изменена на: {db_choice.upper()}")
        st.info("👉 Нажмите 'Обработать документы' если индекс ещё не создан, затем 'Инициализировать систему'")
    
    # Сохранение выбора в .env и обновление переменной окружения
    if model_choice != current_model:
        os.environ["MODEL_TYPE"] = model_choice
        
        # Обновление .env файла
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            with open(env_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.startswith("MODEL_TYPE="):
                        f.write(f"MODEL_TYPE={model_choice}\n")
                    else:
                        f.write(line)
        
        # Сброс RAG цепочки при смене модели
        st.session_state.rag_chain = None
        st.success(f"✅ Модель изменена на: {model_choice}")
        st.info("👉 Нажмите 'Инициализировать систему' для применения изменений")
    
    # Компактный статус API ключей
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if model_choice == "openai":
            openai_key = os.getenv("OPENAI_API_KEY", "")
            if openai_key and openai_key != "your_openai_api_key_here":
                st.markdown("✅ **API ключ**")
            else:
                st.markdown("❌ **API ключ**")
        else:
            hf_token = os.getenv("HUGGINGFACE_TOKEN", "")
            if hf_token and hf_token != "your_huggingface_token_here":
                st.markdown("✅ **HF токен**")
            else:
                st.markdown("❌ **HF токен**")
    
    with col2:
        if st.session_state.rag_chain:
            st.markdown("✅ **Готова**")
        else:
            st.markdown("⚠️ **Не готова**")
    
    st.markdown("---")
    
    # Кнопки управления в две колонки
    st.markdown("### 🔧 Управление")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Обработать", use_container_width=True):
            process_documents()
        
        if st.button("🚀 Запустить", use_container_width=True):
            init_rag_chain()
    
    with col2:
        if st.button("🗑️ Очистить", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        # Пустая кнопка для симметрии или добавьте свою функцию
        if st.button("ℹ️ Справка", use_container_width=True):
            st.info("📚 Смотрите раздел 'Инструкция' ниже")
    
    st.markdown("---")
    
    # Компактная информация о системе
    st.markdown("### ℹ️ Статус")
    
    # Информация в две колонки
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Модель:")
        st.markdown(f"**{model_choice.upper()}**")
        
        st.caption("БД:")
        st.markdown(f"**{st.session_state.db_type.upper()}**")
        
        st.caption("Режим:")
        mode_icon = "🆓" if st.session_state.processing_mode == "local" else "☁️"
        mode_text = "LOCAL" if st.session_state.processing_mode == "local" else "API"
        st.markdown(f"**{mode_icon} {mode_text}**")
        
        if st.session_state.processing_mode == "local":
            st.caption("Стратегия:")
            strategy_icon = "⚡" if st.session_state.processing_strategy == "fast" else "🔍"
            strategy_text = "FAST" if st.session_state.processing_strategy == "fast" else "HI-RES"
            st.markdown(f"**{strategy_icon} {strategy_text}**")
    
    with col2:
        data_dir = Path(os.getenv("DATA_DIR", "./Data"))
        if data_dir.exists():
            files = list(data_dir.glob("*.*"))
            st.caption("Файлов:")
            st.markdown(f"**{len(files)}**")
        
        st.caption("API ключ:")
        if has_api:
            st.markdown("**✅ Есть**")
        else:
            st.markdown("**❌ Нет**")
        
        st.caption("Статус:")
        if st.session_state.rag_chain:
            st.markdown("**✅ Готова**")
        else:
            st.markdown("**⚠️ Ждёт**")
    
    # Статус БД компактно
    st.caption("Индексы:")
    faiss_path = Path(os.getenv("FAISS_INDEX_PATH", "./faiss_index"))
    chroma_path = Path(os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("📊 FAISS: " + ("✅" if faiss_path.exists() else "❌"))
    with col2:
        st.markdown("🔮 Chroma: " + ("✅" if chroma_path.exists() else "❌"))
    
    st.markdown("---")
    
    # Компактная инструкция
    with st.expander("📖 Инструкция"):
        st.markdown("""
        **Быстрый старт:**
        1. Выберите модель и БД
        2. Нажмите "Обработать"
        3. Нажмите "Запустить"
        4. Общайтесь!
        
        **Режимы:**
        - ⚡ Быстрый: OpenAI + FAISS
        - 🔒 Приватный: Local + Chroma
        - 📈 Масштаб: OpenAI + Chroma
        """)

# Основная область
st.title("💎 Ювелирный Ассистент")

# Компактная информационная панель
info_col1, info_col2, info_col3, info_col4 = st.columns(4)

with info_col1:
    st.metric(
        "Модель", 
        model_choice.upper(),
        delta="OpenAI" if model_choice == "openai" else "Local"
    )

with info_col2:
    st.metric(
        "База данных",
        st.session_state.db_type.upper(),
        delta="FAISS" if st.session_state.db_type == "faiss" else "ChromaDB"
    )

with info_col3:
    data_dir = Path(os.getenv("DATA_DIR", "./Data"))
    file_count = len(list(data_dir.glob("*.*"))) if data_dir.exists() else 0
    st.metric("Документов", file_count)

with info_col4:
    status = "Готова" if st.session_state.rag_chain else "Ожидание"
    st.metric("Статус", status)

st.markdown("---")

# Проверка инициализации
if st.session_state.rag_chain is None:
    st.info("👈 Пожалуйста, инициализируйте систему в боковой панели")
    st.stop()

# Отображение истории чата
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Поле ввода
user_input = st.chat_input("Задайте вопрос о ювелирных изделиях...")

if user_input:
    # Добавление сообщения пользователя
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Получение ответа
    with st.chat_message("assistant"):
        with st.spinner("🤔 Думаю..."):
            try:
                response = st.session_state.rag_chain.get_response(user_input)
                st.markdown(response)
                
                # Добавление ответа в историю
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Футер
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Ювелирный Ассистент v1.0 | Создано с использованием RAG и LangChain</small>
</div>
""", unsafe_allow_html=True)

