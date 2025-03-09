# chat_manager.py - Chat history and LLM integration
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from typing import List, Dict, Any, Tuple, Optional
import os
import json
from datetime import datetime


def get_llm(api_key: str, temperature: float = 0.1):
    """Get OpenAI chat model."""
    return ChatOpenAI(
        openai_api_key=api_key,
        temperature=temperature,
        model_name="gpt-4o-mini"
    )


def get_chat_history(chat_id: str, history_dir: str, max_history: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get chat history for a specific chat ID.

    Args:
        chat_id: The chat ID
        history_dir: Directory where chat histories are stored
        max_history: Maximum number of recent messages to return

    Returns:
        List of chat messages
    """
    history_file = os.path.join(history_dir, f"{chat_id}.json")

    if not os.path.exists(history_file):
        return []

    with open(history_file, "r") as f:
        history = json.load(f)

    if max_history is not None and max_history > 0:
        return history[-max_history:]

    return history


def add_message_to_history(chat_id: str, role: str, content: str, history_dir: str):
    """
    Add a message to chat history.

    Args:
        chat_id: The chat ID
        role: Message role (user or assistant)
        content: Message content
        history_dir: Directory where chat histories are stored
    """
    history_file = os.path.join(history_dir, f"{chat_id}.json")

    # Create or load existing history
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = []

    # Add new message
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    # Save updated history
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)


def format_chat_history(history: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """
    Format chat history for the ConversationalRetrievalChain.

    Args:
        history: List of chat messages

    Returns:
        List of tuples (human message, ai message)
    """
    formatted_history = []

    for i in range(0, len(history) - 1, 2):
        if i + 1 < len(history):
            if history[i]["role"] == "user" and history[i + 1]["role"] == "assistant":
                formatted_history.append((history[i]["content"], history[i + 1]["content"]))

    return formatted_history


def get_answer(query: str, vectorstore: FAISS, chat_history: List[Dict[str, Any]], api_key: str) -> Tuple[
    str, List[Dict[str, Any]]]:
    """
    Get answer for a query using RAG.

    Args:
        query: The user query
        vectorstore: FAISS vector store
        chat_history: List of previous chat messages
        api_key: OpenAI API key

    Returns:
        Answer and source documents
    """
    llm = get_llm(api_key)

    # Format chat history for the retrieval chain
    formatted_history = format_chat_history(chat_history)

    # Create memory object
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key="question",
        output_key="answer",
        chat_memory=ChatMessageHistory()
    )


    # Load memory with previous chat history
    for human_msg, ai_msg in formatted_history:
        memory.chat_memory.add_user_message(human_msg)
        memory.chat_memory.add_ai_message(ai_msg)

    # Create retrieval chain
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    # Get answer
    result = qa_chain.invoke({"question": query})

    # Format source documents
    sources = []
    for doc in result["source_documents"]:
        sources.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", None)
        })

    return result["answer"], sources