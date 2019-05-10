├── aminer_crawler
│   ├── multi.py          多线程爬虫
│   └── single.py        单线程爬虫
├── baike_crawler      各个百科爬虫, batch_xxx的爬虫是对于大规模情况的批量输入的批处理多线程爬虫
│   ├── baidu_baike_crawler.py
│   ├── batch_baidu_crawler.py
│   ├── batch_enwikipedia_crawler.py
│   ├── batch_zhwiki_crawler.py
│   ├── data
│   ├── enwikipedia_crawler.py
│   ├── hudong_baike_crawler.py
│   ├── hudong_batch_crawler.py
│   ├── log.py
│   ├── post_process.py
│   ├── readme.md
│   ├── wikipedia.py
│   └── zhwikpedia_crawler.py
├── dict
│   ├── fields_dict.json
│   ├── organs_dict.json
│   └── persons_dict.json
├── gen_key_key.py          生成关键词与关键词三元组
├── gen_keywords_id.py   生成关键词id字典
├── gen_org_key.py          生成机构与关键词三元组
├── gen_orgs_id.py           生成机构id字典
├── gen_per_key.py          生成人员与关键词三元组
├── gen_per_org.py          生成人员与机构三元组
├── gen_pers_id.py           生成人员id字典
├── keywords.txt
├── readme.md
├── scholar_crawler       学术爬虫
│   ├── baidu_scholar_crawler.py
│   ├── bing_scholar_crawler.py
│   ├── data
│   ├── log.py
│   ├── post_process.py
│   ├── proxy_hellper
│   ├── readme.md
│   └── util
└── triples                        三元组数据集
    ├── key_key_rel.csv
    ├── org_key_rel.csv
    ├── per_key_rel.csv
    └── per_org_rel.csv

