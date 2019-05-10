# encoding:utf-8
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
	req = request.Request(url=url)
	response = request.urlopen(req, timeout=5)
	html = response.read()
	html = etree.HTML(html)
	property_name_list = []
	property_value_list = []
	if html.xpath('//div[@class="basic-info cmn-clearfix"]/dl'):
		for t in html.xpath('//div[@class="basic-info cmn-clearfix"]/dl'):
			for dt in t.xpath('./dt[@class="basicInfo-item name"]'):
				property_name = ''.join(pattern.findall(''.join(dt.xpath('./text()'))))
				property_name_list.append(property_name)
			for dd in t.xpath('./dd[@class="basicInfo-item value"]'):
				property_value = ''.join(dd.xpath('.//text()')).replace("\n", "")
				property_value_list.append(property_value)
	for i in range(len(property_value_list)):
		property.setdefault(property_name_list[i], property_value_list[i])
	print(property)
	return property


def main():
	base_url = "http://baike.baidu.com/item/"
	keywords = load_keywords('organ.csv')
	for k in keywords:
		property = extract(base_url, k)
		if property == {}:
			logger.error("Keyword = '{}' not found in 百度百科.".format(k))
			continue
		fpath = 'data/百度/baidu_{}.json'.format(k)
		property['name'] = k
	fp = codecs.open(fpath, 'w', encoding='utf-8')
	json.dump(property, fp)
	fp.close()
	time.sleep(1.5)


if __name__ == '__main__':
	# main()
	extract('https://baike.baidu.com/item/','辽宁省电力有限公司')