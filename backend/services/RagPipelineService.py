from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from services.gemini_service import GeminiService
import time

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

    def __call__(self, prompt: str) -> str:
        return self.gemini_service.ask(prompt)

    @property
    def _llm_type(self) -> str:
        return "gemini_service"

gemini_service = GeminiService() 
gemini_llm = GeminiLLM(gemini_service=gemini_service)


embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

class RagPipelineService:
    def __init__(self, logger):
        self.llm = gemini_llm
        self.prompt_template = default_prompt_template
        self.logger = logger

    def _find_context(self, query):
        embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = PGVector(
            connection_string="postgresql://postgres:test@35.246.200.139:5432/vectorstore",
            embedding_function=embedding_model,
            collection_name="embeddings"
        )
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})


        retrieved_docs = retriever.get_relevant_documents(query)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        return context

    def _run_internal(self, query: str, prompt_template: PromptTemplate, style: str):
        try:
            start = time.time()

            context = self._find_context(query)

            # Formatowanie prompta
            prompt = prompt_template.format(context=context, question=query)
            response = self.llm(prompt)

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
        try:
            start = time.time()

            context = self._find_context(query)

            # Użyj prompta do generowania tematów
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

            # Przetwarzanie listy tematów
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


# rag_pipeline = RagPipelineService()

# query = "Czym zajmuje się twoj_plik.txt?"
# response = rag_pipeline.run(query)
# print(response)
