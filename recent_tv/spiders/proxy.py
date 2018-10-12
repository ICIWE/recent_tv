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
        for i in range(1,3):          # <<<====== 设置爬取页数
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
            # meta = {
            #     'proxy': proxy,
            #     'dont_retry': True,
            #     'download_timeout': 5,

            #     '_proxy': proxy         # 此网站未标注代理的协议类型，所以取消scheme字段
            #     '_ip': ip
            # }s
            # print('++++正在测试代理：', proxy)
            # # 注意必须设置 dont_filter=True
            # yield Request(url, callback=self.check_alive, meta=meta, dont_filter=True)

            # 用scrapy.Request 测试，失败时好多Traceback，看着心烦，所以用改 requests模块
            proxy_item = self.check_and_duplicate(url, proxy, scheme)

            if proxy_item:
                yield proxy_item

        # 爬取前 几 页,，此网站又连续访问检测，在下载时需延时
        if self.page_kuai < 4:  # <<<====== 设置爬取页数
            time.sleep(10)
            self.page_kuai += 1
            url_kuai = self.base_url_kuak % self.page_kuai
            yield Request(url_kuai, callback=self.parse_kuai)
        
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

            url = 'https://movie.douban.com/'
            proxy = '%s://%s:%s' % (scheme, ip, port) 
            # meta = {
            #     'proxy': proxy,
            #     'dont_retry': True,
            #     'download_timeout': 5,

            #     '_proxy': proxy,
            #     '_proxy_scheme': scheme
            #     '_ip': ip
            # }
            # print('++++正在测试代理：', proxy)
            # 注意必须设置 dont_filter=True
            # yield Request(url, callback=self.check_alive, meta=meta, dont_filter=True)
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

        # if response.status == 200:
        #     print('===已找到一个可用代理：', response.meta['proxy'])
            # proxy_dict = {
            #     'proxy_alive': response.meta['_proxy'],
            #     'scheme': 'https'       # 代理类型都按https 处理
            # }
            # proxy_item = ProxyItem(proxy_dict)
            # yield proxy_item