data 抓取结果
logs 生成日志
ProxyGetter 构建代理池
Util 代理池工具包
log.py 日志工具
post_process.py 后处理脚本
baidu_scholar_crawler.py 主函数（启动爬虫）
keyword.csv 关键字词典

启动爬虫：

> optional arguments:
>   -h, --help      show this help message and exit
>   --key-num N     input number of keywords (default: 100)
>   --thread-num N  input number of thread (default: 10)
>   --page-num N    input number of pages (default: 5)

```shell
python main.py --key-num 100 --thread-num 10 --page-num 5
```

