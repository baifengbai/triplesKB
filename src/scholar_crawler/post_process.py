#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:post_process
   Author:jasonhaven
   date:18-12-29
-------------------------------------------------
   Change Activity:18-12-29:
-------------------------------------------------
"""
import re


def author_coauthor():
	result = []
	file = "author_coauthor.csv"
	data = open(file, 'r', encoding='utf-8').readlines()
	for line in data:
		if len(line.strip().split('\t')) < 2:
			continue
		result.append(line)
	with open('coauthor.csv', 'w', encoding='utf-8') as f:
		f.writelines(result)

def author_organ():
	result = []
	upper = r"University|Laboratory|Institute|School|College|Academy|Hospital|Foundation|Department|Laboratories|Corporation|Consultancy|Centro|Centre|International|Technology|Universiti|Administration|Ministry|Universiteit|Station|enterprise|Istituto|Agency|Energy|Management|National|Universitat|Office|Institut|Universidad|Departament|Council|Universidade|Center|Company|Seminar|System|Educational|Service|Research|Government|Unit"
	lower = upper.lower()
	#short=r"Dep|Lab|Inst|Dept"
	chinese = r"学院|大学|学校|公司|组织|实验室|中国|公司|研究院|中心|集团|实验室|医院|研究所|局"
	other = r"Universitaet|Universität|Università|Département|Université"
	pattern = upper + '|' + lower + '|' + chinese + '|'+ other

	file = "author_organ.csv"
	data = open(file, 'r', encoding='utf-8').readlines()
	total = len(data)
	for line in data:
		org = line.strip().split('\t')[1]
		if len(org) < 8:  # 过滤长度
			continue
		if re.findall(pattern, org) == []:
			continue
		result.append(line)
	with open('organ.csv', 'w', encoding='utf-8') as f:
		f.writelines(result)

	print("保留 : {:.2f}".format(len(result) / total))#保留 : 0.92


if __name__ == '__main__':
	author_coauthor()
	author_organ()
