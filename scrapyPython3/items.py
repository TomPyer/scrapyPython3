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
    question_launch_date = scrapy.Field()
    question_title = scrapy.Field()
    question_description = scrapy.Field()
    question_image = scrapy.Field()
    question_comment = scrapy.Field()
    question_comment_num = scrapy.Field()
    question_care_num = scrapy.Field()
    question_view_num = scrapy.Field()
    answer_count = scrapy.Field()
    pass


class ZhihuAnswerItem(scrapy.Item):
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

