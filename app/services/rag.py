import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIR
        self.embedding_function = None
        self.llm = None

    def _ensure_initialized(self):
        if not self.embedding_function:
            print("Initializing RAG models...")
            self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
            self.llm = HuggingFaceEndpoint(
                repo_id=repo_id, 
                task="text-generation",
                max_new_tokens=512,
                do_sample=False,
                repetition_penalty=1.03,
                huggingfacehub_api_token=settings.HF_API_TOKEN
            )
            print("RAG models initialized.")

    def process_subtitles(self, file_path: str, video_id: str):
        """
        Ingest subtitles into vector store.
        """
        self._ensure_initialized()
        
        # 1. Load Data
        loader = TextLoader(file_path)
        documents = loader.load()
        
        # 2. Split Data
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        # 3. Store in VectorDB
        # We use a separate collection for each video or filter by metadata.
        # For simplicity, let's just use one collection but filter by source if needed?
        # Actually, creating a new collection per video might be cleaner for isolation but heavier.
        # using metadata={"video_id": video_id} is better.
        
        for chunk in chunks:
            chunk.metadata["video_id"] = video_id
            
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_function,
            persist_directory=self.persist_directory,
            collection_name="video_subtitles"
        )
        return True

    def get_answer(self, video_id: str, question: str):
        """
        Ask a question about a specific video.
        """
        self._ensure_initialized()
        
        vectorstore = Chroma(
            persist_directory=self.persist_directory, 
            embedding_function=self.embedding_function,
            collection_name="video_subtitles"
        )
        
        # Retrieve only docs for this video
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 3, "filter": {"video_id": video_id}}
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        result = qa_chain.invoke({"query": question})
        return result["result"]

rag_service = RAGService()
