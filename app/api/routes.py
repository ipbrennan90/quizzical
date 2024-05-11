from . import api_blueprint
from flask import request, jsonify
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from operator import itemgetter
from langchain.schema import StrOutputParser

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

@api_blueprint.route('/query', methods=['POST'])
def search():
    request_data = request.get_json()
    query = request_data.get('query')
    namespace = request_data.get('namespace')
    character = request_data.get('character')
    prompt_to_use = prompt(character)
    vector_store = VectorStore(namespace=namespace)
    retriever = vector_store.retriever()
    prompt_template = ChatPromptTemplate.from_template(prompt_to_use)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, streaming=True)
    retrieval_augmented_chain = { "context": itemgetter("question") | retriever, "question": itemgetter("question") } | prompt_template | llm | StrOutputParser()
    response = retrieval_augmented_chain.invoke({"question": query})

    return jsonify({ "data": response, "status": { "code": 200, "message": "success"}})







    return jsonify({"data": "searching..."})