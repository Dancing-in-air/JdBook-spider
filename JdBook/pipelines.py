# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pprint import pprint
import re


class JdbookPipeline(object):
    def process_item(self, item, spider):
        # 去除空白符
        item["book_name"] = re.sub(r"\s", "", item["book_name"])
        pprint(item)
