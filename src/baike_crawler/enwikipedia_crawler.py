# encoding =utf-8
import os
from bs4 import BeautifulSoup
import requests
import log
import time
import codecs
import json

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


def main():
	en_base_url = 'https://en.wikipedia.org/wiki/'
	keywords = load_keywords('organ.csv')
	count=0
	for k in keywords:
		count=count+1
		fpath = 'data/enwiki/enwiki_{}.json'.format(k)
		print('{}/{}...'.format(count,len(keywords)))
		if os.path.exists(fpath):
			continue
		property = extract(en_base_url, k)
                        property['name']=k
		if property == {}:
			continue
		logger.info("Keyword = '{}' found in 英文维基百科.".format(k))
		fp = codecs.open(fpath, 'w', encoding='utf-8')
		json.dump(property, fp)
		fp.close()
		time.sleep(2.5)


if __name__ == '__main__':
	main()
