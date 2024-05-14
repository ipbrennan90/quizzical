import os
import secrets

import redis
from typing import Any



class Session():
  def __init__(self, session_id, client = redis.from_url(os.getenv("REDIS_URL"))):
    self.session_client =  client
    self.session_id = session_id or secrets.token_hex(16)
    self.user_session()

  def user_session(self):
    (new_session, new_session_id) = self.check_for_new_session(self.session_id)

    if new_session:
      self.__delete(self.session_id)
      self.__delete(f'#{self.session_id}-new')
      self.session_id = new_session_id

    active_session = self.__get_map(self.session_id)
    if not active_session:
      self.__set_map(self.session_id, { "mode": 'tutor', "quiz_topic": "None", "question_count": 0, "id": self.session_id})
      active_session = self.__get_map(self.session_id)

    self.session = active_session

  def check_for_new_session(self, session_id):
    new_session_id = self.__get(f'#{session_id}-new')
    if new_session_id:
      return (True, new_session_id)
    else:
      return (False, None)

  def new_session(self, mode, quiz_topic=""):
    new_session_id = secrets.token_hex(16)
    self.__set_map(new_session_id, { "mode": mode, "quiz_topic": quiz_topic, "question_count": 0, "id": new_session_id})
    self.__set(f'#{self.session_id}-new', new_session_id)
    self.session_id = new_session_id
    self.session = self.__get_map(new_session_id)

  def update_session(self, session: dict[str, Any]):
    active_session = self.session or self.__get_map(self.session_id)

    self.__set_map(self.session_id, {**active_session, **session})
    self.session = self.__get_map(self.session_id)

  def __set_map(self, key, value: dict[str, Any]):
    self.session_client.hset(key, mapping=value)

  def __get_map(self, key) -> dict[str, Any]:
    byte_mapping = self.session_client.hgetall(key)
    return eval(str(byte_mapping).replace("b'", "'"))

  def __set(self, key, value):
    self.session_client.set(key, value)

  def __get(self, key):
    return self.session_client.get(key)

  def __delete(self, key):
    self.session_client.delete(key)