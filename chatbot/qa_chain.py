from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import os
import logging
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from typing import List, Dict
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import AsyncGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = "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"

class QAChain:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatGroq(
            model_name="llama3-70b-8192", 
            api_key=GROQ_API_KEY
        )
        self.qa_chain = self._create_qa_chain()
        self.memory = ConversationBufferMemory()
        self.streaming_chain = self._create_streaming_chain()

    def _create_qa_chain(self):
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 5}
                ),
                return_source_documents=True,
                verbose=True
            )
            return qa_chain
        except Exception as e:
            logger.error(f"Error creating QA chain: {str(e)}")
            raise

    def _create_streaming_chain(self):
        try:
            callbacks = [StreamingStdOutCallbackHandler()]
            return ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error creating streaming chain: {str(e)}")
            raise

    def _format_chat_history(self, history: List[Dict]) -> str:
        formatted_history = []
        for interaction in history:
            formatted_history.extend([
                f"Human: {interaction['question']}",
                f"Assistant: {interaction['answer']}"
            ])
        return "\n".join(formatted_history)

    def get_answer(self, question: str, conversation_history: List[Dict] = None) -> str:
        try:
            chat_history = ""
            if conversation_history:
                chat_history = self._format_chat_history(conversation_history)
                
            context = f"""Previous conversation:{chat_history}

Current question: {question}

Instructions:
- Answer using ONLY the information found in the provided documents and previous conversation.
- Do not include any external knowledge or assumptions
- If the information is not in the documents, state "I cannot find this information in the provided documents"
- Base the response purely on the document content"""

            result = self.qa_chain({"query": context})
            answer = result["result"]
            source_docs = result["source_documents"]
            print(source_docs)
            # Extract chunk details from source_docs as needed
            return answer
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            raise

    async def get_answer_stream(self, question: str, conversation_history: List[Dict] = None) -> AsyncGenerator[str, None]:
        try:
            chat_history = ""
            if conversation_history:
                chat_history = self._format_chat_history(conversation_history)

            context = f"""Previous conversation:{chat_history}

Current question: {question}

Instructions:
- Answer using ONLY the information found in the provided documents and previous conversation.
- Do not include any external knowledge or assumptions
- Base the response purely on the document content"""

            async for chunk in self.streaming_chain.astream(
                {"question": context, "chat_history": []}
            ):
                if isinstance(chunk, dict) and "answer" in chunk:
                    yield chunk["answer"]
                elif isinstance(chunk, str):
                    yield chunk
                
        except Exception as e:
            logger.error(f"Error in streaming answer: {str(e)}")
            raise
