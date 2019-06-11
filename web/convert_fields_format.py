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
from pprint import pprint
import json


keyword_vocab = json.load(open('fields_dict.json', 'r'))


def kid_to_kname(kid):
    return keyword_vocab.get(kid)['english']


def post_process(result):
    kid = result['name']
    if kid != 'keyword':
        result['name'] = kid_to_kname(kid)
    children = result['children']
    if children != []:
        tmp = []
        for c in children:
            tmp.append(post_process(c))
        result['children'] = tmp
    else:
        del result['children']
        result['value'] = kid
    return result


if __name__ == "__main__":
    keyword_ids = [l.strip().split('##')[0]
                   for l in open('fields_with_id.csv', 'r', encoding='utf-8')]
    level_map = {  # id对应的level
        2: 0,
        4: 1,
        5: 2,
        6: 3,
        7: 4,
        8: 5
    }
    levels = [[] for i in range(len(level_map))]  # idx对应的level

    for kid in keyword_ids:
        level = level_map[len(kid.split('.'))]
        levels[level].append(kid)

    result = {}
    result['name'] = 'keyword'
    result['children'] = []

    for zero in levels[0]:
        a = {}
        a['name'] = zero
        # a['value'] = zero # 防止级别过高,搜索太大
        a['children'] = []
        for second in levels[1]:
            b = {}
            b['name'] = second
            b['children'] = []
            # for third in levels[2]:
            #     c = {}
            #     c['name'] = third
            #     c['children'] = []
            # for fourth in levels[3]:
            #     d = {}
            #     d['name'] = fourth
            #     d['children'] = []
            #     for fifth in levels[4]:
            #         e = {}
            #         e['name'] = fifth
            #         e['children'] = []
            #         for sixth in levels[5]:
            #             f = {}
            #             f['name'] = sixth
            #             if sixth.startswith(fifth):
            #                 e['children'].append(f)
            #         if fifth.startswith(fourth):
            #             d['children'].append(e)
            # if fourth.startswith(third):
            #     c['children'].append(d)
            # if third.startswith(second):
            #     b['children'].append(c)
            if second.startswith(zero):
                a['children'].append(b)
        result['children'].append(a)
    result = post_process(result)
    json.dump(result, open('static/keyword.json', 'w'))
    # pprint(result['children'][7]['name'])
    # pprint(len(result['children'][7]['children']))
