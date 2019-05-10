#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:wiki_batch_crawler
   Author:jasonhaven
   date:19-1-19
-------------------------------------------------
   Change Activity:19-1-19:
-------------------------------------------------
"""

from bs4 import BeautifulSoup
from urllib import request
from queue import Queue
import os
import requests
import log
import time
import codecs
import json
import threading
import random
import copy
import datetime

logger = log.Logger().get_logger()
base_url = 'https://zh.wikipedia.org/wiki/'

properties = ['Preceding', 'Parent ', 'Child ']  # 可以扩展机构的属性


def run_time(func):
	def wrapper(*args, **kw):
		start = datetime.datetime.now()
		func(*args, **kw)
		end = datetime.datetime.now()
		logger.info('Finished in {}s'.format(end - start))

	return wrapper


class BatchCrawler():
	def __init__(self, keyword_dir='keyword', batch_size=2):
		self.keyword_dir = keyword_dir
		self.batch_size = batch_size

	def download_html(self, url, retry):
		try:
			proxy_list = [p.strip() for p in open('proxies.txt').readlines()]
			proxy = random.choice(proxy_list)
			proxy_handler = request.ProxyHandler({'http': proxy})
			opener = request.build_opener(proxy_handler)
			request.install_opener(opener)
			html_doc = requests.get(url, timeout=15).text
			return html_doc
		except Exception as e:
			logger.error("failed and retry = {} to download url {}".format(retry, url))
			if retry >= 0:
				time.sleep(1.5)
				return self.download_html(url, retry - 1)

	def load_keywords(self, batch):
		"""
		加载批量关键词
		:param batch:批量关键词列表
		:return:批量关键词
		"""
		keywords = []

		for fp in batch:
			with codecs.open(fp, 'r', encoding='utf-8') as f:
				keywords.extend(list(key.strip() for key in f.readlines() if key.strip() != ''))

		return keywords

	def list_files(self, dir):
		"""
		返回指定目录下全部文件
		:param dir:目录
		:return:
		"""
		return [dir + os.path.sep + f for f in os.listdir(dir)]

	def barch_process(self):
		"""
		批量处理关键字
		:param keyword_dir:关键字目录
		:param data_dir: 存放数据目录
		:param batch_size: 批处理关键字文件数目
		:return:
		"""
		files = []
		batch_files = []

		for f in os.listdir(self.keyword_dir):
			f = self.keyword_dir + os.path.sep + f
			if os.path.isdir(f):
				files.extend(self.list_files(f))
			else:
				files.append(f)

		idx = list(range(0, len(files), self.batch_size))

		for i in range(len(idx) - 1):
			batch_files.append(files[idx[i]:idx[i + 1]])

		batch_files.append(files[idx[-1]:])

		logger.info("total number of keyword files = {}, batch_size = {}.".format(len(files), self.batch_size))

		for i, batch in enumerate(batch_files):
			th = ThreadBatch(str(i), batch)  # 在batch级别使用多线程
			th.start()
			time.sleep(1)


class ThreadCrawler():
	def __init__(self, batch_files, thread_num=1, retry=3, delay=2,max_qsize=10**5):
		self.queue = Queue()
		self.batch_files = batch_files
		self.thread_num = thread_num
		self.retry = retry
		self.delay = delay

		self.queue.maxsize=max_qsize
		self.init_queue()

	def download_html(self, url, retry):
		try:
			# proxy_list = [p.strip() for p in open('proxies.txt').readlines()]
			# proxy = random.choice(proxy_list)
			# proxy_handler = request.ProxyHandler({'http': proxy})
			# opener = request.build_opener(proxy_handler)
			# request.install_opener(opener)
			html_doc = requests.get(url, timeout=15).text
			return html_doc
		except Exception as e:
			logger.error("failed and retry = {} to download url {}".format(retry, url))
			if retry >= 0:
				time.sleep(1.5)
				return self.download_html(url, retry - 1)

	def load_keywords(self, batch):
		"""
		加载批量关键词
		:param batch:批量关键词列表
		:return:批量关键词
		"""
		keywords = []

		for fp in batch:
			with codecs.open(fp, 'r', encoding='utf-8') as f:
				keywords.extend(list(key.strip() for key in f.readlines() if key.strip() != ''))

		return keywords

	def init_queue(self):
		keywords = list(set(self.load_keywords(self.batch_files)))
		for k in keywords:
			self.queue.put(k)

	def run(self):
		for i in range(self.thread_num):
			th = ThreadKeywords(str(i), self)
			th.start()

	def extract_keywords(self):
		"""
		每个线程内的抽取
		:return:
		"""
		count = 0

		try:
			while not self.queue.empty():
				logger.info('{} crawled. / {} left.'.format(count, self.queue.qsize()))

				k = self.queue.get()
				count = count + 1

				fpath = 'data/enwiki_{}.json'.format(k)

				if os.path.exists(fpath):  # 如果已经存在结果文件则跳过
					continue

				infobox, related_keywords = self.extract_infobox(k)

				if related_keywords:
					for t in related_keywords:
						self.queue.put(t)

				if infobox == {}:
					if int(random.random() * 10) > 6:  # 以一定概率将失败的关键词重新加入队列
						self.queue.put(k)
					continue

				infobox['Name'] = k

				keys = []
				for prop in properties:
					keys.extend([key for key in list(infobox.keys()) if key.find(prop) != -1])

				if keys:
					for k in keys:
						for t in infobox[k].split('\t'):
							self.queue.put(t)

				fp = codecs.open(fpath, 'w', encoding='utf-8')
				json.dump(infobox, fp)
				fp.close()

				time.sleep(self.delay)
		except Exception as e:
			logger.error('Exception in extract_keywords "{}".'.format(k))

	def extract_infobox(self, keyword):
		"""
		抽取指定URL的infobox
		:param keyword:
		:return:infobox json
		"""
		infobox = {}
		related_keywords = []

		try:
			url = base_url + keyword.strip().replace(' ', '_')
			html = self.download_html(url, self.retry)

			related_keywords = self.extract_related_keywords(keyword, copy.deepcopy(html))  # 扩展相关机构

			soup = BeautifulSoup(html, 'lxml')
			table = soup.find('table', class_="infobox")

			try:
				trs = table.find_all('tr')
			except:
				raise RuntimeError

			for i in trs:
				try:
					tag = i.find('th').getText()
					tag = tag.replace('\n', '\t')
				except:
					tag = "None"
				try:
					val = i.find('td').getText()
					div = i.find('div', class_="plainlist")

					if div is not None:
						val = '\t'.join([x.text for x in div.find_all('li')])
					else:
						val = val.replace('\n', '\t')
				except:
					val = 'None'

				infobox[tag] = val
		except RuntimeError as e1:
			logger.error("Keyword = '{}' RuntimeError.".format(keyword))
			return {}, related_keywords
		return infobox, related_keywords

	def extract_related_keywords(self, keyword, html):
		"""
		抽取指定URL的nowraplinks
		:param keyword:
		:param html:
		:return:list
		"""
		related_keywords = []
		try:
			# url = base_url + keyword.strip().replace(' ', '_')
			# html = download_html(url, 3)
			soup = BeautifulSoup(html, 'lxml')
			for table in soup.find_all('table', class_="nowraplinks navbox-subgroup"):
				for link in table.find_all('li'):
					for a in link.find_all('a'):
						k = a.get('title')
						if k is None or k == '' or k.startswith('List'):
							continue
						related_keywords.append(k)
			return related_keywords
		except RuntimeError as e1:
			logger.error("Keyword = '{}' RuntimeError.".format(keyword))
			return []


class ThreadBatch(threading.Thread):
	"""
	多线程处理batch级别
	"""

	def __init__(self, name, batch):
		threading.Thread.__init__(self)
		self.name = name
		self.batch = batch

	@run_time
	def run(self):
		logger.info("create thread for batch's number = {}".format(self.name))
		tc = ThreadCrawler(self.batch, thread_num=2, retry=3, delay=2,max_qsize=10*5)
		tc.run()


class ThreadKeywords(threading.Thread):
	"""
	多线程处理keywords
	"""

	def __init__(self, name, obj):
		threading.Thread.__init__(self)
		self.name = name
		self.obj = obj

	def run(self):
		logger.info("create sub_thread = {}".format(self.name))
		self.obj.extract_keywords()


if __name__ == '__main__':
	bc = BatchCrawler(keyword_dir='keyword', batch_size=1)
	bc.barch_process()
	# tc = ThreadCrawler(['keyword/1.csv'], thread_num=1, retry=3, delay=2)
	# tc.run()
