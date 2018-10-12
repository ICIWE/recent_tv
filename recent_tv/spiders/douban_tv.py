# -*- coding: utf-8 -*-
import scrapy
import json
import re
import copy
from scrapy import Request


class DoubanTvSpider(scrapy.Spider):
    name = 'douban_tv'
    allowed_domains = ['movie.douban.com']
    page_limit = 20
    page_start = 0
    base_url = 'https://movie.douban.com/j/search_subjects?type=tv&tag=' \
                '%E7%83%AD%E9%97%A8&sort=time&page_limit={}&page_start={}'
    start_urls = [base_url.format(page_limit, page_start)]

    def parse(self, response):

        resp = json.loads(response.body.decode('utf-8'))
        for item in resp['subjects']: 

            # tv_item 初始化。必须在for 循环内，因为meta 参数的值被获取后，会删除，需要每次传递时初始化
            tv_item = {}                        
            url = item['url']
            tv_item['评分'] = item['rate']
            tv_item['片名'] = item['title']
            tv_item['豆瓣链接'] = url

            yield Request(url, callback=self.parse_page, 
                meta={'_item': tv_item})

        # 获取下一页，直到响应为空
        # if resp['subjects']:
        #     self.page_start += self.page_limit
        #     url = self.base_url.format(self.page_limit, self.page_start)
        #     yield Request(url, callback=self.parse)

    def parse_page(self, response):
        # 从meta中提取字段数据
        tv_item = response.meta['_item']

        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        node = response.css("div#info")
        # 先提取所有信息字段（因为字段容易读取，值比较乱）
        pl = [s.replace(':', '') for s in node.xpath(".//span[@class='pl']/text()").extract()]
        # 节点下所有的文本
        info = node.xpath('string(.)').extract_first()
        # 用字段名分割文本，并去除空格、换行，组成列表
        # 主要用到 re.split('par1|par2|par3', string) ,用par1或par2或par3分割
        values = [s.strip() for s in re.split(':|'.join(pl)+':', info)][1:]

        # 将提取的信息汇入 tv_item 字典中
        tv_item['详情'] = dict(zip(pl, values))
        # tv_item.update(dict(zip(pl, values)))

        # 前面爬取了电视剧所有季数，现在替换成当前季数
        tv_item['详情']['季数'] = node.xpath('.//option[@selected="selected"]/text()').extract_first()
        # 电视剧 ID
        tv_item['id'] = re.findall('subject/(\d+)/',response.url)[0]
        # 查看豆瓣提供的视频源
        node_source = response.css('div.gray_ad')
        if node_source:
            source = node_source.xpath(".//a//text()").extract()
            tv_item['播放源'] = ''.join([s.strip() for s in source])
        else:
            tv_item['播放源'] = None

        yield tv_item