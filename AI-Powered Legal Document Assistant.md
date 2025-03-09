# AI-Powered Legal Document Assistant

## Project: AI-Powered Legal Document Assistant  
**Team:** AI Development Team  
**Audience:** Frontend Team  

## User Stories (Frontend Perspective)
- **As a user**, I want to upload legal documents (PDF/text) so the system can process them for analysis.
- **As a user**, I want to search for specific clauses/terms in my documents using natural language queries.
- **As a user**, I want to ask questions about the documents and receive concise, context-aware answers.
- **As a user**, I want to view summarized versions of complex legal texts in plain language.

## Technical Specifications for AI-Frontend Integration

### 1. Document Upload & Processing
#### **Frontend Responsibilities:**
- Provide a UI/API endpoint to upload documents (PDF/text) to AWS S3.
- After upload, send the S3 object key or presigned URL to the AI backend.

#### **AI Backend API Endpoint:**
```http
POST /api/upload
```
##### **Request Body:**
```json
{
  "s3_key": "user123/contracts/contract.pdf",  
  "filename": "contract.pdf",  
  "user_id": "user123"  
}
```
##### **Response:**
```json
{
  "success": true,  
  "document_id": "doc_abc123",  
  "message": "Document processing started."  
}
```

#### **AI Processing Workflow:**
1. Fetch document from S3 using provided key/presigned URL.
2. Extract text from PDFs using libraries like **PyPDF2** or **pdfplumber**.
3. Split text into chunks (e.g., paragraphs/clauses) using NLP chunking.
4. Apply **NER** to identify key entities (e.g., parties, dates, obligations).
5. Generate embeddings for chunks using **Sentence Transformers** or **OpenAI Embeddings**.
6. Store embeddings in **Pinecone vector database**.

---
### 2. Semantic Search
#### **Frontend Responsibilities:**
- Send a search query (e.g., "confidentiality clause") and document ID to the AI backend.

#### **AI Backend API Endpoint:**
```http
POST /api/search
```
##### **Request Body:**
```json
{
  "document_id": "doc_abc123",  
  "query": "confidentiality clause",  
  "user_id": "user123"  
}
```
##### **Response:**
```json
{
  "results": [  
    {  
      "chunk_id": "chunk_1",  
      "text": "Section 5. Confidentiality: All parties agree to...",  
      "relevance_score": 0.95,  
      "page_number": 3  
    }  
  ]  
}
```

#### **AI Workflow:**
- Use **semantic similarity (vector search)** to retrieve relevant document chunks from **Pinecone**.

---
### 3. Q&A with RAG + LLM
#### **Frontend Responsibilities:**
- Send a user question (e.g., "What are the termination conditions?") and document ID to the AI backend.

#### **AI Backend API Endpoint:**
```http
POST /api/qa
```
##### **Request Body:**
```json
{
  "document_id": "doc_abc123",  
  "question": "What are the termination conditions?",  
  "user_id": "user123"  
}
```
##### **Response:**
```json
{
  "answer": "The contract may be terminated with 30 days' written notice...",  
  "sources": ["Section 10. Termination", "Page 12"],  
  "confidence": 0.89  
}
```

#### **AI Workflow:**
1. Retrieve relevant document chunks via vector search in **Pinecone**.
2. Generate answers using **LLM (e.g., GPT-4)** with **RAG pipeline**.
3. Return answer + source references.

---
### 4. Document Summarization (Optional)
#### **Frontend Responsibilities:**
- Trigger summarization via API and display results.

#### **AI Backend API Endpoint:**
```http
POST /api/summarize
```
##### **Request Body:**
```json
{
  "document_id": "doc_abc123",  
  "user_id": "user123"  
}
```
##### **Response:**
```json
{
  "summary": "This contract outlines obligations between Party A and Party B, including confidentiality terms, payment schedules, and a 30-day termination clause...",  
  "key_clauses": ["Confidentiality", "Payment", "Termination"]  
}
```

---
## Data Formats & Integrations
### **Input from Frontend:**
- S3 object key/presigned URL, user queries, document IDs.

### **Output to Frontend:**
- Processed text chunks, search results, QA answers, summaries.

### **AI Tools:**
- **NER**: Hugging Face **spaCy** or **transformers**.
- **Embeddings**: **Sentence Transformers** or **OpenAI Embeddings**.
- **LLM**: **OpenAI GPT-4** or **Google PaLM API**.
- **Vector DB**: **Pinecone** for storage.

---
## Error Handling
### **General Guidelines:**
- Return **HTTP 400** for invalid inputs (e.g., unsupported file types).
- Return **HTTP 500** for processing failures (e.g., LLM API downtime).

##### **Example Error Response:**
```json
{
  "success": false,  
  "error": "Invalid PDF format",  
  "code": 400  
}
```

---
## Next Steps:
- **Frontend** to implement UI/API endpoints as specified.
- **AI team** to deploy backend services and test integration.
- **Joint testing** for edge cases (e.g., large documents, ambiguous queries).

