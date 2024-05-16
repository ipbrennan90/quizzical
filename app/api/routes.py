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

def start_quiz(session, quiz_topic):
  session.new_session("quiz", quiz_topic=quiz_topic)

def start_tutor(session):
  session.new_session("tutor")

def quiz_over(session):
  if session.session["mode"] == "quiz" and int(session.session["question_count"]) >= 5:
    return True
  else:
    return False

@api_blueprint.route('/configure', methods=['POST'])
def configure_chat():
  request_data = request.get_json()
  study_content_url = request_data.get('studyContent')
  study_content_name = request_data.get('studyContentName')

  namespace = study_content_name.lower().replace(" ", "-")
  loader = ResourceLoader(url = study_content_url)

  docs = loader.to_text()
  embeddings = Embeddings()
  embeddings.embed(docs, embeddings_name=namespace)

  return jsonify({ "data": { "namespace": namespace, "studyContentName": study_content_name}, "status": { "code": 200, "message": "success"}})

@api_blueprint.route('/session', methods=['POST'])
def check_session():
  request_data = request.get_json()
  chat_session_id = request_data.get('chat_session_id')
  session = Session(chat_session_id).session

  return jsonify({ "data": { "chat_session_id": session["id"] }, "status": { "code": 200, "message": "success"}})

@api_blueprint.route('/chat', methods=['POST'])
def chat():
  request_data = request.get_json()
  chat_session_id = request_data.get('chat_session_id')
  query = request_data.get('question')
  namespace = request_data.get('namespace')


  session = Session(chat_session_id)


  if "quiz me on" in query.lower():
    quiz_topic = query.lower().split("quiz me on ")[1]
    start_quiz(session, quiz_topic)

  if "stop quiz" in query.lower():
    start_tutor(session)

  if session.session["mode"] == "quiz" and quiz_over(session):
    start_tutor(session)


  prompt_to_use = prompt(session.session["mode"], request_data.get('character'))

  vector_store = VectorStore(namespace=namespace)
  retriever = vector_store.retriever()

  prompt_template = ChatPromptTemplate.from_messages([("system", prompt_to_use), MessagesPlaceholder(variable_name="history"), ("human", "{question}")])

  llm = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)

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
    session.update_session({ "question_count": int(session.session["question_count"]) + 1})

    return Response(stream_chat(chain_with_history, { "question": query, "concept": session.session["quiz_topic"] }, config), 200, {"Access-Control-Allow-Origin": "*"})
  else:
    return Response(stream_chat(chain_with_history, { "question": query }, config), 200, {"Access-Control-Allow-Origin": "*"})
