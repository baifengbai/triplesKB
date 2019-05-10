# encoding =utf-8
import os
from bs4 import BeautifulSoup
import requests
import log
import time
import codecs
import json
import threading
from queue import Queue

logger = log.Logger().get_logger()


def load_keywords(fp):
	with codecs.open(fp, 'r', encoding='utf-8') as f:
		return list(set(key.strip() for key in f.readlines() if key.strip() != ''))


def extract(base_url, keyword):
	property = {}
	property['name'] = keyword

	url = base_url + keyword.strip().replace(' ', '_')
	html = requests.get(url, timeout=15).text
	soup = BeautifulSoup(html, 'lxml')

	table = soup.find('table', class_="infobox")
	try:
		trs = table.find_all('tr')
	except:
		return {}
	for i in trs:
		try:
			tag = i.find('th').getText()
			tag = tag.replace('\n', '')
		except:
			tag = "None"
		try:
			val = i.find('td').getText()
			val = val.replace('\n', '')
		except:
			val = 'None'
		property[tag] = val
	return property


def start(k):
	en_base_url = 'https://en.wikipedia.org/wiki/'
	global count

	count = count + 1
	name=k.replace(' ', '_').replace(',','_')
	fpath = 'data/{}.json'.format(name)
	print('{}/{}...'.format(count, len(keywords)))

	if os.path.exists(fpath):
		return

	try:
		property = extract(en_base_url, k)

		if property == {}:
			return
                
		property['name'] = k
		logger.info("Keyword = '{}' found in 英文维基百科.".format(k))
		
		fp = codecs.open(fpath, 'w', encoding='utf-8')
		json.dump(property, fp)
		fp.close()
	except Exception as e:
		print(e)


class Consumer(threading.Thread):
	def run(self):
		global queue
		while queue.qsize() > 0:
			start(queue.get())
			time.sleep(2.5)


queue = Queue()
count = 0

if __name__ == '__main__':
	keywords = load_keywords('organ.csv')
	for k in keywords:
		queue.put(k.split('\t')[0].strip())

	for i in range(15):
		c = Consumer()
		c.start()
