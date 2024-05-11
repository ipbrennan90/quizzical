from . import api_blueprint
from flask import request, jsonify

from app.services.resource_loader import ResourceLoader
from app.services.embeddings import Embeddings
from app.services.vector_store import VectorStore

from flask import g

@api_blueprint.route('/', methods=['GET'])
def handle_query():
    loader = ResourceLoader(url = 'https://www.uen.org/emedia/resources/oer/6thGradeSEEd.pdf')
    docs = loader.to_text()
    embeddings = Embeddings()
    vector_store = embeddings.embed(docs)
    return jsonify({ "data": "hello world" })

@api_blueprint.route('/search', methods=['GET'])
def search():
    vector_store = VectorStore(namespace="1")
    return jsonify({"data": "searching..."})