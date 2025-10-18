"""
Модуль для обработки документов
"""
import os
import sys
from pathlib import Path

# Установка UTF-8 для Windows в самом начале
if os.name == 'nt':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from dotenv import load_dotenv
from unstructured.staging.base import elements_from_json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata
import chromadb

# Загрузка переменных окружения
load_dotenv()

# Безопасная функция для вывода с UTF-8
def safe_print(message):
    """Безопасный вывод с поддержкой UTF-8"""
    try:
        # Пытаемся вывести как есть
        print(message)
    except (UnicodeEncodeError, UnicodeError):
        try:
            # Если не получается, пытаемся вывести без непечатаемых символов
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            if safe_message.strip():  # Проверяем, что что-то осталось
                print(safe_message)
        except Exception:
            # В крайнем случае просто выводим в stderr как текст
            try:
                import sys
                sys.stderr.write(f"{message}\n")
            except:
                pass
    except Exception:
        # Любая другая ошибка - просто игнорируем
        pass


class DocumentProcessor:
    """Класс для обработки документов и создания векторной БД"""
    
    def __init__(self, db_type="faiss"):
        self.data_dir = Path(os.getenv("DATA_DIR", "./Data"))
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.db_type = db_type.lower()
        
        # Пути к БД
        self.faiss_path = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
        self.chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        
        # Инициализация эмбеддингов с обработкой ошибок
        self.embeddings = self._init_embeddings()
        
        # Создание директорий если их нет
        self.output_dir.mkdir(exist_ok=True)
    
    def _init_embeddings(self):
        """Инициализация эмбеддингов с обработкой ошибок"""
        import time
        
        model_name = "BAAI/bge-base-en-v1.5"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                safe_print(f"Загрузка модели эмбеддингов... (попытка {attempt + 1}/{max_retries})")
                
                # Настройки для обхода SSL проблем
                import ssl
                import urllib.request
                
                # Создание SSL контекста с менее строгой проверкой
                ssl._create_default_https_context = ssl._create_unverified_context
                
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                
                safe_print("OK: Модель эмбеддингов загружена")
                return embeddings
                
            except Exception as e:
                safe_print(f"WARN: Попытка {attempt + 1} не удалась: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    safe_print(f"Повтор через {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    safe_print("ERROR: Не удалось загрузить модель эмбеддингов")
                    safe_print("INFO: Проверьте интернет-соединение")
                    raise Exception(
                        "Не удалось загрузить модель эмбеддингов. "
                        "Проверьте подключение к интернету и попробуйте снова."
                    )
    
    def decode_text(self, text):
        """Декодирование текста"""
        try:
            if isinstance(text, bytes):
                return text.decode('utf-8')
            return text
        except (UnicodeDecodeError, AttributeError):
            return text
    
    def load_processed_files(self):
        """Загрузка обработанных файлов из JSON"""
        elements = []
        for filename in self.output_dir.glob("*.json"):
            try:
                file_elements = elements_from_json(filename=str(filename))
                for element in file_elements:
                    if hasattr(element, "text") and element.text is not None:
                        element.text = self.decode_text(element.text)
                elements.extend(file_elements)
            except IOError as e:
                print(f"Ошибка чтения файла {filename}: {e}")
        return elements
    
    def process_files(self):
        """Обработка файлов и создание FAISS индекса"""
        import requests
        from unstructured.partition.auto import partition
        
        # Проверка режима обработки
        processing_mode = os.getenv("UNSTRUCTURED_MODE", "local")
        
        # Проверка наличия API ключа
        api_key = os.getenv("UNSTRUCTURED_API_KEY")
        has_api_key = api_key and api_key != "your_unstructured_api_key_here"
        
        # Определение, использовать ли API
        if processing_mode == "api":
            if has_api_key:
                use_api = True
                safe_print("📡 Режим: API обработка (платно)")
            else:
                safe_print("⚠️ Режим API выбран, но ключ не найден. Использую локальную обработку.")
                use_api = False
        else:
            use_api = False
            safe_print("🆓 Режим: Локальная обработка (бесплатно)")
        
        # Создание директории для вывода
        self.output_dir.mkdir(exist_ok=True)
        
        # Обработка каждого файла
        all_elements = []
        
        for file_path in self.data_dir.glob("*.*"):
            if file_path.suffix.lower() in ['.pdf', '.docx', '.doc', '.txt']:
                safe_print(f"📄 Обработка файла: {file_path.name}")
                
                try:
                    if use_api:
                        # Использование Unstructured API
                        elements = self._process_with_api(file_path, api_key)
                    else:
                        # Локальная обработка
                        elements = self._process_locally(file_path)
                    
                    all_elements.extend(elements)
                    safe_print(f"✅ Обработано элементов: {len(elements)}")
                    
                except Exception as e:
                    safe_print(f"⚠️ Ошибка обработки {file_path.name}: {e}")
                    continue
        
        if not all_elements:
            raise ValueError("Не удалось обработать ни одного документа")
        
        # Преобразование в LangChain документы
        documents = []
        for element in all_elements:
            # Проверка наличия текста
            text = getattr(element, 'text', None) or str(element)
            if text and text.strip():
                metadata = {}
                if hasattr(element, 'metadata'):
                    try:
                        metadata = element.metadata.to_dict() if hasattr(element.metadata, 'to_dict') else {}
                    except:
                        metadata = {}
                
                documents.append(Document(page_content=text, metadata=metadata))
        
        safe_print(f"\n📊 Всего документов для индексации: {len(documents)}")
        
        # Создание векторной БД в зависимости от выбора
        if self.db_type == "chroma":
            safe_print("📦 Создание ChromaDB индекса...")
            
            # Фильтрация сложных метаданных для ChromaDB
            safe_print("🔧 Фильтрация метаданных...")
            filtered_documents = filter_complex_metadata(documents)
            
            # Дополнительная очистка метаданных
            clean_documents = []
            for doc in filtered_documents:
                clean_metadata = {}
                for key, value in doc.metadata.items():
                    # ChromaDB принимает только str, int, float, bool, None
                    if isinstance(value, (str, int, float, bool, type(None))):
                        clean_metadata[key] = value
                    elif isinstance(value, list):
                        # Преобразуем списки в строки
                        clean_metadata[key] = ", ".join(str(v) for v in value)
                    elif isinstance(value, dict):
                        # Преобразуем словари в строки
                        clean_metadata[key] = str(value)
                    else:
                        # Остальное преобразуем в строку
                        clean_metadata[key] = str(value)
                
                clean_documents.append(
                    Document(page_content=doc.page_content, metadata=clean_metadata)
                )
            
            db = Chroma.from_documents(
                documents=clean_documents,
                embedding=self.embeddings,
                persist_directory=self.chroma_path
            )
            safe_print(f"✅ ChromaDB индекс создан в {self.chroma_path}")
            return f"✅ Обработано {len(clean_documents)} документов и создан ChromaDB индекс"
        else:  # faiss
            safe_print("📦 Создание FAISS индекса...")
            db = FAISS.from_documents(documents, self.embeddings)
            db.save_local(self.faiss_path)
            safe_print(f"✅ FAISS индекс создан в {self.faiss_path}")
            return f"✅ Обработано {len(documents)} документов и создан FAISS индекс"
    
    def _process_with_api(self, file_path, api_key):
        """Обработка файла через Unstructured API"""
        import requests
        
        url = os.getenv("UNSTRUCTURED_URL", "https://api.unstructuredapp.io/general/v0/general")
        
        with open(file_path, 'rb') as f:
            files = {'files': (file_path.name, f)}
            headers = {'unstructured-api-key': api_key}
            data = {'strategy': 'hi_res', 'languages': 'rus'}
            
            response = requests.post(url, files=files, headers=headers, data=data)
            response.raise_for_status()
            
            # Парсинг ответа
            from unstructured.staging.base import elements_from_json
            import tempfile
            import json
            
            # Сохранение во временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
                json.dump(response.json(), tmp, ensure_ascii=False)
                tmp_path = tmp.name
            
            try:
                elements = elements_from_json(filename=tmp_path)
                return elements
            finally:
                Path(tmp_path).unlink(missing_ok=True)
    
    def _process_locally(self, file_path):
        """Локальная обработка файла без API"""
        from unstructured.partition.auto import partition
        import os
        
        # Установка UTF-8 для Windows через переменную окружения
        if os.name == 'nt':  # Windows
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Получение стратегии обработки из переменных окружения
        strategy = os.getenv("UNSTRUCTURED_STRATEGY", "fast")
        
        safe_print(f"  └─ Использование локальной обработки (стратегия: {strategy})")
        
        # Параметры обработки в зависимости от типа файла
        partition_kwargs = {
            "filename": str(file_path),
            "strategy": strategy,
        }
        
        # Дополнительные параметры для PDF
        if file_path.suffix.lower() == '.pdf':
            partition_kwargs.update({
                "languages": ["rus", "eng"],  # Поддержка русского и английского
                "include_page_breaks": True,
            })
            
            # Если hi_res, добавляем параметры для лучшего качества
            if strategy == "hi_res":
                partition_kwargs["infer_table_structure"] = True
        
        # Дополнительные параметры для DOCX
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            partition_kwargs["languages"] = ["rus", "eng"]
        
        try:
            # Обработка файла локально
            elements = partition(**partition_kwargs)
            
            # Проверка и декодирование текста
            for element in elements:
                if hasattr(element, 'text') and element.text:
                    element.text = self.decode_text(element.text)
            
            return elements
            
        except ImportError as e:
            # Подсказка если не хватает зависимостей
            if "detectron2" in str(e) or "hi_res" in str(e):
                safe_print(f"  ⚠️ Для стратегии 'hi_res' нужны дополнительные зависимости")
                safe_print(f"  💡 Переключаюсь на стратегию 'fast'...")
                partition_kwargs["strategy"] = "fast"
                if "infer_table_structure" in partition_kwargs:
                    del partition_kwargs["infer_table_structure"]
                elements = partition(**partition_kwargs)
                return elements
            else:
                raise
        except Exception as e:
            error_msg = str(e)
            safe_print(f"  ❌ Ошибка локальной обработки: {e}")
            
            # Специфичная подсказка для poppler
            if "poppler" in error_msg.lower() or "page count" in error_msg.lower():
                safe_print(f"  💡 Для hi_res стратегии с PDF требуется poppler")
                safe_print(f"  💡 Установите poppler или используйте стратегию 'fast'")
                safe_print(f"  📖 Инструкция: УСТАНОВКА_POPPLER_WINDOWS.md")
            
            # Попытка с базовыми параметрами, но с языками
            safe_print(f"  🔄 Повторная попытка с базовыми параметрами...")
            try:
                elements = partition(
                    filename=str(file_path),
                    languages=["rus", "eng"]  # Сохраняем поддержку языков
                )
            except:
                # Совсем базовый вариант
                elements = partition(filename=str(file_path))
            
            return elements
    
    def load_db(self):
        """Загрузка существующей векторной БД"""
        if self.db_type == "chroma":
            if not Path(self.chroma_path).exists():
                raise FileNotFoundError(
                    f"ChromaDB индекс не найден по пути {self.chroma_path}. "
                    "Пожалуйста, сначала обработайте документы."
                )
            
            db = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings
            )
            return db
        else:  # faiss
            if not Path(self.faiss_path).exists():
                raise FileNotFoundError(
                    f"FAISS индекс не найден по пути {self.faiss_path}. "
                    "Пожалуйста, сначала обработайте документы."
                )
            
            db = FAISS.load_local(
                self.faiss_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            return db
    
    # Обратная совместимость
    def load_faiss_db(self):
        """Загрузка FAISS БД (для обратной совместимости)"""
        self.db_type = "faiss"
        return self.load_db()

