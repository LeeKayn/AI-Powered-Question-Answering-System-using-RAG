# main.py - FastAPI application
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uvicorn
from dotenv import load_dotenv
import uuid
from datetime import datetime
import json

# Import helper modules
from document_processor import process_document, supported_extensions
from vector_store import get_vectorstore, save_vectorstore, load_vectorstore
from chat_manager import get_answer, add_message_to_history, get_chat_history

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

app = FastAPI(title="RAG Question-Answering System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    chat_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    chat_id: str
    sources: List[Dict[str, Any]]


class ChatHistory(BaseModel):
    messages: List[Dict[str, Any]]


# Storage paths
UPLOAD_DIR = "uploads"
VECTOR_STORE_DIR = "vector_store"
CHAT_HISTORY_DIR = "chat_history"

# Create necessary directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# Initialize vector store if it doesn't exist
try:
    # Try to load existing vector store
    if os.path.exists(os.path.join(VECTOR_STORE_DIR, "index.faiss")):
        print("Vector store found.")
    else:
        print("Initializing empty vector store...")
        vectorstore = get_vectorstore([])
        save_vectorstore(vectorstore, VECTOR_STORE_DIR)
        print("Empty vector store initialized.")
except Exception as e:
    print(f"Error initializing vector store: {str(e)}")
    # Create a fresh empty vector store
    print("Creating a fresh vector store...")
    vectorstore = get_vectorstore([])
    save_vectorstore(vectorstore, VECTOR_STORE_DIR)


@app.get("/")
async def root():
    return {"message": "RAG Question-Answering System API"}


@app.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    # Check file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(supported_extensions)}"
        )

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process document immediately
        docs = process_document(file_path)
        if docs:
            vectorstore = load_vectorstore(VECTOR_STORE_DIR)
            vectorstore.add_documents(docs)
            save_vectorstore(vectorstore, VECTOR_STORE_DIR)
            print(f"Document '{file_path}' processed and added to vector store")
            return {"message": f"File '{file.filename}' uploaded and processed successfully"}
        else:
            return {"message": f"File '{file.filename}' uploaded but no content was extracted"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        # Load vector store
        vectorstore = load_vectorstore(VECTOR_STORE_DIR)

        chat_id = request.chat_id
        if not chat_id:
            # Create new chat ID if not provided
            chat_id = str(uuid.uuid4())

        # Get chat history (last 3 messages)
        chat_history = get_chat_history(chat_id, CHAT_HISTORY_DIR, max_history=3)

        # Get answer
        answer, sources = get_answer(request.query, vectorstore, chat_history, OPENAI_API_KEY)

        # Add message to history
        add_message_to_history(chat_id, "user", request.query, CHAT_HISTORY_DIR)
        add_message_to_history(chat_id, "assistant", answer, CHAT_HISTORY_DIR)

        return {
            "answer": answer,
            "chat_id": chat_id,
            "sources": sources
        }
    except Exception as e:
        if "no docs in retriever" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="No documents have been uploaded yet. Please upload documents first."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/chat/{chat_id}", response_model=ChatHistory)
async def get_chat(chat_id: str):
    try:
        messages = get_chat_history(chat_id, CHAT_HISTORY_DIR)
        return {"messages": messages}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chat history not found")


def process_and_update_vectorstore(file_path: str):
    try:
        # Process document
        docs = process_document(file_path)

        if not docs:
            print(f"No content extracted from document '{file_path}'")
            return

        try:
            # Try to load existing vector store
            vectorstore = load_vectorstore(VECTOR_STORE_DIR)
            # Add new documents to vector store
            vectorstore.add_documents(docs)
        except Exception as e:
            print(f"Error loading existing vector store: {str(e)}")
            # Create new vector store with documents
            vectorstore = get_vectorstore(docs)

        # Save updated vector store
        save_vectorstore(vectorstore, VECTOR_STORE_DIR)

        print(f"Document '{file_path}' processed and added to vector store")
    except Exception as e:
        print(f"Error processing document '{file_path}': {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)