# -*- coding: utf-8 -*-
import scrapy
import re
import logging

from scrapy import Selector, Request
from scrapy_splash import SplashRequest
from ..items import CgTableItem, TsTableItem


class GdstatsSpider(scrapy.Spider):
    name = 'gdstats'
    # allowed_domains = ['www.gdstats.gov.cn']
    start_urls = ['http://www.gdstats.gov.cn/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        url_dic = {'gmjjzyzb': 'http://www.gdstats.gov.cn/tjsj/zh/gmjjzyzb/',
                   'bfsszyjjzb': 'http://www.gdstats.gov.cn/tjsj/zh/bfsszyjjzb/',
                   'nyzcz': 'http://www.gdstats.gov.cn/tjsj/ny/nyzcz/',
                   'xmysc': 'http://www.gdstats.gov.cn/tjsj/ny/xmysc/',
                   'zynzwcl': 'http://www.gdstats.gov.cn/tjsj/ny/zynzwcl/',
                   'zynzwbzmj': 'http://www.gdstats.gov.cn/tjsj/ny/zynzwbzmj/',
                   'fsjdgnsczz': 'http://www.gdstats.gov.cn/tjsj/gmjjhs/fsjdgnsczz/',
                   'jdgnsczz': 'http://www.gdstats.gov.cn/tjsj/gmjjhs/jdgnsczz/'}
        url_test_dic = {'gmjjzyzb': 'http://www.gdstats.gov.cn/tjsj/zh/gmjjzyzb/'}
        info_dic = {'gmjjzyzb': '广东主要统计指标', 'bfsszyjjzb': '部分省市主要经济指标', 'nyzcz': '广东农林牧渔业数据统计',
                    'xmysc': '广东畜牧业生产情况', 'zynzwcl': '广东主要农作物生产情况', 'zynzwbzmj': '广东主要农作物播种情况',
                    'fsjdgnsczz': '广东省各市地区生产总值', 'jdgnsczz': '广东省生产总值'}
        func_dic = {'gmjjzyzb': self.gmjjzyzb_parse, 'bfsszyjjzb': self.bfsszyjjzb_parse, 'nyzcz': self.nyzcz_parse,
                    'xmysc': self.xmysc_parse, 'zynzwcl': self.zynzwcl_parse, 'zynzwbzmj': self.zynzwbzmj_parse,
                    'fsjdgnsczz': self.fsjdgnsczz_parse, 'jdgnsczz': self.jdgnsczz_parse}
        for sx, url in url_test_dic.items():
            yield SplashRequest(url, self.page_func, meta={'name': info_dic[sx], 'func': func_dic[sx], 'g_url': url,
                                                           'table': info_dic[sx]})

    def page_func(self, response):
        # 页数处理
        sel = Selector(response)
        meta = response.meta
        url = response.url
        max_page = sel.xpath('//div[@class="page"]/a/@href').extract()[-1]
        for page_num in range(int((re.findall("\d+", max_page))[0]) + 1):
            if page_num == 0:
                yield Request(url, meta['func'], meta=meta)
            else:
                next_url = ''.join([url, 'index_', str(page_num), '.html'])
                yield SplashRequest(next_url, meta['func'], meta=meta)

    def gmjjzyzb_parse(self, response):
        sel = Selector(response)
        meta = response.meta
        ul_obj = sel.xpath('//div[@class="main"]/ul/li')
        for li in ul_obj:
            a_text = li.xpath('.//a/text()').extract_first()
            meta['year'] = re.findall("\d+", a_text)[0]
            meta['section'] = str('1-12月')
            meta['area'] = str('广东')
            if '12月' in a_text:
                a_url = li.xpath(".//a/@href").extract_first()[2::]
                next_url = ''.join([meta['g_url'], a_url])
                yield SplashRequest(next_url, self.cg_table_func, meta=meta)

    def bfsszyjjzb_parse(self, response):
        pass

    def nyzcz_parse(self, response):
        pass

    def xmysc_parse(self, response):
        pass

    def zynzwcl_parse(self, response):
        pass

    def zynzwbzmj_parse(self, response):
        pass

    def fsjdgnsczz_parse(self, response):
        pass

    def jdgnsczz_parse(self, response):
        pass

    def cg_table_func(self, response):
        # 常规表格处理
        sel = Selector(response)
        meta = response.meta
        item = CgTableItem()
        div_obj = sel.xpath('//div[@class="TRS_PreAppend"]')
        table = div_obj.xpath('.//table[@class="MsoNormalTable"]')
        item['year_'] = meta['year']
        item['section_'] = meta['section']
        item['area'] = meta['area']
        item['table'] = meta['table']
        for tr in table.xpath('.//tr')[1::]:
            td = tr.xpath('.//td')
            if len(td) > 2:
                item['target'] = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                item['value_'] = self.string_func(td[1].xpath('.//text()').extract()[1])
                item['grow_b'] = self.string_func(td[2].xpath('.//text()').extract()[1])
                if len(item['value_']) < 5:
                    yield item

    def ts_table_func(self, response):
        # 特殊表格处理
        pass

    @staticmethod
    def string_func(strs):
        # 字符串处理
        if strs:
            return strs.replace(' ', '').replace('\t', '').replace('\r', '').replace('\n', '').replace('&nbsp;', '')
        else:
            return ''