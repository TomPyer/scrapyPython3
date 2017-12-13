# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy import Selector, Request


class FirstspiderSpider(scrapy.Spider):
    name = 'firstSpider'
    # allowed_domains = ['www.baidu.com']  先注释掉,有需要再开
    start_urls = ['http://ent.ifeng.com/']  # 修改start_urls为我们需要的网址

    def parse(self, response):
        sel = Selector(response)        # 将response传给Selector生成Selector实例
        next_url = sel.xpath('//ul[@class="clearfix"]/li[3]/a/@href').extract()     # 娱乐版块下的电影版块链接
        yield Request(next_url, self.next_parse)

    def next_parse(self, response):
        sel = Selector(response)
        box_div = sel.xpath('//div[@class="box650"]/div')       # 电影相关新闻内容
        for div in box_div:
            title = div.xpath('.//h2/text()').extract()[0]
            image_url = div.xpath('.//div[@class="box_pic"]/a/img/@src').extract()[0]       # 缩略图
            content_url = div.xpath('.//div[@class="box_pic"]/a/@href').extract()[0]
            yield Request(content_url, self.content_parse, meta={'title': title, 'image_url': image_url})

    def content_parse(self, response):
        sel = Selector(response)
        meta = response.meta
        content = '\n'.join(sel.xpath('/div[@id="main_content"]/p/text()').extract())
        file_path = os.path.join('D:/tangxuelin/testfile/spiderfile', (meta['title']+'.txt'))
        with open(file_path, 'w') as f:
            f.write(content)
