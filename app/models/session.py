import os
import redis
from typing import Any


class Session():
  def __init__(self, session_id, client = redis.from_url(os.getenv("REDIS_URL"))):
    self.session_client =  client
    self.session_id = session_id
    self.user_session()

  def user_session(self):
    active_session = self.__get_map(self.session_id)
    if not active_session:
      self.__set_map(self.session_id, { "mode": 'tutor', "quiz_topic": "None", "question_count": 0})
      active_session = self.__get_map(self.session_id)

    self.session = active_session

  def update_session(self, session: dict[str, Any]):
    active_session = self.session or self.__get_map(self.session_id)

    self.__set_map(self.session_id, {**active_session, **session})
    self.session = self.__get_map(self.session_id)

  def __set_map(self, key, value: dict[str, Any]):
    self.session_client.hset(key, mapping=value)

  def __get_map(self, key) -> dict[str, Any]:
    byte_mapping = self.session_client.hgetall(key)
    return eval(str(byte_mapping).replace("b'", "'"))
