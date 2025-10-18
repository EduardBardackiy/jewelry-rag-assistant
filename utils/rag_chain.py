"""
Модуль для RAG цепочки
"""
import os
import sys

# Установка UTF-8 для Windows в самом начале
if os.name == 'nt':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage
from typing import Dict, Any

from .document_processor import DocumentProcessor

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


class CustomRetrievalQA(LLMChain):
    """Кастомная цепочка для работы с двумя retriever'ами"""
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        context = inputs.get("context", "")
        products = inputs.get("products", "")
        query = inputs.get("query", "")
        
        # Формируем полный промпт
        full_prompt = self.prompt.format(
            context=context, 
            products=products, 
            query=query
        )
        
        # Преобразуем промпт в список сообщений
        messages = [HumanMessage(content=full_prompt)]
        
        # Вызываем модель
        response = self.llm.invoke(messages)
        
        # Обработка ответа в зависимости от типа модели
        if isinstance(response, str):
            # Локальная модель возвращает строку
            response_text = response
        elif hasattr(response, 'content'):
            # OpenAI возвращает объект с атрибутом content
            response_text = response.content
        else:
            # Попытка преобразовать в строку
            response_text = str(response)
        
        return {"text": response_text}


class RAGChain:
    """Класс для работы с RAG системой"""
    
    def __init__(self, db_type="faiss"):
        self.model_type = os.getenv("MODEL_TYPE", "openai")
        self.db_type = db_type.lower()
        self.catalog_path = os.getenv("CATALOG_PATH", "./catalog.json")
        
        # Инициализация эмбеддингов с обработкой ошибок
        self.embeddings = self._init_embeddings()
        
        # Инициализация процессора документов с выбранным типом БД
        self.doc_processor = DocumentProcessor(db_type=self.db_type)
        
        # Загрузка векторной БД
        self.db = self.doc_processor.load_db()
        self.retriever = self.db.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}
        )
        
        # Загрузка каталога товаров
        self.catalog_db = self._load_catalog()
        self.catalog_retriever = self.catalog_db.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}
        )
        
        # Инициализация LLM
        self.llm = self._init_llm()
        
        # Создание RAG цепочки
        self.rag_chain = self._create_rag_chain()
    
    def _load_catalog(self):
        """Загрузка каталога товаров"""
        if not Path(self.catalog_path).exists():
            # Создание примера каталога если его нет
            self._create_sample_catalog()
        
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        
        documents = []
        for element in catalog:
            documents.append(
                Document(
                    page_content=element['description'], 
                    metadata=element
                )
            )
        
        # Создаем каталог в той же БД, что и основная
        if self.db_type == "chroma":
            # Фильтрация метаданных для ChromaDB
            filtered_documents = filter_complex_metadata(documents)
            
            # Дополнительная очистка
            clean_documents = []
            for doc in filtered_documents:
                clean_metadata = {}
                for key, value in doc.metadata.items():
                    if isinstance(value, (str, int, float, bool, type(None))):
                        clean_metadata[key] = value
                    elif isinstance(value, list):
                        clean_metadata[key] = ", ".join(str(v) for v in value)
                    elif isinstance(value, dict):
                        clean_metadata[key] = str(value)
                    else:
                        clean_metadata[key] = str(value)
                
                clean_documents.append(
                    Document(page_content=doc.page_content, metadata=clean_metadata)
                )
            
            catalog_db = Chroma.from_documents(
                documents=clean_documents,
                embedding=self.embeddings,
                persist_directory=os.getenv("CHROMA_CATALOG_PATH", "./chroma_catalog")
            )
        else:  # faiss
            catalog_db = FAISS.from_documents(documents, self.embeddings)
        
        return catalog_db
    
    def _init_embeddings(self):
        """Инициализация эмбеддингов с обработкой ошибок"""
        import time
        import ssl
        
        model_name = "BAAI/bge-base-en-v1.5"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                safe_print(f"Загрузка модели эмбеддингов... (попытка {attempt + 1}/{max_retries})")
                
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
                    raise Exception(
                        "Не удалось загрузить модель эмбеддингов. "
                        "Проверьте подключение к интернету."
                    )
    
    def _create_sample_catalog(self):
        """Создание примера каталога"""
        catalog = [
            {
                "name": "Кольцо с бриллиантом",
                "description": "Элегантное кольцо с высококачественным бриллиантом 0.5 карата.",
                "usage": "Идеально подходит для особых случаев, таких как помолвка или свадьба.",
                "price": "15000 руб.",
                "url": "https://example.com/product/1"
            },
            {
                "name": "Серебряные серьги с аметистами",
                "description": "Серьги из 925 стерлингового серебра с аметистами высшей пробы.",
                "usage": "Подходят для ежедневного ношения или торжественных мероприятий.",
                "price": "8000 руб.",
                "url": "https://example.com/product/2"
            },
            {
                "name": "Золотая подвеска с изумрудом",
                "description": "Изысканная подвеска из 14-каратного золота с натуральным изумрудом.",
                "usage": "Отлично смотрится как для повседневного, так и для вечернего образа.",
                "price": "22000 руб.",
                "url": "https://example.com/product/3"
            },
            {
                "name": "Браслет с цирконами",
                "description": "Тонкий браслет с вставками из искусственных цирконов.",
                "usage": "Подходит для праздничных случаев или в качестве стильного аксессуара.",
                "price": "3500 руб.",
                "url": "https://example.com/product/4"
            },
            {
                "name": "Серьги с жемчугом",
                "description": "Классические серьги с натуральным жемчугом и золотыми вставками.",
                "usage": "Идеально для повседневного ношения или для элегантных мероприятий.",
                "price": "10000 руб.",
                "url": "https://example.com/product/5"
            },
        ]
        
        with open(self.catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=4, ensure_ascii=False)
    
    def _init_llm(self):
        """Инициализация LLM модели"""
        if self.model_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your_openai_api_key_here":
                raise ValueError(
                    "Пожалуйста, укажите OPENAI_API_KEY в файле .env "
                    "или измените MODEL_TYPE на 'local'"
                )
            return ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
        
        elif self.model_type == "local":
            # Для локальной модели потребуется больше ресурсов
            # ВНИМАНИЕ: На Windows без CUDA это будет работать медленно!
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            from langchain_community.llms import HuggingFacePipeline
            from huggingface_hub.hf_api import HfFolder
            
            # Сохранение токена HuggingFace
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            if hf_token and hf_token != "your_huggingface_token_here":
                HfFolder.save_token(hf_token)
            
            model_name = "IlyaGusev/saiga_llama3_8b"
            
            # Загрузка модели (с квантизацией на GPU или оптимизацией для CPU)
            has_cuda = torch.cuda.is_available()
            
            if has_cuda:
                # GPU доступен - используем 4-bit квантизацию
                try:
                    from transformers import BitsAndBytesConfig
                    
                    safe_print("GPU обнаружен! Загрузка с 4-bit квантизацией...")
                    
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16
                    )
                    
                    model = AutoModelForCausalLM.from_pretrained(
                        model_name, 
                        quantization_config=bnb_config,
                        device_map="auto"
                    )
                    
                    safe_print("OK: Модель загружена с 4-bit квантизацией (~4-5GB)")
                    
                except Exception as e:
                    safe_print(f"WARN: Квантизация не удалась: {e}")
                    safe_print("Загрузка на GPU без квантизации...")
                    
                    model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        dtype=torch.float16,
                        low_cpu_mem_usage=True,
                        device_map="auto"
                    )
                    safe_print("OK: Модель загружена на GPU (float16)")
            else:
                # CPU - используем оптимизированную загрузку
                safe_print("GPU не обнаружен. Загрузка модели на CPU...")
                safe_print("ВНИМАНИЕ: Модель займет ~16GB RAM и будет работать медленно")
                safe_print("Рекомендуется использовать OpenAI API для CPU (MODEL_TYPE=openai)")
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    device_map="cpu"
                )
                
                safe_print("OK: Модель загружена на CPU (может работать медленно)")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            terminators = [
                tokenizer.eos_token_id,
                tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]
            
            text_generation_pipeline = pipeline(
                model=model,
                tokenizer=tokenizer,
                task="text-generation",
                temperature=0.5,
                do_sample=True,
                repetition_penalty=1.1,
                return_full_text=False,
                max_new_tokens=700,
                eos_token_id=terminators,
            )
            
            return HuggingFacePipeline(pipeline=text_generation_pipeline)
        
        else:
            raise ValueError(f"Неподдерживаемый тип модели: {self.model_type}")
    
    def _create_rag_chain(self):
        """Создание RAG цепочки"""
        if self.model_type == "openai":
            prompt_template = """
Ты — умный ассистент, специализирующийся на ювелирных украшениях.
Ваши основные задачи:
1. Отвечать на вопросы о ювелирных украшениях, их характеристиках и ценах по следующему контексту: {context}
2. Помогать клиентам в выборе подходящих товаров по следующему контексту: {products}

Ваша цель — предоставлять полезные, понятные и дружелюбные ответы.
Если вы не знаете ответа, просто скажите: «Я не знаю». Не придумывайте информацию.
При предложении товаров старайтесь быть конкретным и описывать, как товар может помочь.
Если для ответа требуется больше информации, задавайте уточняющие вопросы.

Вопрос: {query}
"""
        else:  # local
            prompt_template = """
<|start_header_id|>user<|end_header_id|>
Ты — умный ассистент, специализирующийся на ювелирных украшениях.
Ваши основные задачи:
1. Отвечать на вопросы о ювелирных украшениях, их характеристиках и ценах по следующему контексту {context}
2. Помогать клиентам в выборе подходящих товаров по следующему контексту {products}

Ваша цель — предоставлять полезные, понятные и дружелюбные ответы.
Если вы не знаете ответа, просто скажите: «Я не знаю». Не придумывайте информацию.
При предложении товаров старайтесь быть конкретным и описывать, как товар может помочь.
Если для ответа требуется больше информации, задавайте уточняющие вопросы.

Вопрос: {query}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        
        prompt = PromptTemplate(
            input_variables=["context", "products", "query"],
            template=prompt_template
        )
        
        return CustomRetrievalQA(llm=self.llm, prompt=prompt)
    
    def format_docs(self, docs):
        """Форматирование документов"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def format_products(self, products):
        """Форматирование товаров"""
        return "\n".join(
            f"Название: {doc.metadata['name']}\n"
            f"Описание: {doc.page_content}\n"
            f"Цена: {doc.metadata['price']}\n"
            f"Ссылка: {doc.metadata['url']}\n"
            for doc in products
        )
    
    def get_response(self, query: str) -> str:
        """Получение ответа на запрос"""
        # Извлечение контекста
        context = self.format_docs(
            self.retriever.get_relevant_documents(query)
        )
        products = self.format_products(
            self.catalog_retriever.get_relevant_documents(query)
        )
        
        # Вызов цепочки
        result = self.rag_chain.invoke({
            "context": context,
            "query": query,
            "products": products
        })
        
        return result['text']

