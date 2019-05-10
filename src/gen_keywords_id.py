# encoding=utf-8
import re
import loguru
import json


def main(src, des):
    data = [l.strip() for l in open(src, 'r').readlines() if l.strip() != '']
    pattern = r'(?P<id>(\d+.)+)(?P<keyword>.+)'
    with open(des, 'w') as f:
        f.write("%s##%s##%s\n" % ("id", "chinese", 'english'))
        for s in data:
            match = re.match(pattern, s, re.S)
            if match == None:
                loguru.logger.error('match == None##'+s)
                continue

            dic = match.groupdict()
            id = dic['id']
            keyword = dic['keyword']

            if keyword.find('/') == -1:
                # loguru.logger.error(s+'##no english name')
                f.write("%s##%s##%s\n" % (id, keyword, 'None'))
                continue
            f.write("%s##%s##%s\n" %
                    (id, keyword.split('/')[0], keyword.split('/')[1]))
            # loguru.logger.info(s)


def test_input_format(fin):
    return [d for d in open(fin, 'r').readlines() if len(d.split('##')) != 3] == []


def update_no_english_keywords(src, upd, des):
    '''
    对于没有英文keyword的实例进行更新
    src:源文件
    upd:更新文件
    des:目标文件
    '''
    data1 = [l.strip() for l in open(src, 'r').readlines() if l.strip() != '']
    data2 = [l.strip() for l in open(upd, 'r').readlines() if l.strip() != '']

    result = {}
    for d in data1:
        dic = {}
        try:
            dic['id'], dic['chinese'], dic['english'] = d.split('##')
            result[dic['id']] = dic
        except Exception as e:
            print(len(d.split('##')))

    update = {}
    for d in data2:
        dic = {}
        try:
            dic['id'], dic['chinese'], dic['english'] = d.split('##')
            update[dic['id']] = dic
        except Exception as e:
            print(dic)
            print(len(d.split('##')))

    for k in update.keys():
        result[k] = update[k]

    with open(des, 'w') as f:
        for k, v in result.items():
            _, chinese, english = v['id'], v['chinese'], v['english']
            f.write("%s##%s##%s\n" % (k, chinese, english))


def dump(src, des):
    dct = {}
    for d in open(src, 'r').readlines()[1:]:
        i, j, k = d.strip().split('##')
        dct[i] = {'id': i, 'chinese': j, 'english': k.lower()}
    json.dump(dct, open(des, 'w',encoding='utf-8'))


if __name__ == "__main__":
    # main('fields 2.0.txt', 'fields_with_id.csv')

    # print(test_input_format('fields_with_id.csv'))
    # print(test_input_format('tmp/tmp.csv'))
    # update_no_english_keywords(
    #     'fields_with_id.csv', 'tmp/tmp.csv', 'fields_with_id_good.csv')
    # print(test_input_format('fields_with_id_good.csv'))
    
    dump('fields_with_id.csv','fields_dict.json')
