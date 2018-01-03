#! coding:utf-8
import json
import redis
import random
from .settings import agents
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware #UserAegent中间件
from scrapy.downloadermiddlewares.retry import RetryMiddleware #重试中间件


class UserAgentmiddleware(UserAgentMiddleware):

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent