import json

import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

from antique_rest_api.antique_docs_service import get_query_result
from antique_rest_api.antique_indexing import get_query_relevant_docs, build_docs_index
from antique_rest_api.antique_lemmatize_text import get_lemmatize_texts
from antique_rest_api.antique_suggestions import get_suggestions, build_queries_index

search_app = Flask(__name__)
CORS(search_app, resources={r"/*": {"origins": "*"}})


@search_app.route('/search', methods=['POST'])
def search():
    data = json.loads(request.data)
    query = data['query']
    page = data['page']
    page_size = data['pageSize']
    payload = {
        "query": query,
        "page": page,
        "page_size": page_size
    }
    resp = requests.post("http://127.0.0.1:4000//lemmatizer", json=payload)
    return resp.text, resp.status_code, resp.headers.items()


@search_app.route('/lemmatizer', methods=['POST'])
def lemmatizer():
    data = json.loads(request.data)
    query = data['query']
    page = data['page']
    page_size = data['page_size']
    result = get_lemmatize_texts([query])[0]
    payload = {
        "query": result,
        "page": page,
        "page_size": page_size
    }
    resp = requests.post("http://127.0.0.1:4000//indexing", json=payload)
    return resp.text, resp.status_code, resp.headers.items()


@search_app.route('/indexing', methods=['POST'])
def indexing():
    data = json.loads(request.data)
    query = data['query']
    page = data['page']
    page_size = data['page_size']
    result = get_query_relevant_docs(query)
    payload = {
        "query": query,
        "page": page,
        "page_size": page_size,
        "related_docs": list(result)
    }
    resp = requests.post("http://127.0.0.1:4000//get_docs", json=payload)
    return resp.text, resp.status_code, resp.headers.items()


@search_app.route('/get_docs', methods=['POST'])
def get_docs():
    data = json.loads(request.data)
    query = data['query']
    page = data['page']
    page_size = data['page_size']
    related_docs = data['related_docs']
    result, total_count = get_query_result(query, related_docs, page, page_size)
    return make_response(jsonify({"result": result, "total_count": total_count}), 200)


@search_app.route('/get_suggestions', methods=['POST'])
def get_query_suggestions():
    data = json.loads(request.data)
    query = data['query']
    result = get_suggestions(query)
    return make_response(jsonify({"result": list(result)}), 200)


if __name__ == '__main__':
    build_docs_index()
    build_queries_index()
    search_app.run('localhost', 4000)
