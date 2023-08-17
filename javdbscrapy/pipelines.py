import datetime
import random

from bson import Binary

from pymongo import MongoClient

from gridfs import GridFS
import uuid

proxy_url = 'socks5://127.0.0.1:7890'

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}


class SaveToMongoDbPipline:
    def __init__(self):
        client = MongoClient("mongodb://localhost:27017/")
        db = client['py_crawal']
        self.batch_id = random.randint(404005, 999966454343)
        print(f'本次下载批次号：{self.batch_id}')
        self.doc = db['movies']
        self.batch_num = db['crawl_record_num']
        self.batch_num.insert_one({
            'num': self.batch_id,
            'created_time': datetime.datetime.now()
        })

    def process_item(self, item, spider):
        code = item['code']
        try:
            item['batch_num'] = self.batch_id
            self.doc.insert_one(dict(item))

        except Exception as e:
            print(e)
            print(f'{code}已存在,不存入mongodb')

        return item

    def update_item(self, item):
        aa = item['code']
        print(f'更新{aa}')
        update_query = {"$set": {"tag_list": ['debut']}}  # 替换为要添加的学生信息
        self.doc.update_one({'code': item['code']}, update_query)
