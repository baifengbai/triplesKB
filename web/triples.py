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

def query_all(dbtype):
    entities, triples = query_all_triples_of_mongodb(dbtype)
    return {'entities': entities, 'triples': triples}


def query_all_triples_of_mongodb(dbtype):
    entities = []
    triples = []
    table = kg_db[dbtype]
    result = table.find({}).limit(300)  # 限制显示

    category_map = {
        'key_key': (0, 0),
        'per_key': (1, 0),
        'org_key': (2, 0),
        'per_org': (1, 2),
    }

    e1_type, e2_type = category_map[dbtype]

    if dbtype == 'key_key':
        e1_table = kg_db['keyword']
        e2_table = kg_db['keyword']
    if dbtype == 'per_key':
        e1_table = kg_db['person']
        e2_table = kg_db['keyword']
    if dbtype == 'org_key':
        e1_table = kg_db['organ']
        e2_table = kg_db['keyword']
    if dbtype == 'per_org':
        e1_table = kg_db['person']
        e2_table = kg_db['organ']

    for rst in tqdm(result):
        e1_id, rel, e2_id = rst['e1'], rst['rel'], rst['e2']
        dct = {}
        try:
            dct['e1'] = e1_table.find_one({'_id': str(e1_id)})
            dct['e2'] = e2_table.find_one({'_id': str(e2_id)})
            if dct['e1'] is None or dct['e2'] is None:
                print('None')
                continue
            dct['e1'] = {'name': dct['e1']['name'], 'category': e1_type}
            dct['e2'] = {'name': dct['e2']['name'], 'category': e2_type}
            dct['rel'] = rel
        except Exception as e:
            print(e)
            continue
        if dct['e1'] not in entities:
            entities.append(dct['e1'])  # {'name':'小明','category':0}
        if dct['e2'] not in entities:
            entities.append(dct['e2'])
        triples.append(dct)
    # 对triples后处理 #{ 'e1': 0, 'rel': 'like1', 'e2': 1 }
    for i in range(len(triples)):
        tpl = triples[i]
        tpl['e1'] = entities.index(tpl['e1'])
        tpl['e2'] = entities.index(tpl['e2'])
        triples[i] = tpl
    return entities, triples


def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def query_by_node(e1_name,e2_name,dbtype):
    if e1_name != '' and e2_name != '':
        entities, triples = query_by_e1_e2(e1_name, e2_name, dbtype)
    elif e1_name != '':
        entities, triples = query_by_e1(e1_name, dbtype)
    else:
        entities, triples = query_by_e2(e2_name, dbtype)
    return {'entities': entities[:300], 'triples': triples[:400]}


def query_by_e1(name, dbtype):
    print('query_by_e1,name = '+name+','+dbtype)
    entities = []
    triples = []
    category_map = {
        'key_key': (0, 0),
        'per_key': (1, 0),
        'org_key': (2, 0),
        'per_org': (1, 2),
    }
    e1_type, e2_type = category_map[dbtype]
    table = kg_db[dbtype]

    if dbtype == 'key_key':
        e1_table = kg_db['keyword']
        e2_table = kg_db['keyword']
        if check_contain_chinese(name):
            e1_s = e1_table.find({'chinese': re.compile(name)})
        else:
            e1_s = e1_table.find({'english': re.compile(name)})
    if dbtype == 'per_key':
        e1_table = kg_db['person']
        e2_table = kg_db['keyword']
        e1_s = e1_table.find({'name': re.compile(name)})
    if dbtype == 'org_key':
        e1_table = kg_db['organ']
        e2_table = kg_db['keyword']
        if check_contain_chinese(name):
            e1_s = e1_table.find({'中文名': re.compile(name)})
        else:
            e1_s = e1_table.find({'name': re.compile(name)})
    if dbtype == 'per_org':
        e1_table = kg_db['person']
        e2_table = kg_db['organ']
        e1_s = e1_table.find({'name': re.compile(name)})

    # 截取部分
    e1_s = [t for t in e1_s]
    print(len(e1_s))

    for e1 in e1_s:
        result = table.find({'e1': e1['_id']})
        if len(triples) > 500:
            print('>500 break')
            break
        for rst in result:
            if len(triples) > 500:
                print('>500 break')
                break
            e1_id, rel, e2_id = rst['e1'], rst['rel'], rst['e2']
            dct = {}
            try:
                dct['e1'] = e1_table.find_one({'_id': str(e1_id)})
                dct['e2'] = e2_table.find_one({'_id': str(e2_id)})
                if dct['e1'] is None or dct['e2'] is None:
                    print('None')
                    continue
                dct['e1'] = {'name': dct['e1']['name'], 'category': e1_type}
                dct['e2'] = {'name': dct['e2']['name'], 'category': e2_type}
                dct['rel'] = rel
            except Exception as e:
                print('error none')
                continue
            if dct['e1'] not in entities:
                entities.append(dct['e1'])  # {'name':'小明','category':0}
            if dct['e2'] not in entities:
                entities.append(dct['e2'])
            triples.append(dct)
    # 对triples后处理 #{ 'e1': 0, 'rel': 'like1', 'e2': 1 }
    for i in range(len(triples)):
        tpl = triples[i]
        tpl['e1'] = entities.index(tpl['e1'])
        tpl['e2'] = entities.index(tpl['e2'])
        triples[i] = tpl
    return entities, triples


def query_by_e2(name, dbtype):
    print('query_by_e2,name = '+name+','+dbtype)
    entities = []
    triples = []
    category_map = {
        'key_key': (0, 0),
        'per_key': (1, 0),
        'org_key': (2, 0),
        'per_org': (1, 2),
    }
    e1_type, e2_type = category_map[dbtype]
    table = kg_db[dbtype]

    if dbtype == 'key_key':
        e1_table = kg_db['keyword']
        e2_table = kg_db['keyword']
        if check_contain_chinese(name):
            e2_s = e2_table.find({'chinese': re.compile(name)})
        else:
            e2_s = e2_table.find({'english': re.compile(name)})
    if dbtype == 'per_key':
        e1_table = kg_db['person']
        e2_table = kg_db['keyword']
        if check_contain_chinese(name):
            e2_s = e2_table.find({'chinese': re.compile(name)})
        else:
            e2_s = e2_table.find({'english': re.compile(name)})
    if dbtype == 'org_key':
        e1_table = kg_db['organ']
        e2_table = kg_db['keyword']
        if check_contain_chinese(name):
            e2_s = e2_table.find({'chinese': re.compile(name)})
        else:
            e2_s = e2_table.find({'english': re.compile(name)})
    if dbtype == 'per_org':
        e1_table = kg_db['person']
        e2_table = kg_db['organ']
        if check_contain_chinese(name):
            e2_s = e2_table.find({'中文名': re.compile(name)})
        else:
            e2_s = e2_table.find({'name': re.compile(name)})

    # 截取部分
    e2_s = [t for t in e2_s]
    print(len(e2_s))

    for e2 in e2_s:
        result = table.find({'e2': e2['_id']})
        if len(triples) > 500:
            print('>500 break')
            break
        for rst in result:
            if len(triples) > 500:
                print('>500 break')
                break
            e1_id, rel, e2_id = rst['e1'], rst['rel'], rst['e2']
            dct = {}
            try:
                dct['e1'] = e1_table.find_one({'_id': str(e1_id)})
                dct['e2'] = e2_table.find_one({'_id': str(e2_id)})
                if dct['e1'] is None or dct['e2'] is None:
                    print('None')
                    continue
                dct['e1'] = {'name': dct['e1']['name'], 'category': e1_type}
                dct['e2'] = {'name': dct['e2']['name'], 'category': e2_type}
                dct['rel'] = rel
            except Exception as e:
                print(e)
                continue
            if dct['e1'] not in entities:
                entities.append(dct['e1'])  # {'name':'小明','category':0}
            if dct['e2'] not in entities:
                entities.append(dct['e2'])
            triples.append(dct)
    # 对triples后处理 #{ 'e1': 0, 'rel': 'like1', 'e2': 1 }
    for i in range(len(triples)):
        tpl = triples[i]
        tpl['e1'] = entities.index(tpl['e1'])
        tpl['e2'] = entities.index(tpl['e2'])
        triples[i] = tpl
    return entities, triples


def query_by_e1_e2(e1_name, e2_name, dbtype):
    print('query_by_e1_e2, e1='+e1_name+', e2='+e2_name+','+dbtype)
    entities = []
    triples = []

    category_map = {
        'key_key': (0, 0),
        'per_key': (1, 0),
        'org_key': (2, 0),
        'per_org': (1, 2),
    }

    e1_type, e2_type = category_map[dbtype]
    table = kg_db[dbtype]

    if dbtype == 'key_key':
        e1_table = kg_db['keyword']
        e2_table = kg_db['keyword']
        if check_contain_chinese(e1_name):
            e1_s = e1_table.find({'chinese': re.compile(e1_name)})
        else:
            e1_s = e1_table.find({'english': re.compile(e1_name)})
        if check_contain_chinese(e2_name):
            e2_s = e2_table.find({'chinese': re.compile(e2_name)})
        else:
            e2_s = e2_table.find({'english': re.compile(e2_name)})
    if dbtype == 'per_key':
        e1_table = kg_db['person']
        e2_table = kg_db['keyword']
        e1_s = e1_table.find({'name': re.compile(e1_name)})
        if check_contain_chinese(e2_name):
            e2_s = e2_table.find({'chinese': re.compile(e2_name)})
        else:
            e2_s = e2_table.find({'english': re.compile(e2_name)})
    if dbtype == 'org_key':
        e1_table = kg_db['organ']
        e2_table = kg_db['keyword']
        if check_contain_chinese(e1_name):
            e1_s = e1_table.find({'中文名': re.compile(e1_name)})
        else:
            e1_s = e1_table.find({'name': re.compile(e1_name)})
        if check_contain_chinese(e2_name):
            e2_s = e2_table.find({'chinese': re.compile(e2_name)})
        else:
            e2_s = e2_table.find({'english': re.compile(e2_name)})
    if dbtype == 'per_org':
        e1_table = kg_db['person']
        e2_table = kg_db['organ']
        e1_s = e1_table.find({'name': re.compile(e1_name)})
        if check_contain_chinese(e2_name):
            e2_s = e2_table.find({'中文名': re.compile(e2_name)})
        else:
            e2_s = e2_table.find({'name': re.compile(e2_name)})

    e1_s = [t for t in e1_s]
    e2_s = [t for t in e2_s]

    for i in range(len(e1_s)):
        if len(triples) > 400:
            print('>400 break')
            break
        for j in range(len(e2_s)):
            e1 = e1_s[i]
            e2 = e2_s[j]
            result = table.find({'e1': e1['_id'], 'e2': e2['_id']})

            for rst in result:
                if len(triples) > 400:
                    print('>400 break')
                    break
                e1_id, rel, e2_id = rst['e1'], rst['rel'], rst['e2']
                dct = {}
                try:
                    dct['e1'] = e1_table.find_one({'_id': str(e1_id)})
                    dct['e2'] = e2_table.find_one({'_id': str(e2_id)})
                    if dct['e1'] is None or dct['e2'] is None:
                        print('None')
                        continue
                    dct['e1'] = {'name': dct['e1']
                                 ['name'], 'category': e1_type}
                    dct['e2'] = {'name': dct['e2']
                                 ['name'], 'category': e2_type}
                    dct['rel'] = rel
                except Exception as e:
                    print(e)
                    continue
                if dct['e1'] not in entities:
                    entities.append(dct['e1'])  # {'name':'小明','category':0}
                if dct['e2'] not in entities:
                    entities.append(dct['e2'])
                triples.append(dct)

    # 对triples后处理 #{ 'e1': 0, 'rel': 'like1', 'e2': 1 }
    for i in range(len(triples)):
        tpl = triples[i]
        tpl['e1'] = entities.index(tpl['e1'])
        tpl['e2'] = entities.index(tpl['e2'])
        triples[i] = tpl

    return entities, triples
