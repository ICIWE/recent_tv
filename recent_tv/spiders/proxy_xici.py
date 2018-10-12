# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ..items import ProxyItem


class ProxyXiciSpider(scrapy.Spider):
    name = 'proxy_xici'
    allowed_domains = ['xicidaili.com']

    def start_requests(self):
        base_url = 'http://www.xicidaili.com/nn/%s'
        # 爬取前 几 页
        for i in range(5):
            url = base_url % i
            yield Request(url, callback=self.parse)

    def parse(self, response):
        # 解析代理的ip，port，scheme，并构造测试连接
        table = response.xpath("//table//tr")
        for row in table:
            # 第一行为表格标题，所以跳过
            if table.index(row) == 0:
                continue
            ip = row.xpath('.//td[2]/text()').extract_first()
            port = row.xpath('.//td[3]/text()').extract_first()
            scheme = row.xpath('.//td[6]/text()').extract_first().lower()

            # # 通过 http://httpbin.org/ip 网站检测到代理是否可用
            # url = '%s://httpbin.org/ip' % scheme

            # 通过访问豆瓣网，测试可用代理ip ，因为有些ip 已经被豆瓣封了
            url = 'https://movie.douban.com/'
            proxy = '%s://%s:%s' % (scheme, ip, port) 
            meta = {
                'proxy': proxy,
                'dont_retry': True,
                'download_timeout': 5,

                '_proxy': proxy,
                '_proxy_scheme': scheme
            }
            print('++++正在测试代理：', proxy)
            # 注意必须设置 dont_filter=True
            yield Request(url, callback=self.check_alive, meta=meta, dont_filter=True)


    def check_alive(self, response):
        if response.status == 200:
            print('===已找到一个可用代理：', response.meta['proxy'])
            proxy_dict = {
                'proxy_alive': response.meta['_proxy'],
                'scheme': response.meta['_proxy_scheme']
            }
            proxy_item = ProxyItem(proxy_dict)
            yield proxy_item

    #     # 通过response 判断到代理是否可用
    #     resp = json.loads(response.body)
    #     ip = resp["origin"]
    #     _proxy_ip = response.meta['_proxy_ip']
    #     if ip == _proxy_ip:
    #         yield {
    #                 'proxy_alive':response.meta['proxy_alive'], 
    #                 'scheme': response.meta['_proxy_scheme']
    #             }



