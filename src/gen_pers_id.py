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
            person = json.load(open(os.path.join(directory,fname), 'r'))
            dct[pid] = person
        json.dump(dct, f)

if __name__ == "__main__":
    main('../data/persons','persons_dict.json')
