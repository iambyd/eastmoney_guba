# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

# from scrapy.item import Item


class MongoDBPipeline(object):
    """保存爬虫数据到mongodb中"""

    DB_URI = 'mongodb://localhost:27017/'
    DB_NAME = 'eastmoney'
    Collection_NAME = 'eastmoney'

    def open_spider(self, spider):
        """spider处理数据前，调用该方法，此处主要打开数据库"""
        self.client = client = MongoClient(self.DB_URI)
        self.db = self.client[self.DB_NAME]

    def close_spider(self, spider):
        """spider关闭时，调用该方法，关闭数据库"""
        self.client.close()

    def process_item(self, item, spider):
        collection = self.db[self.Collection_NAME]
        post = dict(item)
        collection.insert_one(post)
        return item


# class EastmoneySpiderPipeline(object):

#     def process_item(self, item, spider):
#         return item
