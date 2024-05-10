class BaseLoader:
  def __init__(self, content):
    self.content = content

  def load(self):
    raise NotImplementedError('load method must be implemented by subclass')
