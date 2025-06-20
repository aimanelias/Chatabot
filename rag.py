#pip install sentence-transformers huggingface-hub --upgrade
# pdf_rag.py

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Use raw strings so backslashes aren’t treated as escapes
INDEX_DIR = r"C:\Users\hyper\Desktop\multimodal-chatbot\multimodal-chatbot-UI-main\multimodal\rag_data"
PDF_PATH  = r"C:\Users\hyper\Desktop\multimodal-chatbot\multimodal-chatbot-UI-main\multimodal\rag_data\DOSH Malaysia-2022.pdf"

def build_index():
    """One-time: load PDF, chunk, embed, and save FAISS index."""
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = FAISS.from_documents(chunks, embedder)
    index.save_local(INDEX_DIR)

def load_index():
    """On-startup: load the existing FAISS index."""
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # You built this index locally, so it’s safe to allow pickle deserialization:
    return FAISS.load_local(
        INDEX_DIR,
        embedder,
        allow_dangerous_deserialization=True
    )

if __name__ == "__main__":
    print("Building RAG index from PDF…")
    build_index()
    print("Done. Index saved to", INDEX_DIR)
