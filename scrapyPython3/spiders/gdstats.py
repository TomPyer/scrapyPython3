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
        url_test_dic = {'zynzwcl': 'http://www.gdstats.gov.cn/tjsj/ny/zynzwcl/'}
        info_dic = {'gmjjzyzb': '国民经济主要指标', 'bfsszyjjzb': '部分省市主要经济指标', 'nyzcz': '广东农林牧渔业数据统计',
                    'xmysc': '广东畜牧业生产情况', 'zynzwcl': '广东主要农作物生产情况', 'zynzwbzmj': '广东主要农作物播种情况',
                    'fsjdgnsczz': '广东省各市地区生产总值', 'jdgnsczz': '广东省生产总值'}
        func_dic = {'gmjjzyzb': self.gmjjzyzb_parse, 'bfsszyjjzb': self.bfsszyjjzb_parse, 'nyzcz': self.nyzcz_parse,
                    'xmysc': self.xmysc_parse, 'zynzwcl': self.zynzwcl_parse, 'zynzwbzmj': self.zynzwbzmj_parse,
                    'fsjdgnsczz': self.fsjdgnsczz_parse, 'jdgnsczz': self.jdgnsczz_parse}
        for sx, url in url_test_dic.items():
            yield SplashRequest(url, self.page_func, meta={'name': sx, 'func': func_dic[sx], 'g_url': url,
                                                           'table': info_dic[sx]})

    def page_func(self, response):
        # 页数处理
        sel = Selector(response)
        meta = response.meta
        url = response.url
        max_page = sel.xpath('//div[@class="page"]/a/@href').extract()[-1]
        for page_num in range(int((re.findall("\d+", max_page))[0]) + 1):
            if page_num == 0:
                yield SplashRequest(url, self.get_table_url, meta=meta)
            else:
                next_url = ''.join([url, 'index_', str(page_num), '.html'])
                yield SplashRequest(next_url, self.get_table_url, meta=meta)

    def get_table_url(self, response):
        sel = Selector(response)
        meta = response.meta
        ul_obj = sel.xpath('//div[@class="main"]/ul/li')
        url_list = []
        for li in ul_obj:
            a_text = li.xpath('.//a/text()').extract_first()
            if meta['name'] == 'zynzwbzmj' and '播种面积' in a_text:
                continue
            if meta['name'] in ['gmjjzyzb', 'bfsszyjjzb'] and '12月' not in a_text:
                continue
            if meta['name'] in ['nyzcz', 'xmysc'] and ('季' in a_text and '半' in a_text):
                continue
            if meta['name'] == 'zynzwcl' and '收' in a_text:
                continue
            if meta['name'] in ['fsjdgnsczz', 'jdgnsczz'] and '4季度' not in a_text:
                continue
            try:
                meta['year'] = re.findall("\d+", a_text)[0]
            except Exception as e:
                logging.error(e)
                continue
            meta['section'] = str('1-12月')
            meta['area'] = str('广东') if meta['name'] != 'bfsszyjjzb' else str('部分省市')
            func = meta['func']
            a_url = li.xpath(".//a/@href").extract_first()[2::]
            next_url = ''.join([meta['g_url'], a_url])
            url_list.append(next_url)
            yield SplashRequest(next_url, func, meta=meta)

    def gmjjzyzb_parse(self, response):
        # 广东国民经济主要指标
        sel = Selector(response)
        meta = response.meta
        item = CgTableItem()
        table = sel.xpath('//table')
        item['year_'] = meta['year']
        item['section_'] = meta['section']
        item['area'] = meta['area']
        item['table'] = meta['table']
        if int(meta['year']) >= 2006:
            for tr in table.xpath('.//tr')[1::]:
                td = tr.xpath('.//td')
                if len(td) >= 3:
                    item['target'] = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                    item['value_'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                    item['grow_b'] = self.string_func(''.join(td[2].xpath('.//text()').extract()))
                    if (item['target']) != '指标':
                        yield item
        else:
            for tr in table.xpath('.//tr')[1::]:
                td = tr.xpath('.//td')
                if len(td) >= 6:
                    item['target'] = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                    item['company'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                    item['value_'] = self.string_func(''.join(td[3].xpath('.//text()').extract()))
                    item['grow_b'] = self.string_func(''.join(td[5].xpath('.//text()').extract()))
                    if item['target'] != '':
                        yield item

    def bfsszyjjzb_parse(self, response):
        # 部分省市主要经济指标
        sel = Selector(response)
        meta = response.meta
        item = CgTableItem()
        div_obj = sel.xpath('//div[@id="content"]')
        table = div_obj.xpath('.//table')
        if len(table) == 2:
            table = table[0]
        zhibiao = None
        item['table'] = meta['table']
        item['year_'] = meta['year']
        item['section_'] = meta['section']
        item['area'] = meta['area']
        if int(meta['year']) >= 2006:
            for tr in table.xpath('.//tr')[1::]:
                td = tr.xpath('.//td')
                if len(td) >= 2:
                    if len(self.string_func(''.join(td[0].xpath('.//text()').extract()))) > 3:
                        zhibiao = None if zhibiao else ''.join(td[0].xpath('.//text()').extract())
                        logging.warning(zhibiao)
                        continue
                    try:
                        item['target'] = self.string_func(''.join([zhibiao, '_', ''.join(td[0].xpath('.//text()').extract())]))
                        item['value_'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                        item['grow_b'] = self.string_func(''.join(td[2].xpath('.//text()').extract()))
                        yield item
                    except Exception as e:
                        logging.error(td[0].xpath('.//text()').extract())
        else:
            # 2006年以前数据不要
            pass

    def nyzcz_parse(self, response):
        # 广东农林牧渔业生产总值、增加值
        sel = Selector(response)
        meta = response.meta
        item = CgTableItem()
        div_obj = sel.xpath('//div[@class="nr"]')
        table = div_obj.xpath('.//table')
        logging.warning(table)
        item['table'] = meta['table']
        item['year_'] = meta['year']
        item['section_'] = meta['section']
        item['area'] = meta['area']
        for tr in table.xpath('.//tr')[1::]:
            td = tr.xpath('.//td')
            if len(td) >= 2:
                target = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                if len(target) != 0:
                    item['target'] = target
                    item['value_'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                    item['grow_b'] = self.string_func(''.join(td[2].xpath('.//text()').extract()))
                    logging.warning(item)
                    yield item

    def xmysc_parse(self, response):
        # 广东畜牧业生产情况
        sel = Selector(response)
        meta = response.meta
        item = CgTableItem()
        div_obj = sel.xpath('//div[@class="nr"]')
        table = div_obj.xpath('.//table')
        logging.warning(table)
        item['table'] = meta['table']
        item['year_'] = meta['year']
        item['section_'] = meta['section']
        item['area'] = meta['area']
        for tr in table.xpath('.//tr')[1::]:
            td = tr.xpath('.//td')
            if len(td) >= 2:
                target = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                if len(target) != 0 and target != '指标':
                    item['company'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                    item['target'] = target
                    item['value_'] = self.string_func(''.join(td[2].xpath('.//text()').extract()))
                    item['grow_b'] = self.string_func(''.join(td[3].xpath('.//text()').extract()))
                    logging.warning(item)
                    yield item

    def zynzwcl_parse(self, response):
        # 广东主要农作物生产情况
        sel = Selector(response)
        meta = response.meta
        item = TsTableItem()
        div_obj = sel.xpath('//div[@class="nr"]')
        table = div_obj.xpath('.//table')
        logging.warning(table)
        item['table'] = meta['table']
        item['year_'] = meta['year']
        item['section_'] = meta['section']
        item['area'] = meta['area']
        item['company'] = '万亩/公斤/万吨'
        for tr in table.xpath('.//tr')[1::]:
            td = tr.xpath('.//td')
            if len(td) >= 6:
                target = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                if len(target) != 0 and target != '指标':
                    item['target'] = target
                    item['sh_value'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                    item['sh_grow_b'] = self.string_func(''.join(td[2].xpath('.//text()').extract()))
                    item['mc_value'] = self.string_func(''.join(td[3].xpath('.//text()').extract()))
                    item['zc_value'] = self.string_func(''.join(td[4].xpath('.//text()').extract()))
                    item['zc_grow_b'] = self.string_func(''.join(td[5].xpath('.//text()').extract()))
                    logging.info(item)
                    yield item

    def zynzwbzmj_parse(self, response):
        # 广东主要农作物播种面积
        pass

    def fsjdgnsczz_parse(self, response):
        # 各市地区生产总值
        pass

    def jdgnsczz_parse(self, response):
        # 广东省生产总值
        pass

    def cg_table_func(self, response):
        # 常规表格处理
        sel = Selector(response)
        meta = response.meta
        item = CgTableItem()
        table = sel.xpath('//table')
        item['year_'] = meta['year']
        item['section_'] = meta['section']
        item['area'] = meta['area']
        item['table'] = meta['table']
        if int(meta['year']) >= 2006:
            for tr in table.xpath('.//tr')[1::]:
                td = tr.xpath('.//td')
                if len(td) >= 3:
                    item['target'] = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                    item['value_'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                    item['grow_b'] = self.string_func(''.join(td[2].xpath('.//text()').extract()))
                    if (item['target']) != '指标':
                        yield item
        else:
            for tr in table.xpath('.//tr')[1::]:
                td = tr.xpath('.//td')
                if len(td) >= 6:
                    item['target'] = self.string_func(''.join(td[0].xpath('.//text()').extract()))
                    item['company'] = self.string_func(''.join(td[1].xpath('.//text()').extract()))
                    item['value_'] = self.string_func(''.join(td[3].xpath('.//text()').extract()))
                    item['grow_b'] = self.string_func(''.join(td[5].xpath('.//text()').extract()))
                    if item['target'] != '':
                        yield item

    def ts_table_func(self, response):
        # 特殊表格处理
        pass

    @staticmethod
    def string_func(strs):
        # 字符串处理
        if strs:
            return strs.replace(' ', '').replace('\t', '').replace('\r', '').replace('\n', '').replace('&nbsp;', '')\
                .replace('\u3000', '').replace('\xa0', '')
        else:
            logging.error('string is None!!!!!!!!!!!!')
            return ''