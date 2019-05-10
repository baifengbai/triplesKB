# encoding:utf-8
import os
from urllib import request
from urllib import parse
from lxml import etree
import re
import json
import codecs
import log
import time

logger = log.Logger().get_logger()
pattern = re.compile("[\u4e00-\u9fa50-9]+")


def load_keywords(fp):
	with codecs.open(fp, 'r', encoding='utf-8') as f:
		return list(set(key.strip() for key in f.readlines() if key.strip() != ''))


def extract(url, name):
	url = url + parse.quote(name)
	property = dict()
	property['name'] = name
	fpath = 'data/hudong_{}.json'.format(name)
	req = request.Request(url=url)
	response = request.urlopen(req, timeout=5)
	html = response.read()
	html = etree.HTML(html)
	if html.xpath('//div[@class="module zoom"]'):
		for tr in html.xpath('//div[@class="module zoom"]//tr'):
			for td in tr.xpath('./td'):
				property_name = ''.join(''.join(td.xpath('./strong//text()')))
				property_name = property_name[0:-1]
				property_value = ''.join(''.join(td.xpath('./span//text()')).split())
				if property_name or property_value != '':
					property.setdefault(property_name, property_value)
	return property


def main():
	base_url = "http://www.baike.com/wiki/"
	keywords = load_keywords('organ.csv')
	count = 0


for k in keywords:
	count = count + 1
	fpath = 'data/互动/Hudong_{}.json'.format(k)
	print('{}/{}...'.format(count, len(keywords)))
	if os.path.exists(fpath):
		continue
	property = extract(base_url, k)
	property['name'] = k
	if property == {}:
		continue
	logger.error("Keyword = '{}' found in 互动百科.".format(k))

	fp = codecs.open(fpath, 'w', encoding='utf-8')
	json.dump(property, fp)
	fp.close()
	time.sleep(1.5)

if __name__ == '__main__':
	main()
