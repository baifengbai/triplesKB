#encoding = utf-8
import requests
import json
import time
import os
import re
import random
import datetime

good = 0
bad = 0

def search_person(query, type='person'):
	'''
	:param type: person| following
	:param query: query string. This parameter is required
	'''
	base_url = "https://api.aminer.org/api/search/" + type + "?"

	param = 'query=' + query.replace(' ', '%20') + '&sort=relevance&'

	offset = 0
	size = 10

	headers = {
		"Upgrade-Insecure-Requests": "1",
		"Connection": "keep-alive",
		"Cache-Control": "max-age=0",
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
		"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,la;q=0.7,pl;q=0.6",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
	}

	search_url = base_url + param
	search_url += "offset=" + str(offset) + "&size=" + str(size) + '&limit=50'
	print(search_url)
	'''
	try:
		response = requests.get(search_url, headers=headers)
		content = json.loads(response.content)  # windows下将bytes.decode()为str
		results = content["result"]
		if results == []:
			print('results==[]')
			return {}
		for r in results:
			if 'desc' in r['aff'].keys():
				return r
		return {}
	except Exception as e:
		print(e)
		return {}
	'''


def remove_punctuation(line):
	rule = re.compile(r"[^a-zA-Z\u4e00-\u9fa5 ]")
	line = rule.sub('', line)
	return line


def test():
	query = 'Geoffrey Hinton'
	assert {} != search_person(query)


def extract(x):
	success = 'True'
	fail = open('False.txt', 'a')
	global good
	global bad

	try:
		size = len(data)
		result = search_person(x.strip())

		if result == {}:
			bad += 1
			print("{}:\t{}/{} is not ok ...".format(datetime.datetime.now(), bad, size))
			fail.write(x)
			return

		# 更新一下
		name = result['name']

		fname = success + '/' + remove_punctuation(name) + ".json"

		if os.path.exists(fname):
			return

		good += 1
		json.dump(result, open(fname, 'w'))
		print("{}:\t{}/{} is ok ...".format(datetime.datetime.now(), good, size))

		fail.close()
	except Exception as e:
		print(e)
	finally:
		fail.close()


if __name__ == '__main__':
	search_person('Geoffrey Hinton')
	search_person('Yoshua Bengio')
	search_person('Yann LeCun')

	# fin = 'name.csv'
	# data = open(fin, 'r', encoding='utf-8').readlines()
	#
	# for d in data:
	# 	extract(d)
	# 	delay = random.randrange(8, 12) + int(random.random() * 10) / 10
	# 	time.sleep(delay)
