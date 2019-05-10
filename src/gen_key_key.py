# encoding = utf-8
import re
import loguru
import json


def compare(tpl):
    '''
    0：自己     1：上级    2：下级    3：同领域    -1:无关系
    '''
    x, y = tpl
    if x == y:
        return x, y, 0
    elif len(x.split('.')) == len(y.split('.')):
        xs = x.split('.')
        ys = y.split('.')
        for i in range(len(xs)):
            if xs[i] != ys[i]:
                break
        if i > 0:
            return x, y, 3
        else:
            return x, y, -1
    else:
        if y.startswith(x):  # 1：上级
            return x, y, 1
        elif x.startswith(y):  # 2：下级
            return x, y, 2
        else:
            return x, y, -1


def main(src, des):
    data = json.load(open(src,'r'))
    ids = list(data.keys() )
    with open(des, 'w') as f:
        f.write('%s##%s##%s\n' % ('field1', 'field2', 'relation'))
        n = len(ids)
        tpl = [[ids[i], ids[j]] for i in range(n) for j in range(n)]
        result = list(map(compare, tpl))
        
        for k1,k2,rel in result:
            f.write('%s##%s##%s\n' % (k1,k2,rel))


if __name__ == "__main__":
    main('field_dict.json', 'triples/key_key_rel.csv')
