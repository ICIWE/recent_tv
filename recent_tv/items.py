# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RecentTvItem(scrapy.Item):
    # 豆瓣电影页面解析出的字段
    评分 = scrapy.Field()
    片名 = scrapy.Field()
    豆瓣链接 = scrapy.Field()
    详情 = scrapy.Field()
    播放源 = scrapy.Field()


class ProxyItem(scrapy.Item):
    # 代理页面解析出的字段
    proxy_alive = scrapy.Field()
    scheme = scrapy.Field()