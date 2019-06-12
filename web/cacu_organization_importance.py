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
import json
from tqdm import tqdm
from pymongo import MongoClient

client = MongoClient("mongodb://10.108.17.25:27017/")
kg_db = client['kg']


if __name__ == "__main__":
    organ_table = kg_db['organ']
    organ_dct = {}
    organ_list = [o for o in organ_table.find({})]
    for t in organ_list:
        organ_dct[t['_id']] = len(t.keys())

    for o in organ_list:
        for i in ['university', 'technology', 'school', 'army', 'space', 'college', 'institute', 'navy']:
            if o['name'].find(i) != -1:
                organ_dct[o['_id']] += 500

    per_org_table = kg_db['per_org']
    tpls = per_org_table.find({})
    for tpl in tpls:
        organ_dct[tpl['e2']] += 1

    json.dump(organ_dct, open('organ_import.json', 'w'))
