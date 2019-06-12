# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:start_server
   Author:djh
   date:19-5-6
-------------------------------------------------
   Change Activity:18-4-25:
-------------------------------------------------
"""
import sys
import re
import json
from tqdm import tqdm
from pymongo import MongoClient
from flask import Flask, request, render_template, jsonify, app
import kg
import triples

app = Flask(__name__)

################################### Index ############################
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

################################### Triples ##########################
@app.route('/triples')
def triple():
    return render_template('triples.html')


@app.route('/triples/query_all', methods=['POST'])
def query_all():
    dbtype = request.form.get('dbtype')
    result = triples.query_all(dbtype)
    return jsonify(result), 200


@app.route('/triples/query_by_node', methods=['POST'])
def query_by_node():
    e1_name = request.form.get('e1').strip().lower()
    e2_name = request.form.get('e2').strip().lower()
    dbtype = request.form.get('dbtype')
    result = triples.query_by_node(e1_name, e2_name, dbtype)
    return jsonify(result), 200
################################### Knowledge #########################
@app.route('/kg')
def kg_index():
    return render_template('kg_index.html')


@app.route('/kg/file/<filepath>', methods=['GET'])
def kg_init(filepath):
    print('filepath = {}'.format(filepath))
    return app.send_static_file(filepath)


@app.route('/kg/query_by_kid', methods=['GET'])
def query_by_kid():
    kid = request.args.get('kid').strip().lower()
    person_list, organ_list = kg.query_by_kid(kid)
    return render_template('kg_result.html', person_list=person_list, organ_list=organ_list)


@app.route('/kg/query_by_keyword', methods=['GET'])
def query_by_keyword():
    keyword = request.args.get('keyword').strip().lower()
    person_list, organ_list = kg.query_by_keyword(keyword)
    return render_template('kg_result.html', person_list=person_list, organ_list=organ_list)


@app.route('/kg/json/query_by_kid', methods=['GET'])
def query_by_kid_json():
    kid = request.args.get('kid').strip().lower()
    person_list, organ_list = kg.query_by_kid(kid)
    return jsonify({'person_list': person_list, 'organ_list': organ_list}), 200


@app.route('/kg/json/query_person_by_id', methods=['GET', 'POST'])
def query_person_by_id_json():
    pid = request.form.get('pid').strip().lower()
    e = kg.query_person_by_id(pid)
    return jsonify(e), 200


@app.route('/kg/json/query_organ_by_id', methods=['GET', 'POST'])
def query_organ_by_id_json():
    oid = request.form.get('oid').strip().lower()
    e = kg.query_organ_by_id(oid)
    return jsonify(e), 200


@app.route('/kg/json/query_person_by_name', methods=['GET', 'POST'])
def query_person_by_name_json():
    name = request.args.get('name').strip().lower()
    es = kg.query_person_by_name(name)
    return jsonify(es), 200


@app.route('/kg/json/query_organ_by_name', methods=['GET', 'POST'])
def query_organ_by_name_json():
    name = request.args.get('name').strip().lower()
    es = kg.query_organ_by_name(name)
    return jsonify(es), 200


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
