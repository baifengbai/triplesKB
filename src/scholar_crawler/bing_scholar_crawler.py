#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:main
   Author:jasonhaven
   date:2018/4/17
-------------------------------------------------
   Change Activity:2018/4/17:
-------------------------------------------------
"""
import linecache
import argparse
import os
import log
import json
import codecs
from queue import Queue
import datetime
import time
from urllib import parse
from urllib import request
from bs4 import BeautifulSoup
import string
import threading
import random
import socket

logger = log.Logger().get_logger()

headers = {
	"Upgrade-Insecure-Requests": "1",
	"Connection": "keep-alive",
	"Cache-Control": "max-age=0",
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
	"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,la;q=0.7,pl;q=0.6",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
}

base_url = "https://cn.bing.com/academic/search?"


def load_keywords(fpath):
	with codecs.open(fpath, 'r', encoding='utf-8') as f:
		keywords = list(set(key.strip().split(':')[-1] for key in f.readlines()))
	return keywords


queue = Queue()
no_exist_keys = set()
good = 0
total = 0


def gen_url_for_keyword(key):
	global queue
	for i in range(5):
		first = 1 + i * 10
		query = {}
		query['q'] = key
		query['first'] = str(first)
		url = base_url + parse.urlencode(query)
		queue.put(url)


def init_queue(keywords):
	for key in keywords:
		gen_url_for_keyword(key)


def download_html(url, retry, delay):
	'''
	:return:无法访问,暂未找到，正常
	'''
	try:
		req = request.Request(url=url, headers=headers)
		resp = request.urlopen(req, timeout=5)

		if resp.status != 200:
			logger.error('url open error. url = {}'.format(url))

		html_doc = resp.read()

		if html_doc == None or html_doc.strip() == '':
			logger.error('NULL html_doc')
		return html_doc
	except Exception as e:
		logger.error("failed and retry to download url {} delay = {}".format(url, delay))
		if retry > 0:
			time.sleep(delay)
			retry -= 1
			return download_html(url, retry, delay)


def extract(key, url):
	'''
	:return:[author,author]
	'''
	global no_exist_keys
	global total
	total += 1

	html = download_html(url, 3, 2)

	if html == None:
		logger.error("unreachable url {}.".format(url))
		return [], []
	soup = BeautifulSoup(html, 'lxml')
	text = soup.text

	if text.find('暂未找到') != -1:
		no_exist_keys.add(key)  # 减少搜索次数
		logger.error("keyword not exists {}.".format(key))
		return [], []

	# 抽取人名
	author_div = soup.find('div', {'id': 'fgid_author'})

	if author_div == None:
		logger.error("div='fgid_author' not exists.")
		return [], []
	aca_fg_items = author_div.nextSibling.find('div', {'class': 'aca_fg_items'})
	author_list = aca_fg_items.findAll('li')

	if author_list == None or author_list == []:
		logger.error("no more authors.")
		return [], []

	author_list = [item.text.strip() for item in author_list]

	# 获取更多focus
	focus_list = []
	focus_div = soup.find('div', {'id': 'fgid_fos'})
	if focus_div == None:
		logger.error("div='fgid_fos' not exists.")
		return author_list, []
	else:
		aca_fg_items = focus_div.nextSibling.find('div', {'class': 'aca_fg_items'})
		focus_list = aca_fg_items.findAll('li')

	if focus_list != None and focus_list != []:
		focus_list = [item.text.strip() for item in focus_list]

	return author_list, focus_list


def start(url):
	global good
	logger.info(url)
	query = parse.urlparse(url).query
	key = parse.parse_qs(query)['q'][0]
	author_list, focus_list = extract(key, url)

	if author_list == []:
		return

	good += 1

	# 保存人名
	fp.write('\n'.join(author_list))

	if focus_list == []:
		return

	# 更新队列
	if queue.qsize() < 10000 and len(set(linecache.getlines('authors.txt')))<500000:
		for fos in focus_list:
			gen_url_for_keyword(fos)


class Consumer(threading.Thread):
	def run(self):
		global queue
		global good
		while queue.qsize() > 0:
			url = queue.get()
			start(url)
			logger.info("total:{}/{}...".format(total, queue.qsize()))
			logger.info("good:{}/{}...".format(good, queue.qsize()))
			time.sleep(2)


if __name__ == '__main__':
	keywords = load_keywords('keyword.csv')
	init_queue(keywords)
	fp = open('authors.txt', 'a', encoding='utf-8')
	for i in range(10):
		c = Consumer()
		c.start()
