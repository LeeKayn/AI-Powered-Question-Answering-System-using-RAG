# app.py - Streamlit RAG application

import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
import uuid
import pandas as pd
from io import StringIO

# Configuration
API_URL = "http://localhost:8000"  # FastAPI backend URL
SUPPORTED_EXTENSIONS = ["pdf", "txt", "docx", "csv"]

# App title and configuration
st.set_page_config(page_title="Document Q&A System", page_icon="📚", layout="wide")

# Initialize session state variables
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing_files" not in st.session_state:
    st.session_state.processing_files = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


def check_api_status():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except:
        return False


def upload_file(file):
    """Upload a file to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), f"application/{file.type}")}
        response = requests.post(f"{API_URL}/upload", files=files)

        if response.status_code == 201:
            st.session_state.processing_files.append(file.name)
            st.session_state.uploaded_files.append(file.name)
            return True, response.json()["message"]
        else:
            return False, f"Error: {response.json()['detail']}"
    except Exception as e:
        return False, f"Error uploading file: {str(e)}"


def query_document(question):
    """Send a query to the API."""
    try:
        data = {
            "query": question,
            "chat_id": st.session_state.chat_id
        }
        response = requests.post(f"{API_URL}/query", json=data)

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()["detail"]
    except Exception as e:
        return False, f"Error querying API: {str(e)}"


def load_chat_history():
    """Load chat history from the API."""
    try:
        response = requests.get(f"{API_URL}/chat/{st.session_state.chat_id}")
        if response.status_code == 200:
            st.session_state.messages = response.json()["messages"]
    except:
        pass  # If we can't load history, just use what's in session


def format_sources(sources):
    """Format sources for display."""
    sources_text = ""
    for i, source in enumerate(sources, 1):
        source_name = source.get("source", "Unknown")
        page = source.get("page")
        page_text = f" (Page {page})" if page else ""
        sources_text += f"**Source {i}:** {source_name}{page_text}\n\n"

        # Add truncated content preview
        content = source.get("content", "")
        if len(content) > 300:
            content = content[:300] + "..."
        sources_text += f"{content}\n\n---\n\n"

    return sources_text


# App layout
st.title("📚 Document Q&A System")

# Sidebar for uploads and settings
with st.sidebar:
    st.header("📁 Document Upload")

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload documents (PDF, TXT, DOCX, CSV)",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True
    )

    # Upload button
    if uploaded_files:
        if st.button("Process Documents"):
            with st.spinner("Uploading documents..."):
                for file in uploaded_files:
                    if file.name not in st.session_state.uploaded_files:
                        success, message = upload_file(file)
                        if success:
                            st.success(f"✅ {file.name} uploaded successfully")
                        else:
                            st.error(f"❌ {message}")

    # Show list of uploaded documents
    if st.session_state.uploaded_files:
        st.header("📋 Uploaded Documents")
        for file in st.session_state.uploaded_files:
            if file in st.session_state.processing_files:
                st.text(f"⏳ {file} (processing)")
            else:
                st.text(f"✅ {file}")

    # New chat button
    if st.button("New Chat"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.success("Started a new chat session")

# Main chat area
st.header("💬 Chat with your Documents")

# Check API status
api_running = check_api_status()
if not api_running:
    st.error("⚠️ Backend API is not running. Please start the API service first.")
    st.stop()

# Load existing chat history if available
if not st.session_state.messages:
    load_chat_history()

# Display chat messages
for message in st.session_state.messages:
    role = message.get("role")
    content = message.get("content")

    if role == "user":
        st.chat_message("user").write(content)
    elif role == "assistant":
        with st.chat_message("assistant"):
            st.write(content)

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat
    st.chat_message("user").write(prompt)

    # Add to session state
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })

    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            success, response = query_document(prompt)

            if success:
                answer = response["answer"]
                sources = response["sources"]

                # Display the answer
                st.write(answer)

                # Display sources in an expander
                if sources:
                    with st.expander("View Sources"):
                        st.markdown(format_sources(sources))

                # Add to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                st.error(f"Error: {response}")

# Footer
st.markdown("---")
st.markdown("This app allows you to upload documents and ask questions about their content.")