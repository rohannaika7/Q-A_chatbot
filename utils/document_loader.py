from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import os
from typing import List
from langchain.docstore.document import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    A class to process documents by loading and splitting them into chunks.
    """
    def __init__(self, directory_path: str):
        """
        Initialize the DocumentProcessor with a directory path.

        :param directory_path: Path to the directory containing documents.
        """
        self.directory_path = directory_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators='# ',
            chunk_overlap=500,
            length_function=len
        )

    def load_documents(self):
        """
        Load documents from the specified directory.

        :return: List of loaded documents.
        """
        try:
            loader = DirectoryLoader(
                self.directory_path,
                glob="**/*.md",
                loader_cls=lambda path: TextLoader(path, encoding="utf-8")
            )
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise

    def split_documents(self, documents):
        """
        Split the loaded documents into chunks.

        :param documents: List of documents to be split.
        :return: List of document chunks.
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise
