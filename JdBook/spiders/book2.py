# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json


class BookSpider(scrapy.Spider):
    name = 'book2'
    allowed_domains = ['jd.com', 'p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        item = dict()
        dt_list = response.xpath("//div[@id='booksort']//div[@class='mc']/dl/dt")
        for dt in dt_list:
            # 获取图书大分类
            item["cat_book"] = dt.xpath("./a/text()").extract_first()
            # 获取图书小分类以及小分类的地址
            em_list = dt.xpath("./following-sibling::dd[1]/em")
            for em in em_list:
                item["books"] = em.xpath("./a/text()").extract_first()
                books_part_url = em.xpath("./a/@href").extract_first()
                if books_part_url is not None:
                    item["books_url"] = "https:" + books_part_url
                # 对小分类发起请求并将请求交给parse_books函数处理
                yield scrapy.Request(item["books_url"], callback=self.parse_books, meta={"item": deepcopy(item)},
                                     dont_filter=False)

    def parse_books(self, response):
        item = response.meta["item"]
        # 获取图书详情页地址
        li_list = response.xpath("//div[@id='plist']/ul/li")
        for li in li_list:
            book_part_url = li.xpath(".//div[@class='p-name']/a/@href").extract_first()
            if book_part_url is not None:
                item["book_url"] = "https:" + book_part_url
            # 对图书详情发起请求并将请求交给parse_book函数处理
            yield scrapy.Request(item["book_url"], callback=self.parse_book, meta={"item": deepcopy(item)},
                                 dont_filter=False)
        # 翻页
        # 提取下一页地址
        next_part_url = response.xpath("//a[text()='下一页']/@href").extract_first()
        if next_part_url is not None:
            next_url = "https:/" + next_part_url
            yield scrapy.Request(next_url, callback=self.parse_books, dont_filter=False)

    def parse_book(self, response):
        # 获取图书的详情信息
        item = response.meta["item"]
        item["book_name"] = response.xpath("//div[@id='name']/div[@class='sku-name']/text()").extract_first()
        item["book_author"] = response.xpath("//div[@id='p-author']/a/@data-name").extract_first()
        # 获取价格地址(由js生成)
        book_id = response.xpath("//a[@id='choose-btn-coll']/@data-id").extract_first()
        if book_id is not None:
            book_price_url = "https://p.3.cn/prices/mgets?skuIds=J_" + book_id
            yield scrapy.Request(book_price_url, callback=self.parse_price, meta={"item": deepcopy(item)},
                                 dont_filter=False)

    def parse_price(self, response):
        """
        获取图书价格
        :param response:
        :return:
        """
        item = response.meta["item"]
        item["book_price"] = json.loads(response.body.decode())[0]["op"]
        yield item
