# Q-A_chatbot

# Q&A Chatbot API

This project is a Q&A Chatbot API built using FastAPI, LangChain, and various other libraries. The chatbot can answer questions based on provided documents and maintain conversation history across sessions.

## Detailed Summary of Methods

### 1. `DocumentProcessor` Class
- **Purpose**: To process documents by loading and splitting them into chunks.
- **Methods**:
  - `__init__(self, directory_path: str)`: Initializes the `DocumentProcessor` with a directory path.
  - `load_documents(self)`: Loads documents from the specified directory.
  - `split_documents(self, documents)`: Splits the loaded documents into chunks.

### 2. `VectorStore` Class
- **Purpose**: To manage the creation and loading of a vector store using Chroma and HuggingFace embeddings.
- **Methods**:
  - `__init__(self, persist_directory: str)`: Initializes the `VectorStore` with a directory to persist the vector data.
  - `create_vector_store(self, documents)`: Creates a vector store from the provided documents.
  - `load_vector_store(self)`: Loads the vector store from the persistent directory.

### 3. `SessionManager` Class
- **Purpose**: To manage user sessions with timeout and conversation history.
- **Methods**:
  - `__init__(self, session_timeout_minutes: int = 30)`: Initializes the `SessionManager` with a session timeout.
  - `create_session(self) -> str`: Creates a new session and returns its ID.
  - `get_session(self, session_id: str) -> Optional[dict]`: Retrieves a session by its ID.
  - `update_conversation(self, session_id: str, question: str, answer: str)`: Updates the conversation history of a session.

### 4. `QAChain` Class
- **Purpose**: To manage the QA chain and handle question-answering tasks.
- **Methods**:
  - `__init__(self, vector_store)`: Initializes the `QAChain` with a vector store.
  - `_create_qa_chain(self)`: Creates the QA chain for retrieval-based question answering.
  - `_create_streaming_chain(self)`: Creates the streaming chain for conversational retrieval.
  - `_format_chat_history(self, history: List[Dict]) -> str`: Formats the chat history into a string.
  - `get_answer(self, question: str, conversation_history: List[Dict] = None) -> str`: Gets an answer to the given question using the QA chain.
  - `get_answer_stream(self, question: str, conversation_history: List[Dict] = None) -> AsyncGenerator[Dict[str, str], None]`: Gets an answer to the given question using the streaming chain.

### 5. FastAPI Endpoints
- **Purpose**: To provide API endpoints for creating sessions, asking questions, and streaming answers.
- **Endpoints**:
  - `@app.on_event("startup")`: Initializes the application components on startup.
  - `@app.post("/create_session")`: Endpoint to create a new session.
  - `@app.post("/ask")`: Endpoint to ask a question and get an answer.
  - `@app.post("/ask_stream")`: Endpoint to ask a question and get an answer as a stream.

## How to Run

1. Clone the repository.
2. Install the required dependencies.
3. Run the FastAPI application using `uvicorn`.

```bash
uvicorn app:app --reload
```

4. Access the API documentation at `http://localhost:8000/docs`.
