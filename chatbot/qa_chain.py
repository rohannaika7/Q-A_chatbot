from langchain.chains import RetrievalQA
import os
import logging
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from typing import List, Dict
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import AsyncGenerator
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

class QAChain:
    """
    A class to manage the QA chain and make handle question answering tasks.
    """
    def __init__(self, vector_store):
        """
        Initialize the QA chain and handle question-answering tasks.

        :param vector_store: The vector store to be used for retrieval.
        """
        self.vector_store = vector_store
        self.llm = ChatGroq(
            model_name="llama3-70b-8192",
        )
        self.qa_chain = self._create_qa_chain()
        self.memory = ConversationBufferMemory()
        self.streaming_chain = self._create_streaming_chain()

    def _create_qa_chain(self):
        """
        Create the QA chain for retrieval-based question answering.

        :return: the created QA chain. 
        """
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
        """
        Create the streaming chain for conversational retrieval.

        :return: The created streaming chain.
        """
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
        """
        Format teh chat history into a string.

        :param history: List of interaction dictionaries containing questions and answers.
        :return: Formatted chat history as a string.
        """
        formatted_history = []
        for interaction in history:
            formatted_history.extend([
                f"Human: {interaction['question']}",
                f"Assistant: {interaction['answer']}"
            ])
        return "\n".join(formatted_history)

    def get_answer(self, question: str, conversation_history: List[Dict] = None) -> str:
        """
        Get an answer to the given question using the QA chain.

        :param question: The question to be answered.
        :param conversation_history: List of previous interactions.
        :return: The answer to the question.
        """
        try:
            chat_history = ""
            if conversation_history:
                chat_history = self._format_chat_history(conversation_history)
                
            context = f"""Previous conversation:{chat_history}

Current question: {question}

Instructions:
- Answer using ONLY the information found in the provided documents and previous conversations.
- Ensure that the answer is accurate and is very detailed.
- Do not include any external knowledge or assumptions
- Base the response purely on the document content"""

            result = self.qa_chain({"query": context})
            answer = result["result"]
            source_docs = result["source_documents"]

            detailed_answer = f"{answer}\n\nSources:\n"
            # Extract chunk details from source_docs as needed
            for doc in source_docs:
                detailed_answer += f"\n-{doc.metadata['source']}"
            return detailed_answer
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            raise

    async def get_answer_stream(self, question: str, conversation_history: List[Dict] = None) -> AsyncGenerator[str, None]:
        """
        Get an answer to the given question using the streaming chain.

        :param question: The question to be answered.
        :param conversation_history: List of previous interactions.
        :return: An async generator yielding chunks of the answer.
        """
        try:
            chat_history = ""
            if conversation_history:
                chat_history = self._format_chat_history(conversation_history)

            context = f"""Previous conversation:{chat_history}

Current question: {question}

Instructions:
- Answer using ONLY the information found in the provided documents and previous conversations.
- Make sure that the answer is accurate and is very detailed.
- Do not include any external knowledge or assumptions.
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
