# encoding = utf-8
import re
import loguru
import json
from collections import defaultdict


def main(per_dict, field_dict, des):
    # keys = ['aff', 'name', 'avatar','indices', 'tags', 'pos', 'contact', 'attr']
    pers = json.load(open(per_dict, 'r'))
    fields = json.load(open(field_dict, 'r'))
    fields_table = {}#name -> id
    for k, v in fields.items():
        i, zh, en = v['id'], v['chinese'], v['english']
        fields_table[zh] = i
        fields_table[en] = i

    with open(des, 'w') as f:
        f.write('%s##%s##%s\n' % ('person', 'field', 'is'))
        for per_id, per_val in pers.items():
            ks = find_fields_for_per(per_val, fields_table)
            if ks != []:
                for k in ks:
                    f.write('%s##%s##%s\n' % (per_id, k, str(1)))


def find_fields_for_per(per_val, fields_table):
    tags = per_val['tags']
    result = []

    if tags != '':
        for tag in tags:
            try:
                field_id = fields_table[tag.lower()]
            except KeyError:
                # loguru.logger.error('KeyError')
                continue
            if field_id != '':
                result.append(field_id)

    return result


if __name__ == "__main__":
    main('persons_dict.json', 'fields_dict.json', 'per_key_rel.csv')
