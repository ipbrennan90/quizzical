import requests
from app.models.loaders.pdf import PdfLoader
from app.models.loaders.website import WebsiteLoader

class ResourceLoader:
    def __init__(self, url):
        self.url = url
        self.__load()

    def to_text(self):
      loader = self.__loader()
      return loader.load()


    def __file_type(self, response):
      content_type = response.headers.get('content-type')
      file_extension = 'unknown'
      if 'application/pdf' in content_type:
        file_extension = 'pdf'
      elif 'text/html' in content_type:
        file_extension = 'html'

      if file_extension == 'unknown':
        raise ValueError('Unknown file type')

      return file_extension

    def __loader(self):
      if self.file_type == 'pdf':
        return PdfLoader(self.url)
      else:
        return WebsiteLoader(self.url)

    def __load(self):
      response = requests.get(self.url)
      file_type = self.__file_type(response)

      print(f'Loaded {self.url} with content type {file_type}')

      self.loaded_content = response.content
      self.file_type = file_type


