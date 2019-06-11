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

print('connecting "mongodb://10.108.17.25:27017/"')
client = MongoClient("mongodb://10.108.17.25:27017/")
kg_db = client['kg']

organ_import_dct = json.load(open('organ_import.json', 'r'))


def query_person_by_id(pid):
    table = kg_db['person']
    e = table.find_one({'_id': pid})
    return e


def query_organ_by_id(oid):
    table = kg_db['organ']
    e = table.find_one({'_id': oid})
    return e


def query_by_kid(kid):
    print('kid = {}'.format(kid))
    person_list = query_per_by_kid(kid)
    organ_list = query_org_by_kid(kid)
    if organ_list == []:
        organ_list = [{'name': p['aff']} for p in person_list]
    return person_list, organ_list


def query_by_keyword(key):
    print('key = {}'.format(key))
    person_list, organ_list = [], []
    key_ids = [k['_id']
               for k in kg_db['keyword'].find({'english': re.compile(key)})]
    for kid in key_ids:
        ps, os = query_by_kid(kid)
        person_list.extend(ps)
        organ_list.extend(os)
        if len(organ_list) > 100 or len(person_list) > 100:
            break
    person_list.sort(key=person_importance, reverse=True)
    organ_list.sort(key=organ_importance, reverse=True)
    return person_list[:50], organ_list[:50]


def query_person_by_name(name):
    es = [e for e in kg_db['person'].find({'name': re.compile(name)})][:50]
    return es


def query_organ_by_name(name):
    es = [e for e in kg_db['organ'].find({'name': re.compile(name)})][:50]
    return es


def person_importance(e):
    num_attrs = len(e.keys())
    indices = e.get('indices', {})
    indices = 0 if indices == {} else indices.get('h_index', 1)
    num_contact = len(e.get('contact', []))
    num_tags = len(e.get('tags', []))*0.5
    return num_attrs+indices+num_contact+num_tags


def organ_importance(e):
    return organ_import_dct.get(e.get('_id', 1), 0)


def query_per_by_kid(kid):
    person_list = []
    table = kg_db['person']
    per_key_list = kg_db['per_key'].find(
        {'e2': re.compile('^{}'.format(kid))})  # 前缀匹配
    for tpl in per_key_list:
        e = table.find_one(tpl['e1'])
        # tmp = {}
        # tmp['name'] = e['name']
        # tmp['id'] = e['_id']
        # tmp['type'] = 'person'
        person_list.append(e)
    person_list.sort(key=person_importance, reverse=True)
    return person_list[:30]


def query_org_by_kid(kid):
    organ_list = []
    table = kg_db['organ']
    organ_key_list = kg_db['org_key'].find(
        {'e2': re.compile('^{}'.format(kid))})  # 前缀匹配
    for tpl in organ_key_list:
        e = table.find_one(tpl['e1'])
        # tmp = {}
        # tmp['name'] = e['name']
        # tmp['id'] = e['_id']
        # tmp['type'] = 'organ'
        organ_list.append(e)
    organ_list.sort(key=organ_importance, reverse=True)
    return organ_list[:30]


if __name__ == "__main__":
    kid = ['4.1.3.5.', '14.1.1.']
    print(query_by_kid(kid[0]))
