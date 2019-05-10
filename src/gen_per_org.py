# encoding = utf-8
import re
import loguru
import json
from collections import defaultdict


def main(per_dict, organ_dict, des):
    # keys = ['aff', 'name', 'avatar','indices', 'tags', 'pos', 'contact', 'attr']
    pers = json.load(open(per_dict, 'r'))
    organs = json.load(open(organ_dict, 'r'))
    organs_table = {}#name -> id
    for k, v in organs.items():
        if 'Name' in v.keys():
            organs_table[v['Name']] = k
        else:
            organs_table[v['name']] = k

    with open(des, 'w') as f:
        f.write('%s##%s##%s\n' % ('person', 'organ', 'is'))
        for per_id, per_val in pers.items():
            ks = find_organs_for_per(per_val, organs_table)
            if ks != []:
                for k in ks:
                    f.write('%s##%s##%s\n' % (per_id, k, str(1)))


def find_organs_for_per(per_val, organs_table):
    tags = per_val['tags']
    result = []

    if tags != '':
        for tag in tags:
            try:
                organ_id = organs_table[tag.lower()]
            except KeyError:
                # loguru.logger.error('KeyError')
                continue
            if organ_id != '':
                result.append(organ_id)

    return result


if __name__ == "__main__":
    main('persons_dict.json', 'organs_dict.json', 'per_org_rel.csv')
