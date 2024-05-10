from .base import BaseLoader
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer

class WebsiteLoader(BaseLoader):
  def load(self):
    loader = AsyncHtmlLoader(self.content)
    html = loader.load()

    transformer = Html2TextTransformer()
    docs = transformer.transform_documents(html)
    return docs



