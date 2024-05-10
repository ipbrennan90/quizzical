from . import api_blueprint
from flask import request, jsonify

from app.services.resource_loader import ResourceLoader


@api_blueprint.route('/', methods=['GET'])
def handle_query():
    loader = ResourceLoader(url = 'https://www.uen.org/emedia/resources/oer/6thGradeSEEd.pdf')
    print(loader.to_text())
    return jsonify({ "data": "hello world" })
