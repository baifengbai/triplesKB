import requests
import json
import time
import os
import re
import difflib
import threading
from queue import Queue

##########################################根据机构和人名抽取##########################################
def filter_by_aff(a, b):
	'''
	根据机构单位过滤

	:return: -1 没有包含；正数包含
	'''
	a = remove_punctuation(a)
	b = remove_punctuation(b)
	# 相似度计算

	seq = difflib.SequenceMatcher(lambda x: x == " ", a, b)
	ratio = seq.ratio()
	
	return ratio 


def search_person(query, organ, type='person'):
	'''
	:param type: person| following
	:param query: query string. This parameter is required
	'''
	#  https://api.aminer.org/api/search/person
	base_url = "https://api.aminer.org/api/search/" + type + "?"

	param = 'query=' + query.replace(' ', '%20') + '&sort=relevance&'

	offset = 0
	size = 10  # results的个数
	
	headers = {
		"Upgrade-Insecure-Requests": "1",
		"Connection": "keep-alive",
		"Cache-Control": "max-age=0",
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
		"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,la;q=0.7,pl;q=0.6",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
	}
	
	search_url = base_url + param
	search_url += "offset=" + str(offset) + "&size=" + str(size)+'&limit=50'
	
	print(search_url)
	
	try:
		
		'''
		proxy_list=[p.strip() for p in open('ProxyGetter/proxies.txt').readlines()]
		proxy=random.choice(proxy_list)
		proxy_handler = request.ProxyHandler({'http': proxy})
		opener=request.build_opener(proxy_handler)
		request.install_opener(opener)
		'''
				
		response = requests.get(search_url, headers=headers)
		content = json.loads(response.content)#windows下将bytes.decode()为str
		results = content["result"]
		if results==[]:
			print('results==[]')
			return {}
		for r in results:
			if 'desc' in r['aff'].keys():
				aff = r['aff']['desc'].strip()
			else:
				continue
			if filter_by_aff(organ, aff) >= 0.3 :  # 匹配到机构
				return r
		return {}
	except Exception as e:
		print(e)
		return {}


# 去除所有半角全角符号，只留字母、数字、中文。
def remove_punctuation(line):
	rule = re.compile(r"[^a-zA-Z\u4e00-\u9fa5 ]")
	line = rule.sub('', line)
	return line


def test():
	query = 'Geoffrey Hinton'
	organ = 'University of Toronto'

	assert {} != search_person(query, organ)


def extract(x):
	success = 'True'
	fail = open('False.txt', 'a')
	global good
	global bad

	try:
		size = len(data)
		name, organ = x.strip().split('\t')
		result = search_person(name, organ)

		if result == {}:
			bad += 1
			print("{}/{} is not ok ...".format(bad, size))
			fail.write(x)
			return

		# 更新一下
		name = result['name']
		organ = result['aff']['desc'].strip()

		fname = success + '/' + 'Person' + '_' + name.replace(' ','-') + '_' + organ.replace(',','-')[:10] + ".json"

		if os.path.exists(fname):
			return

		good += 1
		json.dump(result, open(fname, 'w'))
		print("{}/{} is ok...".format(good, size))

		fail.close()
	except Exception as e:
		print(e)
	finally:
		fail.close()


class Consumer(threading.Thread):
	def run(self):
		global queue
		while queue.qsize() > 0:
			d = queue.get()
			extract(d)
			time.sleep(3)


queue = Queue()
good = 0
bad = 0

if __name__ == '__main__':
	'''
	fin = 'organ.csv'
	data = open(fin, 'r', encoding='utf-8').readlines()
	for d in data:
		queue.put(d)

	for i in range(10):
		c = Consumer()
		c.start()
	'''
	test()
	
	'''
	fin = 'organ.csv'
	data = open(fin, 'r', encoding='utf-8').readlines()
	for d in data:
		extract(d)
		time.sleep(3)
	'''
	