from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import os

class VectorStore:
  def __init__(self, namespace, client=PineconeVectorStore):
    self.store_client = client
    self.namespace = namespace
    self.store = None
    self.__store()


  def retriever(self):
    return self.store.as_retriever()

  def load(self, docs):
    self.store.add_documents(docs)

  def __store(self):
    if self.store is None:
      self.store = self.store_client(index_name="quizzi", embedding=OpenAIEmbeddings(model="text-embedding-3-small"), namespace=self.namespace, pinecone_api_key=os.getenv("PINECONE_API_KEY"))


