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
	zh_base_url = 'https://zh.wikipedia.org/wiki/'
	keywords = load_keywords('organ.csv')
	count = 0
	try:
		for k in keywords:
		    count = count + 1
                            fpath = 'data/zhwiki/zhwiki_{}.json'.format(k)
                            print('{}/{}...'.format(count,len(keywords)))
                            if os.path.exists(fpath):
			continue
                            property = extract(zh_base_url, k)
                            property['name']=k
                            if property == {}:
                                continue
                            logger.info("Keyword = '{}' found in 中文维基百科.".format(k))
                            fpath = 'data/zhwiki_{}.json'.format(k)
                            fp = codecs.open(fpath, 'w', encoding='utf-8')
                            json.dump(property, fp)
                            fp.close()
                            time.sleep(2)
	except Exception as e:
		logger.error('ERROR {}'.format(e))
	finally:
		out.close()


if __name__ == '__main__':
	main()
