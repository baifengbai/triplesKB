#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:post_process.py
   Author:jasonhaven
   date:19-1-12
-------------------------------------------------
   Change Activity:19-1-12:
-------------------------------------------------
"""
import json
import os


def main():
	count = 0
	for dirpath, dirnames, filenames in os.walk('./data'):
		for fname in sorted(filenames):
			fpath = dirpath + os.path.sep + fname
			if os.path.getsize(fpath) == 0:
				continue
			try:
				data = {}
				with open(fpath, 'r', encoding='utf-8') as f:
					data = json.load(f)
					count = count + 1
					print('{}:'.format(count), data)
			#                                                 data['name']=fname.split('_')[1][:-5]
			#                                                 fp=open(fpath,'w',encoding='utf-8')
			#                                                 json.dump(data,fp)
			#                                                 fp.close()
			except Exception as e:
				print("Error in load file = {}".format(fpath))
				continue


def turn_data2org():
	data = []
	for dirpath, dirnames, filenames in os.walk('./data/zhwiki/'):
		for fname in sorted(filenames):
                                data.append(fname[:-5].split('_')[1])
	with open('a.csv', 'w', encoding='utf-8') as f:
		f.writelines('\n'.join(data))


if __name__ == '__main__':
	turn_data2org()