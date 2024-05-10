from .base import BaseLoader
from langchain_community.document_loaders import PyMuPDFLoader

class PdfLoader(BaseLoader):
    def __init__(self, content):
        self.content = content

    def load(self) -> str:
      return PyMuPDFLoader(self.content).load()