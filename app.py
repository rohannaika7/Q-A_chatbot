from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from utils.document_loader import DocumentProcessor
from utils.vector_store import VectorStore
from chatbot.qa_chain import QAChain
from utils.session_manager import SessionManager
import os
from dotenv import load_dotenv
import logging
from typing import Optional
from fastapi.responses import StreamingResponse
import json
import uvicorn

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)


app = FastAPI(title="Q&A Chatbot API")

class Question (BaseModel):
    text: str
    session_id: Optional [str] = None

#Initialize components
doc_processor = DocumentProcessor("./ubuntu-docs")
vector_store = VectorStore("./vector_store")
qa_chain = None
session_manager = SessionManager()

@app.on_event("startup")
async def startup_event():
    global qa_chain

    try: 
        documents_path = os.path.abspath("./ubuntu-docs") 
        logger.info(f"Loading documents from: {documents_path}")

        #Initialize with absolute path 
        doc_processor = DocumentProcessor(documents_path)
        logger.info("Creating new vector store...")
        documents = doc_processor.load_documents()
        chunks = doc_processor.split_documents(documents)
        vs = vector_store.create_vector_store(chunks)
        qa_chain = QAChain(vs)
        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Critical error during startup: {str(e)}")
        raise RuntimeError(f"Failed to initialize the application: {str(e)}") from e

@app.post("/create_session")
async def create_session():
    session_id = question.session_id 
    return {"session_id": session_id}

@app.post("/ask")
async def ask_question (question: Question):
    try:
        session_id = question.session_id
        if not session_id:
            session_id = session_manager.create_session()
        session  = session_manager.get_session(session_id) 
        if not session:
            raise HTTPException(status_code-481, detail="Invalid or expired session")

        #Get conversation history from session
        conversation_history = session.get('conversation history', [])

        # Pass conversation history to QA chain
        answer = qa_chain.get_answer(question.text, conversation_history)

        # Update conversation history
        session_manager.update_conversation(session_id, question.text, answer)

        return {
            "answer": answer,
            "session_id": session_id
        }

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/ask stream")
async def ask_question_stream(question: Question):
    try:
        session_id = question.session_id
        if not session_id:
            session_id = session_manager.create_session()

        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        conversation_history = session.get('conversation_history', [])

        async def generate():
            full_response = ""
            async for chunk in qa_chain.get_answer_stream(question.text, conversation_history):
                full_response += chunk
                yield f"data: {json.dumps({chunk: chunk})}\n\n"
                #update conversation history after streaming completes
            session_manager.update_conversation(session_id, question.text, full_response)
            yield f"data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control":"no-cache",
                "Connection":"keep-alive",
            }
        )
    except Exception as e:
        logger.error(f"Error in streaming response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)