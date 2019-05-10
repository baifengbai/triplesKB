# triplesKB

---

### Background

> 项目需求:根据给定的军事科技词词表,构建特定领域的人员与机构信息,并关联成三元组形式

### Idea

![基本思路](img/pipline.png)

### Environment

> python 3.x
>
> flask 1.x
>
> mongodb v3.6.3

### Directory

├── data                  保存最终的采集数据

│   ├── organizations

│   └── persons

└── web                             部署到Web服务器

└── src

   ├── aminer_crawler     Aminer爬虫

   ├── baike_crawler       百科爬虫

   │   └── data                 保存中间采集数据

   ├── dict                        关键字,人员,机构生成的id字典

   ├── scholar_crawler    学术爬虫

   │   ├── data

   │   ├── proxy_hellper   代理池工具

   │   └── util

   └── triples                    保存三元组

### Result

```python
python server.py  #启动flask服务器
```

![首页](img/web_index.png)

![知识库](img/web_kg.png)

### refer

- [spider](https://github.com/jasonhavend/DJH-Spider)
