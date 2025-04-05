from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from services.gemini_service import GeminiService

loader = TextLoader("xd.txt")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)


prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    Odpowiedz na pytanie na podstawie poniższego kontekstu. Jeśli nie wiesz, powiedz, że nie wiesz.

    KONTEKST:
    {context}

    PYTANIE:
    {question}

    ODPOWIEDŹ:"""
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
vectorstore = PGVector(
    connection_string="postgresql://postgres:test@35.246.200.139/vectorstore",
    embedding_function=embedding_model,
    table_name="embeddings",
    vector_column="embedding"
)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})


class RagPipelineService:
    def __init__(self):
        self.retriever = retriever
        self.llm = gemini_llm
        self.prompt_template = prompt_template

    def run(self, query: str):
        retrieved_docs = self.retriever.get_relevant_documents(query)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        prompt = self.prompt_template.format(context=context, question=query)

        answer = self.llm(prompt)
        return answer

# rag_pipeline = RagPipelineService()

# query = "Czym zajmuje się twoj_plik.txt?"
# response = rag_pipeline.run(query)
# print(response)
