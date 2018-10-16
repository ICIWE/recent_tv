# -*- coding: utf-8 -*-
import scrapy
import time
import requests
from scrapy import Request
from ..items import ProxyItem


class ProxySpider(scrapy.Spider):
    '''爬取xicidaili、kuaidaili 可用免费的高匿代理'''
    name = 'proxy'
    allowed_domains = ['kuaidaili.com', 'xicidaili.com']

    base_url_kuak = 'https://www.kuaidaili.com/free/inha/%s/'
    page_kuai = 1

    base_url_xici = 'http://www.xicidaili.com/nn/%s'

    # 设置爬取的页数
    page_spide = 3

    proxy_set = set()

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS' : { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0', 
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'Accept-Language': 'en;zh-CN', },
        'DOWNLOADER_MIDDLEWARES' : {
            'recent_tv.middlewares.RandomProxyMiddleware': None,
            'recent_tv.middlewares.RandomdelayMiddleware': 1}
    }

    def start_requests(self):
        # xicidaili网站初始链接
        for i in range(1, self.page_spide + 1):
            url_xici = self.base_url_xici % i
            yield Request(url_xici, callback=self.parse_xici)

        # # kuaidaili网站初始链接
        url_kuai = self.base_url_kuak % self.page_kuai
        yield Request(url_kuai, callback=self.parse_kuai)

    def parse_kuai(self, response):
        # 解析代理的ip，port 并构造测试连接
        table = response.xpath("//table//tbody/tr")
        for row in table:
            ip = row.xpath('.//td[1]/text()').extract_first()
            port = row.xpath('.//td[2]/text()').extract_first()

            # 通过访问豆瓣网，测试可用代理ip ，因为有些ip 已经被豆瓣封了
            url = 'https://movie.douban.com/'
            proxy = 'https://%s:%s' % (ip, port) 
            scheme = 'https'

            proxy_item = self.check_and_duplicate(url, proxy, scheme)

            if proxy_item:
                yield proxy_item

        # 爬取前 几 页,，此网站又连续访问检测，在下载时使用延时的下载中间件
        if self.page_kuai < self.page_spide:
            self.page_kuai += 1
            url_kuai = self.base_url_kuak % self.page_kuai
            yield Request(url_kuai, callback=self.parse_kuai)
        
    def parse_xici(self, response):
        # 解析代理的ip，port，scheme，并构造测试连接
        table = response.xpath("//table//tr")
        for row in table:
            
            if table.index(row) == 0:
                continue
            ip = row.xpath('.//td[2]/text()').extract_first()
            port = row.xpath('.//td[3]/text()').extract_first()
            scheme = row.xpath('.//td[6]/text()').extract_first().lower()

            url = 'https://movie.douban.com/'
            proxy = '%s://%s:%s' % (scheme, ip, port)

            proxy_item = self.check_and_duplicate(url, proxy, scheme)

            if proxy_item:
                yield proxy_item

    def check_and_duplicate(self, url, proxy, scheme):
        print('+++正在检测代理：', proxy)
        headers = self.custom_settings['DEFAULT_REQUEST_HEADERS']

        # https,http都当作https处理
        proxies = {'https': proxy}
        try:
            resp = requests.get(url, proxies=proxies, headers=headers, timeout=2)
        except:
            return None
        else:
            if resp.status_code == 200:
                print('===已找到可用代理：', proxy)

                # 去重
                self.proxy_set.add(proxy)

                proxy_dict = {
                    'proxy_alive': proxy,
                    'scheme': 'https'
                }
                proxy_item = ProxyItem(proxy_dict)
                return proxy_item