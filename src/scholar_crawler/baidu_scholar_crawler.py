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
import  socket

logger = log.Logger().get_logger()

headers = {
	'Referer': 'http://xueshu.baidu.com/',
	"Upgrade-Insecure-Requests": "1",
	"Connection": "keep-alive",
	"Cache-Control": "max-age=0",
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
	"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,la;q=0.7,pl;q=0.6",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
}

base_url = "https://xueshu.baidu.com/s?"


def run_time(func):
	def wrapper(*args, **kw):
		start = datetime.datetime.now()
		func(*args, **kw)
		end = datetime.datetime.now()
		logger.info('finished in {}s'.format(end - start))

	return wrapper


class Crawler():
	def __init__(self, key_num=-1, thread_num=1, fpath="keyword.csv", start_num=0, end_num=5, retry=3, delay=2):
		self.queue = Queue()
		self.key_num = key_num
		self.thread_num = thread_num
		self.start_num = start_num
		self.end_num = end_num
		self.fpath = fpath
		self.retry = retry
		self.delay = delay

	def load_keywords(self):
		'''
		加载关键字

		:param num:
		:return:
		'''
		with codecs.open(self.fpath, 'r', encoding='utf-8') as f:
			if self.fpath.startswith('zh'):
				self.keywords = list(set(key.strip() for key in f.readlines() if key.strip()!='') )
			else:
				self.keywords = list(set(key.strip().split(':')[-1] for key in f.readlines()))
			if self.key_num != -1:
				self.keywords = self.keywords

	def init_url_queue(self):
		'''
		初始化队列

		:return:
		'''
		
		for key in self.keywords:
			try:
				# 分页查询
				for page in range(self.start_num, self.end_num + 1):
					# 构造请求
					query = {}
					pn = page * 10

					query['wd'] = parse.quote(key, safe=string.printable)
					
					query['pn'] = str(pn)
					query = parse.urlencode(query)

					if self.fpath.startswith('zh'):
						query=parse.unquote(query)
					
					# 构造地址
					url = base_url + query
					
					self.queue.put((key, url))
		
			except socket.timeout as e:
				logger.error('出错信息：{}'.format(e))
				continue 
			except Exception as e:
				logger.error('出错信息：{}'.format(e))
				continue

	def download_html(self, url):
		'''
		下载网页

		:param url:
		:param retry:
		:return:
		'''
		try:
			proxy_list=[p.strip() for p in open('ProxyGetter/proxies.txt').readlines()]
			proxy=random.choice(proxy_list)
			proxy_handler = request.ProxyHandler({'http': proxy})
			opener=request.build_opener(proxy_handler)
			request.install_opener(opener)
			logger.info('proxy = {}'.format(proxy))

			req = request.Request(url=url, headers=headers)
			resp = request.urlopen(req, timeout=5)
			# resp = request.urlopen(url, timeout=5)
			# resp=opener.open(url)

			if resp.status != 200:
				logger.error('url open error. url = {}'.format(url))
			html_doc = resp.read()
			if html_doc==None or html_doc.strip() == '':
				logger.error('NULL html_doc')
			return html_doc
		except Exception as e:
			logger.error("failed and retry to download url {} delay = {}".format(url, self.delay))
			if self.retry > 0:
				time.sleep(self.delay)
				self.retry -= 1
				return self.download_html(url)

	def extract_full_organization(self, query):
		'''
		抽取机构名字

		:param query:
		:return:
		'''
		# wd=author%3A%28Yann%20LeCun%29&tn=SE_baiduxueshu_c1gjeupa&sc_hit=1&bcp=2&ie=utf-8&tag_filter=%20%20%20affs%3A%28New%20York%20University%29
		name = "None"
		try:
			query_dict = parse.parse_qs(query)
			if query_dict == {}: 
				return "None"
			organ = query_dict['tag_filter'][0]
			# ['   affs:(New York University)']
			name = organ[organ.index("affs:") + len("affs:"):]
			return name
		except Exception as e:
			logger.error("extract_full_organization e = {}".format(e))
			return "None"

	def extract_organizations(self, author):
		'''
		抽取机构信息

		:param author:
		:return:
		'''
		organizations = []

		# 构造请求
		# https://xueshu.baidu.com/s?wd=author%3A%28Yann%20LeCun%29%20
		# https://xueshu.baidu.com/s?wd=author%3A%28周志华%29
		query = {}
		query['wd'] = parse.quote("author:" + author, safe=string.printable)
		query = parse.urlencode(query)

		if self.fpath.startswith('zh'):
			query=parse.unquote(query)

		# 构造地址
		url = base_url + query
		
		logger.info("extract_organizations for author = {}, url = {}".format(author,url))

		html_doc = self.download_html(url)

		if html_doc==None or html_doc.strip() == '':
			return []
		
		soup = BeautifulSoup(html_doc, "html.parser")

		try:
			# 获取左侧栏
			leftnav_div = soup.find("div", id="leftnav")
			leftnav_items = leftnav_div.find_all('div', class_="leftnav_item")

			# 抽取机构
			organs_block = leftnav_items[-1].find("div", class_="leftnav_list_cont").find_all('a')
			for organ in organs_block:
				organ_full_name = self.extract_full_organization(organ.get('href')[3:])
				organizations.append(organ_full_name)
			return organizations
		except Exception as e:
			logger.error("extract organization for {} url = {}".format(author, url))
			return []

	def extract_html_doc(self, html_doc):
		'''
		抽取网页

		:param html_doc:
		:return:
		'''
		records = []

		soup = BeautifulSoup(html_doc, "html.parser")
		result_div = soup.find('div', id="bdxs_result_lists")
		result_lists = result_div.find_all("div", class_="result sc_default_result xpath-log")

		for i, result in enumerate(result_lists):
			record = []

			logger.info("extract for item = {}  delay = {}".format(i, self.delay))
			time.sleep(self.delay)

			# 抽取论文题目paper_title和超链接total_href
			h3 = result.find("h3")
			paper_title = h3.get_text().strip()
			sub_href = h3.find('a').get('href')
			total_href = "http://xueshu.baidu.com" + sub_href
			# logger.info('title = {}, url = {}'.format(paper_title, total_href))

			# 抽取作者信息
			info = result.find('div', class_="sc_info")
			authors_block = info.find('span').find_all('a')
			authors_qs = [x.get('href').strip()[3:] for x in authors_block]

			for query,author_block in zip(authors_qs,authors_block):
				time.sleep(self.delay)
				query=query.strip()
				# logger.info("author_query = {}".format(query))
				query_dict = parse.parse_qs(query)
				if query.startswith('ueshu.baidu.com/usercenter'):
					#{'xueshu.baidu.com/usercenter/data/author?cmd': ['authoruri'],'wd': ['authoruri:(b2adafebea64e9b0) author:(张铃) 安徽大学人工智能研究所']}
					author = query_dict['wd'][0].split()[1].split(':')[1][1:-1]
					
					organizations=[query_dict['wd'][0].split()[2]]
				elif query.startswith('wd=authoruri'):
					#wd=authoruri%3A%287ca9d3874e254001%29%20author%3A%28%E7%8E%8B%E6%96%87%E9%80%9A%29%20%E5%8C%97%E4%BA%AC%E5%B7%A5%E4%B8%9A%E5%A4%A7%E5%AD%A6%E5%9F%8E%E5%B8%82%E4%BA%A4%E9%80%9A%E5%AD%A6%E9%99%A2%E5%A4%9A%E5%AA%92%E4%BD%93%E4%B8%8E%E6%99%BA%E8%83%BD%E8%BD%AF%E4%BB%B6%E6%8A%80%E6%9C%AF%E5%8C%97%E4%BA%AC%E5%B8%82%E9%87%8D%E7%82%B9%E5%AE%9E%E9%AA%8C%E5%AE%A4&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_f_para=sc_hilight%3Dperson&sort=sc_cited
					author = query_dict['wd'][0].split()[1].split(':')[1][1:-1]
					
					organizations=[query_dict['wd'][0].split()[2]]
				elif query.startswith('wd=author%'):
					# wd=author%3A%28%E4%BD%99%E5%87%AF%29%20%E7%99%BE%E5%BA%A6&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_f_para=sc_hilight%3Dperson
					# wd=author%3A%28%E5%BE%90%E5%86%9B%29%20%E5%93%88%E5%B0%94%E6%BB%A8%E5%B7%A5%E4%B8%9A%E5%A4%A7%E5%AD%A6%E6%B7%B1%E5%9C%B3%E7%A0%94%E7%A9%B6%E7%94%9F%E9%99%A2%E6%99%BA%E8%83%BD%E8%AE%A1%E7%AE%97%E7%A0%94%E7%A9%B6%E4%B8%AD%E5%BF%83&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_f_para=sc_hilight%3Dperson
					author = query_dict['wd'][0].split(')')[0][8:]
					if author=="":
						author=author_block.text#用关键词搜索页面下的作者文本表示,对于中文没差别，对于英文名字可能是缩写
					
					organizations = self.extract_organizations(author)
				else:
					logger.error('query error : {}'.format(query))
					continue
	
				# logger.info('author = {}'.format(author))
				# logger.info('organizations = {}'.format(organizations))
		
				# 添加记录
				record.append((author, organizations))
				records.append(record)
		return records

	def begin(self):
		'''
		开始抓取

		:param keywords:
		:param start_page:
		:param end_page:
		:return:
		'''

		while not self.queue.empty():
			key,url = self.queue.get()

			logger.info("search url = {} delay = {}".format(url, self.delay))
			time.sleep(self.delay)
			# https://xueshu.baidu.com/s?wd=Deep+Learning&tn=SE_baiduxueshu_c1gjeupa&cl=3&ie=utf-8&bs=Deep+Learning&f=8&rsv_bp=1&rsv_sug2=0&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D

			# 文件打开
			url_dict = parse.parse_qs(url)
			url_pn = url_dict['pn'][0]
			

			html_doc = self.download_html(url)

			if html_doc==None or html_doc.strip()=='':
				continue

			records = self.extract_html_doc(html_doc)

			if records == []: 
				continue

			fmode = "a"
			fname = "{}-{}.json".format('_'.join(key.split(' ')), url_pn)
			fpath = "data/{}".format(fname)
			if os.path.exists(fpath) and os.path.getsize(fpath)==0:
				continue
			fp = codecs.open(fpath, fmode, encoding='utf-8')
			json.dump({key: records}, fp)
			fp.close()

			logger.info("done with keyword = {} ".format(key))

	def run(self):
		for i in range(self.thread_num):
			th = MyThread(str(i), self)
			th.start()


class MyThread(threading.Thread):
	def __init__(self, name, target):
		threading.Thread.__init__(self)
		self.name = name
		self.target = target

	@run_time
	def run(self):
		logger.info("create thread : {}".format(self.name))
		self.target.begin()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Baidu scolar Crawler')
	parser.add_argument('--key-num', type=int, default=100, metavar='N',
	                    help='input number of keywords (default: 100)')
	parser.add_argument('--thread-num', type=int, default=10, metavar='N',
	                    help='input number of thread (default: 10)')
	parser.add_argument('--page-num', type=int, default=10, metavar='N',
	                    help='input number of pages (default: 10)')
	parser.add_argument('--input', type=str, default='keyword.csv', metavar='S',
	                    help='input keyword file path')
	
	# init_parser = parser.add_mutually_exclusive_group(required=False)
	# init_parser.add_argument('--init', dest='init', action='store_true')
	# init_parser.add_argument('--no-init', dest='init', action='store_false')
	# parser.set_defaults(init=False)
	
	args = parser.parse_args()

	logger.info("开始抓取:key_num={},thread_num={},page_num={}".format(args.key_num,args.thread_num,args.page_num))

	# queue size = [end-start+1] * key_nums
	
	crawler = Crawler(key_num=args.key_num, thread_num=args.thread_num, fpath=args.input, start_num=0, end_num=args.page_num)#一个页面固定约 80 s
	
	crawler.load_keywords()
	crawler.init_url_queue()
	
	time.sleep(5)
	
	crawler.run()
	
