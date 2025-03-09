# document_processor.py - Document processing utilities
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    CSVLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import os

# Supported file extensions and their corresponding loaders
supported_extensions = ["pdf", "txt", "docx", "csv"]


def get_loader(file_path: str):
    """Get the appropriate document loader based on file extension."""
    extension = file_path.split(".")[-1].lower()

    if extension == "pdf":
        return PyPDFLoader(file_path)
    elif extension == "txt":
        return TextLoader(file_path)
    elif extension == "docx":
        return UnstructuredWordDocumentLoader(file_path)
    elif extension == "csv":
        return CSVLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")


def process_document(file_path: str):
    """
    Process a document and split it into chunks.

    Args:
        file_path: Path to the document file

    Returns:
        List of document chunks
    """
    # Load document
    loader = get_loader(file_path)
    documents = loader.load()

    # Add metadata with source information
    for doc in documents:
        doc.metadata["source"] = os.path.basename(file_path)

    # Split document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    return text_splitter.split_documents(documents)