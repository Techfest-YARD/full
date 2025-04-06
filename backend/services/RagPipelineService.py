from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from services.gemini_service import GeminiService
import sqlalchemy
from sqlalchemy import text
import time

# Załóżmy, że plik z tekstem
loader = TextLoader("xd.txt")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

default_prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    Odpowiedz na pytanie na podstawie poniższego kontekstu. Jeśli nie wiesz, powiedz, że nie wiesz.

    KONTEKST:
    {context}

    PYTANIE:
    {question}

    ODPOWIEDŹ:"""
)

prompt_template_curious_child = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a curious child who wants to understand the world deeply.
Ask thoughtful and exploratory questions. Be genuinely interested.
Answer the question based only on the following context. If you don't know the answer, say you don't know.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER (in the style of a curious child):
"""
)

prompt_template_generate_questins = PromptTemplate(
    input_variables=["context"],
    template="""
You are an AI tutor. Based on the following educational content, generate 5 short discussion topics.

CONTENT:
{context}

Return the topics as a plain list, one per line.
"""
)

prompt_template_teacher = PromptTemplate(
    input_variables=["topic", "conversation", "round"],
    template="""
You are a friendly and knowledgeable teacher helping a student understand the topic: {topic}.

Here is the conversation history so far:
{conversation}

We are in round {round}.
Please continue the conversation by asking a follow-up question or giving feedback to encourage the student to elaborate or give examples.
"""
)

# GeminiLLM jako interfejs do zapytań
class GeminiLLM:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def get_answear(self, prompt: str) -> str:
        return await self.gemini_service.ask(prompt)

    @property
    def _llm_type(self) -> str:
        return "gemini_service"

gemini_service = GeminiService() 
gemini_llm = GeminiLLM(gemini_service=gemini_service)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1")


def connect_via_public_ip() -> sqlalchemy.engine.base.Engine:
    """
    Tworzy połączenie z PostgreSQL (np. w Cloud SQL) przez publiczny IP,
    używając SQLAlchemy + psycopg2.
    """
    host = "35.246.200.139"      # publiczny IP bazy
    port = 5432
    db_user = "postgres"
    db_pass = '()+;Cf#V?+`?jqp"'
    db_name = "postgres"

    connection_url = f"postgresql+psycopg2://{db_user}:{db_pass}@{host}:{port}/{db_name}"
    engine = sqlalchemy.create_engine(connection_url)
    return engine


class RagPipelineService:
    def __init__(self, logger):
        self.llm = gemini_llm
        self.prompt_template = default_prompt_template
        self.logger = logger
        self.embedding_model = embedding_model

    def _find_context(self, query: str, k: int = 3) -> str:
        """
        Oblicza embedding zapytania, łączy się z bazą (poprzez SQLAlchemy engine)
        i zwraca scalony tekst z top k najbardziej podobnych dokumentów.
        """
        try:
            # 1. Embedding zapytania (lista floatów)
            query_embedding = self.embedding_model.embed_query(query)

            # Konwersja listy Pythona do formatu {0.12,0.24,...}
            embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

            # 2. Stworzenie engine i połączenie
            engine = connect_via_public_ip()

            # 3. Zapytanie SQL - sortowanie po dystansie wektorowym (pgvector)
            # Operator <-> (najprawdopodobniej kosinus lub Euclides, zależnie od configu)
            # Uwaga: Używamy f-string, bo parametryzowanie limitu i operatora <-> bywa tricky.
            sql = f"""
                SELECT embedding
                FROM embeddings
                ORDER BY embedding <-> '{embedding_str}'
                LIMIT {k}
            """

            # Wykonujemy SELECT w kontekście engine
            with engine.connect() as conn:
                rows = conn.execute(text(sql)).fetchall()

            # 4. Zbieramy treści w jeden ciąg
            context = "\n".join(row[0] for row in rows)
            return context

        except Exception as e:
            raise RuntimeError(f"Nie udało się pobrać kontekstu: {str(e)}")

    async def _run_internal(self, query: str, prompt_template: PromptTemplate, style: str):
        try:
            start = time.time()

            # Pobieramy kontekst z bazy
            context = self._find_context(query)

            # Tworzymy prompt
            prompt = prompt_template.format(context=context, question=query)
            response = await self.llm.get_answear(prompt)

            end = time.time()

            self.logger.log_llm_call({
                "query": query,
                "prompt": prompt,
                "response_length": len(response),
                "context_length": len(context),
                "duration_ms": int((end - start) * 1000),
                "source": f"gemini_llm_{style}",
                "error": None
            })

            return response

        except Exception as e:
            self.logger.log_llm_call({
                "query": query,
                "prompt": "",
                "response_length": 0,
                "context_length": 0,
                "duration_ms": 0,
                "source": f"gemini_llm_{style}",
                "error": str(e)
            })
            raise

    def run(self, query: str):
        return self._run_internal(query, default_prompt_template, style="default")

    def run_curious_child(self, query: str):
        return self._run_internal(query, prompt_template_curious_child, style="curiosity_mode")

    def generate_topics_from_context(self, query: str):
        """
        Generuje listę 5 krótkich tematów/dyskusji na bazie kontekstu.
        """
        try:
            start = time.time()

            context = self._find_context(query)
            prompt = prompt_template_generate_questins.format(context=context)
            response = self.llm(prompt)

            end = time.time()

            self.logger.log_llm_call({
                "query": query,
                "prompt": prompt,
                "response_length": len(response),
                "context_length": len(context),
                "duration_ms": int((end - start) * 1000),
                "source": "gemini_llm_generate_topics",
                "error": None
            })

            # Konwersja tekstu wyjściowego do listy 5 tematów
            topics = [line.strip("-• ").strip() for line in response.splitlines() if line.strip()]
            return topics[:5]

        except Exception as e:
            self.logger.log_llm_call({
                "query": query,
                "prompt": "",
                "response_length": 0,
                "context_length": 0,
                "duration_ms": 0,
                "source": "gemini_llm_generate_topics",
                "error": str(e)
            })
            return ["General Topic: Review the material"]
