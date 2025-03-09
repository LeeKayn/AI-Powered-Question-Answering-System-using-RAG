# vector_store.py - Vector store operations
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import os
import pickle
import shutil


def get_embeddings(api_key: Optional[str] = None):
    """Get OpenAI embeddings model."""
    return OpenAIEmbeddings(openai_api_key=api_key)


def get_vectorstore(documents: List[Document], api_key: Optional[str] = None):
    """Create a new FAISS vector store from documents."""
    embeddings = get_embeddings(api_key)

    # Handle empty documents case (initial setup)
    if not documents:
        # Create a single dummy document with content
        dummy_doc = Document(page_content="This is a placeholder document.", metadata={"source": "initialization"})
        vector_store = FAISS.from_documents([dummy_doc], embeddings)
        return vector_store

    return FAISS.from_documents(documents, embeddings)


def save_vectorstore(vectorstore: FAISS, directory: str):
    """Save FAISS vector store to disk."""
    # Create temp directory for saving
    temp_dir = f"{directory}_temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Save to temp directory first
    vectorstore.save_local(temp_dir)

    # Move files to final destination (atomic operation to prevent corruption)
    if os.path.exists(directory):
        shutil.rmtree(directory)
    shutil.move(temp_dir, directory)


def load_vectorstore(directory: str, api_key: Optional[str] = None):
    """Load FAISS vector store from disk."""
    embeddings = get_embeddings(api_key)
    return FAISS.load_local(directory, embeddings, allow_dangerous_deserialization=True)


def search_documents(query: str, vectorstore: FAISS, k: int = 5):
    """
    Search for relevant documents in the vector store.

    Args:
        query: The search query
        vectorstore: FAISS vector store
        k: Number of documents to retrieve

    Returns:
        List of documents and their similarity scores
    """
    return vectorstore.similarity_search_with_score(query, k=k)