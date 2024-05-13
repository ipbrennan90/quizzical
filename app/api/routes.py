from . import api_blueprint
from flask import request, jsonify, Response
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import StrOutputParser

from operator import itemgetter
import os

from app.services.resource_loader import ResourceLoader
from app.services.embeddings import Embeddings
from app.services.vector_store import VectorStore
from app.models.prompts import prompt
from app.models.session import Session

def stream_chat(chain, query, config):
  for chunk in chain.stream(query, config):
    yield chunk

def end_quiz(session):
  session.update_session({ "mode": "tutor", "quiz_topic": "None", "question_count": 0})

def set_character(quiz_ended, character):
  if(quiz_ended):
    return character
  else:
    return f'{character}_quiz'

def quiz_over(session):
  if session.session["mode"] == "quiz" and int(session.session["question_count"]) >= 5:
    return True
  else:
    return False

@api_blueprint.route('/embed-resource', methods=['POST'])
def handle_query():
    request_data = request.get_json()
    url = request_data.get('url')
    namespace = request_data.get('namespace')
    loader = ResourceLoader(url = url)
    docs = loader.to_text()
    embeddings = Embeddings()
    embeddings.embed(docs, embeddings_name=namespace)


    return jsonify({ "data": { "namespace": namespace}, "status": { "code": 200, "message": "success"}})

@api_blueprint.route('/chat', methods=['POST'])
def chat():
  request_data = request.get_json()
  chat_session_id = request_data.get('chat_session_id')

  session = Session(chat_session_id)



  query = request_data.get('question')

  if "Quiz me on" in query:
      quiz_topic = query.split("Quiz me on ")[1]
      session.update_session({ "mode": "quiz", "quiz_topic": quiz_topic, "question_count": 0})

  quiz_ended = quiz_over(session)
  if quiz_ended:
    end_quiz(session)

  prompt_to_use = prompt(set_character(quiz_ended, request_data.get('character')))

  namespace = request_data.get('namespace')
  vector_store = VectorStore(namespace=namespace)
  retriever = vector_store.retriever()

  prompt_template = ChatPromptTemplate.from_messages([("system", prompt_to_use), MessagesPlaceholder(variable_name="history"), ("human", "{question}")])

  llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, streaming=True)

  get_context = itemgetter("question") | retriever
  first_step = RunnablePassthrough.assign(context=get_context)
  retrieval_augmented_chain = first_step | prompt_template | llm | StrOutputParser()

  chain_with_history = RunnableWithMessageHistory(
      retrieval_augmented_chain,
      lambda session_id: RedisChatMessageHistory(session_id, url=os.getenv("REDIS_URL")),
      input_messages_key="question",
      history_messages_key="history"
  )

  config = {"configurable": {"session_id": chat_session_id}}

  if session.session["mode"] == "quiz":
    return Response(stream_chat(chain_with_history, { "question": query, "concept": session.session["quiz_topic"] }, config), 200, {"Access-Control-Allow-Origin": "*"})
  else:
    return Response(stream_chat(chain_with_history, { "question": query }, config), 200, {"Access-Control-Allow-Origin": "*"})
