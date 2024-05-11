from langchain_experimental.text_splitter import SemanticChunker# Responsible for embedding the input text using a pre-trained embedding model
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
import os

from app.services.vector_store import VectorStore
class Embeddings:
  def __init__(self, text_splitter = SemanticChunker(OpenAIEmbeddings()), embedding_model= OpenAIEmbeddings(model="text-embedding-3-small")):
    self.text_splitter = text_splitter
    self.embedding_model = embedding_model

  def embed(self, docs, embeddings_name="1"):
    chunks = self.__split_docs(docs)
    self.vector_store = VectorStore(embeddings_name)
    self.vector_store.load(chunks)
    return self.vector_store


  def __split_docs(self, docs):
    return self.text_splitter.split_documents(docs)
