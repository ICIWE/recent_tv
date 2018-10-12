# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy import Request
from ..items import ProxyItem


class ProxyKuaiSpider(scrapy.Spider):
    name = 'proxy_kuai'
    allowed_domains = ['kuaidaili.com']
    page = 1
    base_url = 'https://www.kuaidaili.com/free/inha/%s/'

    def start_requests(self):

        start_url = self.base_url % self.page
        yield Request(start_url, callback=self.parse)

    def parse(self, response):
        # 解析代理的ip，port 并构造测试连接
        table = response.xpath("//table//tbody/tr")
        for row in table:
            ip = row.xpath('.//td[1]/text()').extract_first()
            port = row.xpath('.//td[2]/text()').extract_first()

            # 通过访问豆瓣网，测试可用代理ip ，因为有些ip 已经被豆瓣封了
            url = 'https://movie.douban.com/'
            proxy = 'http://%s:%s' % (ip, port) 
            meta = {
                'proxy': proxy,
                'dont_retry': True,
                'download_timeout': 5,

                '_proxy': proxy         # 此网站未标注代理的协议类型，所以取消scheme字段
            }
            print('++++正在测试代理：', proxy)
            # 注意必须设置 dont_filter=True
            yield Request(url, callback=self.check_alive, meta=meta, dont_filter=True)

        # 爬取前 几 页
        if self.page < 5:
            time.sleep(10)
            self.page += 1
            url = self.base_url % self.page
            yield Request(url, callback=self.parse)

    def check_alive(self, response):
        if response.status == 200:
            print('===已找到一个可用代理：', response.meta['proxy'])
            proxy_dict = {
                'proxy_alive': response.meta['_proxy'],
                'scheme': 'https'       # 代理类型都按https 处理
            }
            proxy_item = ProxyItem(proxy_dict)
            yield proxy_item