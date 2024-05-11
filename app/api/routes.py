from . import api_blueprint
from flask import request, jsonify
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
    query = request_data.get('question')
    namespace = request_data.get('namespace')
    character = request_data.get('character')
    chat_session_id = request_data.get('chat_session_id')
    prompt_to_use = prompt(character)
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

    response = chain_with_history.invoke({"question": query}, config=config)

    return jsonify({ "data": response, "status": { "code": 200, "message": "success"}})