import time

import requests
from scrapy import signals


class MyExtend:

    def __init__(self, crawler):
        self.crawler = crawler
        # 注册信号
        self.crawler.signals.connect(self.spider_start, signals.spider_opened)  # 爬虫开始的时候做某些动作
        self.crawler.signals.connect(self.engine_start, signals.engine_started)  # 爬虫开始的时候做某些动作
        self.crawler.signals.connect(self.engine_stop, signals.engine_stopped)  # 引擎关闭的时候做特殊多动作

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def spider_start(self):
        print("signals.spider_opened")

    def engine_start(self):
        print("signals.engine_started")

    def engine_stop(self):
        print("signals.engine_stopped")


        # res = requests.post('http://127.0.0.1:8000/start-handle-task')
        # print(res.text)
