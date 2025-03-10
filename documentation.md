# Chat Manager Module Documentation

## Overview

The `chat_manager.py` module provides functionality for managing chat history and integrating with language models (LLMs) for conversational retrieval-augmented generation (RAG). It handles storing, retrieving, and formatting chat messages, as well as generating responses using OpenAI's language models with document retrieval capabilities.

## Key Components

### LLM Integration

- `get_llm(api_key, temperature)`: Creates and configures an OpenAI chat model (GPT-4o-mini) with the specified API key and temperature setting.

### Chat History Management

- `get_chat_history(chat_id, history_dir, max_history)`: Retrieves chat history for a specific chat ID from the file system, with an option to limit the number of recent messages returned.
  
- `add_message_to_history(chat_id, role, content, history_dir)`: Adds a new message to the chat history, storing it in a JSON file with timestamp information.
  
- `format_chat_history(history)`: Formats the chat history into a structure suitable for the ConversationalRetrievalChain, pairing user and assistant messages.

### Retrieval-Augmented Generation

- `get_answer(query, vectorstore, chat_history, api_key)`: Processes a user query using RAG to generate a contextually relevant answer based on:
  - The user's query
  - Previous conversation context
  - Relevant documents retrieved from the vector store
  
  Returns both the answer and the source documents used to generate it.

## Data Structures

- Chat messages are stored as dictionaries with:
  - `role`: Either "user" or "assistant"
  - `content`: The message text
  - `timestamp`: ISO format timestamp of when the message was created

- Source documents are returned as dictionaries with:
  - `content`: The document content
  - `source`: The document source identifier
  - `page`: Page number (if applicable)

## File Storage

Chat histories are stored as JSON files in the specified history directory, with filenames based on the chat ID.

## Dependencies

- LangChain libraries for OpenAI integration, conversation chains, and memory management
- FAISS for vector storage and similarity search
- Standard Python libraries for file operations and data handling

## Usage Flow

1. Initialize a vector store with relevant documents
2. Retrieve existing chat history for a conversation
3. Process user queries with the `get_answer` function
4. Add both user queries and assistant responses to the chat history
5. Continue the conversation with context awareness 