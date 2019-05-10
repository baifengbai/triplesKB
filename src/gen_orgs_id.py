# encoding=utf-8
import re
import loguru
import json
import os


def main(directory, des):
    with open(des, 'w') as f:
        dct = {}
        for i, fname in enumerate(os.listdir(directory)):
            pid = str(i+1)
            organ = json.load(open(os.path.join(directory,fname), 'r'))
            if 'Name' in organ:
                organ['Name']=organ['Name'].lower()
            else:
                organ['name']=organ['name'].lower()
            dct[pid] = organ
        json.dump(dct, f)


if __name__ == "__main__":
    main('../data/organizations', 'organs_dict.json')
