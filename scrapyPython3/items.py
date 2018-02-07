# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Scrapypython3Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class FirstSpiderItem(scrapy.Item):
    images = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    pass


class ZhihuQuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    # question_launch_date = scrapy.Field()
    question_author = scrapy.Field()
    question_title = scrapy.Field()
    question_description = scrapy.Field()
    question_image = scrapy.Field()
    question_comment = scrapy.Field()
    question_comment_num = scrapy.Field()
    question_care_num = scrapy.Field()
    question_view_num = scrapy.Field()
    answer_count = scrapy.Field()
    from_theme = scrapy.Field()
    from_theme_url = scrapy.Field()
    pass


class ZhihuAnswerItem(scrapy.Item):
    question_id = scrapy.Field()
    answer_id = scrapy.Field()
    answer_cre_date = scrapy.Field()
    answer_content = scrapy.Field()
    answer_author = scrapy.Field()
    answer_comment_num = scrapy.Field()
    answer_zan_num = scrapy.Field()
    pass


class ZhihuCommentItem(scrapy.Item):
    question_id = scrapy.Field()
    answer_id = scrapy.Field()
    is_question = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    zan_num = scrapy.Field()
    to_user = scrapy.Field()
    pass


class YzyQuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    answer_id = scrapy.Field()
    question_info = scrapy.Field()
    answer_info = scrapy.Field()
    image_url = scrapy.Field()
    question_type = scrapy.Field()
    websit = scrapy.Field()
    pass


class CgTableItem(scrapy.Item):
    table = scrapy.Field()
    year_ = scrapy.Field()
    area = scrapy.Field()
    target = scrapy.Field()
    section_ = scrapy.Field()
    value_ = scrapy.Field()
    grow_b = scrapy.Field()
    company = scrapy.Field()
    pass


class TsTableItem(scrapy.Item):
    table = scrapy.Field()
    year = scrapy.Field()
    area = scrapy.Field()
    target = scrapy.Field()
    section = scrapy.Field()
    company = scrapy.Field()
    sh_value = scrapy.Field()
    sh_grow_b = scrapy.Field()
    mc_value = scrapy.Field()
    mc_grow_b = scrapy.Field()
    zc_value = scrapy.Field()
    zc_grow_b = scrapy.Field()
    dj_bn = scrapy.Field()
    dj_sn = scrapy.Field()
    dj_grow_b = scrapy.Field()
    lj_bn = scrapy.Field()
    lj_sn = scrapy.Field()
    lj_grow_b = scrapy.Field()
    pass
