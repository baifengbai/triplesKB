# encoding = utf-8
import re
import loguru
import json
from collections import defaultdict
import pandas as pd


def main(per_key_dict, per_org_dict, des):
    per_key = pd.read_csv(per_key_dict, header=0,sep='##')
    per_org = pd.read_csv(per_org_dict, header=0,sep='##')

    per_key_table = dict((t['person'],t['field']) for i,t in per_key.iterrows())

    with open(des, 'w') as f:
        f.write('%s##%s##%s\n' % ('organ', 'field', 'is'))
        for i,t in per_org.iterrows():
            per, org=t['person'],t['organ']
            try:
                key = per_key_table[per]
                f.write('%s##%s##%s\n' % (org, key, '1'))
            except KeyError:
                continue


if __name__ == "__main__":
    main('per_key_rel.csv', 'per_org_rel.csv', 'org_key_rel.csv')
