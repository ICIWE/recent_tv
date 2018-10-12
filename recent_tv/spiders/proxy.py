# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy import Request
from ..items import ProxyItem


class ProxySpider(scrapy.Spider):
    '''爬取xicidaili、kuaidaili 可用免费的高匿代理'''
    name = 'proxy'
    allowed_domains = ['kuaidaili.com', 'xicidaili.com']

    base_url_kuak = 'https://www.kuaidaili.com/free/inha/%s/'
    page_kuai = 1

    base_url_xici = 'http://www.xicidaili.com/nn/%s'

    ip_set = set()

    def start_requests(self):
        # kuaidaili网站初始链接，此网站又连续访问检测，在下载时需延时
        url_kuai = self.base_url_kuak % self.page_kuai
        yield Request(url_kuai, callback=self.parse_kuai)

        # xicidaili网站初始链接
        for i in range(5):
            url_xici = self.base_url_xici % i
            yield Request(url_xici, callback=self.parse_xici)

    def parse_kuai(self, response):
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
                '_ip': ip
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
        
    def parse_xici(self, response):
        # 解析代理的ip，port，scheme，并构造测试连接
        table = response.xpath("//table//tr")
        for row in table:
            # 第一行为表格标题，所以跳过
            if table.index(row) == 0:
                continue
            ip = row.xpath('.//td[2]/text()').extract_first()
            port = row.xpath('.//td[3]/text()').extract_first()
            scheme = row.xpath('.//td[6]/text()').extract_first().lower()

            # 通过访问豆瓣网，测试可用代理ip ，因为有些ip 已经被豆瓣封了
            url = 'https://movie.douban.com/'
            proxy = '%s://%s:%s' % (scheme, ip, port) 
            meta = {
                'proxy': proxy,
                'dont_retry': True,
                'download_timeout': 5,

                '_proxy': proxy,
                '_proxy_scheme': scheme
                '_ip': ip
            }
            print('++++正在测试代理：', proxy)
            # 注意必须设置 dont_filter=True
            yield Request(url, callback=self.check_alive, meta=meta, dont_filter=True)

    def check_and_duplicate(self, response):
        if response.status == 200:
            print('===已找到一个可用代理：', response.meta['proxy'])
            proxy_dict = {
                'proxy_alive': response.meta['_proxy'],
                'scheme': 'https'       # 代理类型都按https 处理
            }
            proxy_item = ProxyItem(proxy_dict)
            yield proxy_item