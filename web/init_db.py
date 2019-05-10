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

import os
import json
import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient
from py2neo import Graph, Node, Relationship
import re

########################################################################
def init_mongodb():
    '''
    初始化Mongodb
    '''
    keyword_table = kg_db['keyword']
    person_table = kg_db['person']
    organ_table = kg_db['organ']
    key_key_table = kg_db['key_key']
    per_key_table = kg_db['per_key']
    org_key_table = kg_db['org_key']
    per_org_table = kg_db['per_org']

    print('clean table ...')
    # keyword_table.drop()
    # person_table.drop()
    # organ_table.drop()
    # key_key_table.drop()
    per_key_table.drop()
    # org_key_table.drop()
    # per_org_table.drop()

    # print('create keywords ...')
    # f = os.path.join('data', 'fields_dict.json')
    # dct = json.load(open(f, 'r'))
    # for i, u in tqdm(dct.items()):
    #     u['_id'] = u['id']  # 重定义id
    #     u.pop('id')
    #     u['name'] = u['name'].strip().lower()
    #     try:
    #         keyword_table.insert(u)
    #     except Exception as e:
    #         print(e)
    #         break
    # print('create organs ...')
    # en_attrs = ['name', 'country', 'commanders', 'branch', 'location', 'headquarters', 'president', 'established', 'postgraduates', 'party secretary', 'undergraduates', 'website', 'location', 'type', 'affiliations', 'flower', 'colors', 'motto', 'administrative staff', 'students', 'campus', 'mascot', 'academic staff', 'type', 'child agencies', 'annual budget', 'website', 'employees']

    # zh_attrs = ['博士点', '类别', '专职院士', '博士后', '院校代码', '外文名', '校庆日', '知名校友', '创办时间', '地址', '简称', '中文名', '主要奖项', '主管部门', '院系设置', '硕士点', '本科专业', '校训',
    #             '属性', '现任领导', '校歌', '国家重点学科', '类型', '别称', '学校代码', '学校类型', '学校地址', '现任校长', '所属地区', '主要院系', '博士后流动站', '学校类别', '学校属性']

    # f = os.path.join('data', 'organs_dict.json')
    # dct = json.load(open(f, 'r'))
    # for i, u in tqdm(dct.items()):
    #     t = {}
    #     t['_id'] = str(i)
    #     for k, v in u.items():
    #         v = u[k]
    #         k = k.strip().lower()
    #         if k not in en_attrs+zh_attrs:
    #             continue
    #         k = k.replace('.', '')
    #         k = k.lower()
    #         if v == '':
    #             continue
    #         t[k] = v
    #     try:
    #         t['name'] = t['name'].strip().lower()
    #         organ_table.insert(t)
    #     except Exception as e:
    #         print(e)
    #         break
    
    # print('create persons ...')
    # f = os.path.join('data', 'persons_dict.json')
    # dct = json.load(open(f, 'r'))
    # for i, u in tqdm(dct.items()):
    #     u['_id'] = str(i)
    #     u['name'] = u['name'].strip().lower()
    #     try:
    #         person_table.insert(u)
    #     except Exception as e:
    #         print(e)
    #         break
    
    # print('create key_key_table ...')
    # rel_map = {0: '等于', 1: '上级', 2: '下级', 3: '同领域'}
    # df = pd.read_csv(os.path.join('data', 'key_key_rel.csv'), delimiter='##')
    # triples = df[df['relation'] != -1].values.tolist()
    # insert_triples(triples, key_key_table, rel_map)

    print('create per_key_table ...')
    rel_map = {1: '属于'}
    df = pd.read_csv(os.path.join('data', 'per_key_rel.csv'), delimiter='##')
    triples = df[df['relation'] != -1].values.tolist()
    insert_triples(triples, per_key_table, rel_map)

    # print('create org_key_table ...')
    # df = pd.read_csv(os.path.join('data', 'org_key_rel.csv'), delimiter='##')
    # triples = df[df['relation'] != -1].values.tolist()
    # insert_triples(triples, org_key_table, rel_map)

    # print('create per_org_table ...')
    # df = pd.read_csv(os.path.join('data', 'per_org_rel.csv'), delimiter='##')
    # triples = df[df['relation'] != -1].values.tolist()
    # insert_triples(triples, per_org_table, rel_map)


def insert_triples(triples, table, rel_map):
    '''
    triple={'e1':value,'e2':value,'rel':value}
    '''
    for triple in tqdm(triples):
        e1 = triple[0]
        e2 = triple[1]
        rel = triple[2]
        rel = rel_map[rel]

        doc = {}
        doc['e1'], doc['rel'], doc['e2'] = str(e1), rel, str(e2)
        try:
            table.insert(doc)
        except Exception as e:
            print(e)
            break

########################################################################


def init_neo4j():
    # create_keyword()
    # create_organ()
    # create_person()
    # key_key relation
    # per_key relation
    # org_key relation
    # per_org relation
    pass


def create_key_key():
    # CREATE (le)-[:KNOWS {since:1768}]->(db)
    pass


def create_keyword():
    # fields nodes
    f = os.path.join('data', 'fields_dict.json')
    dct = json.load(open(f, 'r'))
    print('create keywords ...')
    for _, u in tqdm(dct.items()):
        cypher = 'CREATE (x:Keyword '
        cypher += "{"
        for k, v in u.items():
            k = k.strip()
            if isinstance(v, int):
                cypher += "{}:{}, ".format(k, v)
            else:
                cypher += '{}:"{}", '.format(k, v)
        if cypher[-2] == ',':
            cypher = cypher[:-2]
        cypher += "})"
        graph.run(cypher)


def create_person():
    # person nodes
    f = os.path.join('data', 'persons_dict.json')
    dct = json.load(open(f, 'r'))
    print('create persons ...')
    for i, u in tqdm(dct.items()):
        cypher = 'CREATE (x:Person '
        cypher += "{"
        cypher += "id:{}, ".format(i)
        for k, v in u.items():
            k = k.strip()
            if k not in ['aff', 'name', 'tags', 'attr']:
                continue
            if v == {} or k == 'indices':
                continue
            if isinstance(v, str) and v.strip() == '':
                continue
            elif isinstance(v, int) or isinstance(v, list):
                cypher += "{}:{}, ".format(k, v)
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, str) and vv.strip() == '':
                        continue
                    cypher += '{}:"{}", '.format(kk, vv)
            else:
                v = v.replace('"', '')
                cypher += '{}:"{}", '.format(k, v)
        if cypher[-2] == ',':
            cypher = cypher[:-2]
        cypher += "})"
        try:
            graph.run(cypher)
        except Exception as e:
            continue


def create_organ():
    # organization nodes
    f = os.path.join('data', 'organs_dict.json')
    dct = json.load(open(f, 'r'))
    print('create organs ...')
    for i, u in tqdm(dct.items()):
        cypher = 'CREATE (x:Organization '
        cypher += "{"
        cypher += "id:{}, ".format(i)
        for k, v in u.items():
            if k.strip() not in ['Name', 'Country', "Commanders", "Branch", 'Location', 'Headquarters', 'Type', 'Child agencies', 'Annual budget', 'Website', 'Employees']:
                continue
            k = k.strip()
            k = re.sub(r"[' ]", '', k)

            if v == {}:
                continue
            if isinstance(v, str) and v.strip() == '':
                continue
            elif isinstance(v, int) or isinstance(v, list):
                cypher += "{}:{}, ".format(k, v)
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    cypher += '{}:"{}", '.format(kk, vv)
                cypher = cypher[:-2]
            else:
                v = v.replace('"', '')
                cypher += '{}:"{}", '.format(k, v)
        if cypher[-2] == ',':
            cypher = cypher[:-2]
        cypher += "})"
        try:
            graph.run(cypher)
        except Exception as e:
            continue


def clean_neo4j():
    statement = '''match(n) optional match(n)-[r]-() delete n,r'''
    graph.run(statement)
########################################################################


if __name__ == '__main__':
    # graph = Graph('http://10.108.17.25:7474/db/data',username='neo4j', password='1216')
    client = MongoClient("mongodb://10.108.17.25:27017/")
    kg_db = client['kg']
    init_mongodb()
