from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from chromadb.config import Settings
from pydantic_settings import BaseSettings
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """
    A class to manage the creation and loading of a sector using Chroma and HuggingFace embeddings.
    """
    def __init__(self, persist_directory: str):
        """
        Initialize the VectorStore with a directory to persist the vector data.

        :param persist_directory: Directory to store the vector data.
        """
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None

    def create_vector_store(self, documents):
        """
        Create a vector store from the provided documents.

        :param documents: List of documents to be embedded and stored.
        :return: The created vector store.
        """
        try:
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name="my_collection",
                client_settings=Settings(anonymized_telemetry=False)
            )
            logger.info("Vector store created successfully")
            return self.vector_store
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise

    def load_vector_store(self):
        """
        Load the vector store from the persistant directory.

        :return: The loaded vector store.
        """
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="my_collection",
                client_settings=Settings(anonymized_telemetry=False)
            )
            logger.info("Vector store loaded successfully")
            return self.vector_store
        except Exception as e:
            if "no such column: collections.topic" in str(e):
                logger.warning("Schema mismatch detected, removing old vector DB...")
                if os.path.exists(self.persist_directory):
                    # Remove old DB
                    for filename in os.listdir(self.persist_directory):
                        file_path = os.path.join(self.persist_directory, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                # Recreate
                return self.create_vector_store([])
            logger.error(f"Error loading vector store: {str(e)}")
            raise
