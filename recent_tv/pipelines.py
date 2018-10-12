# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymysql
from .settings import HTTPPROXY_FILE as httpproxy_file
from scrapy.exporters import JsonItemExporter
from scrapy.exceptions import NotConfigured


class RecentTvPipeline(object):
    ''' 将douban_tv 爬取的电视剧信息，保存至MySQL数据库。 '''
    def __init__(self, settings, status):
        self.status = status
        if settings == None:
            NotConfigured

        self.attrs = settings
        self.table = 'tv'
        self.item_list = set()

    def open_spider(self, spider):
        if self.status == False:
            return

        # 直接传入词典参数有问题
        self.conn = pymysql.connect(
            host=self.attrs.get('host'),
            user=self.attrs.get('user'),
            password=self.attrs.get('password'),
            db=self.attrs.get('db'),
            charset=self.attrs.get('charset')
            )
        self.cur = self.conn.cursor()
        sql = '''CREATE TABLE IF NOT EXISTS {}(
            id  int(11) primary key,
            评分 float(2,1),
            片名 varchar(30),
            豆瓣链接 varchar(60),
            播放源  varchar(30),
            导演  varchar(30),
            主演 varchar(500),
            类型  varchar(20),
            制片国家地区 varchar(20),
            语言 varchar(20),
            首播  varchar(20),
            季数  int(2),
            集数  int(4),
            单集片长 varchar(10),
            又名  varchar(50),
            IMDb链接 varchar(30)
            )
            '''.format(self.table)
        try:
            self.cur.execute(sql)
        except Exception as e:
            print(e)

    def close_spider(self, spider):
        if self.status == False:
            return
        self.conn.close()
        print('爬取完成，共保存%s 条记录。'% len(self.item_list))

    @classmethod
    def from_crawler(cls, crawler):
        # douban_tv爬虫的专用管道
        if crawler is not None and crawler.spider.name == 'douban_tv':
            status = True
            settings = crawler.settings.get('MYSQL_SETTINGS', None)
        else:
            status = False
            settings = None
        
        return cls(settings, status)

    def process_item(self, item, spider):
        if self.status == False:
            return item
        self._str2num(item)

        if not item.get('id') in self.item_list:
            if self._insert_value(item):
                self.item_list.add(item.get('id'))
        
        return item

    def _insert_value(self, item):
        # 保存item至数据库，每一条item 保存一次
        table = self.table
        data = [
            item.get('id'),
            item.get('评分'),
            item.get('片名'),
            item.get('豆瓣链接'),
            item.get('播放源'),
            item.get('详情').get('导演'),
            item.get('详情').get('主演'),
            item.get('详情').get('类型'),
            item.get('详情').get('制片国家/地区'),
            item.get('详情').get('语言'),
            item.get('详情').get('首播'),
            item.get('详情').get('季数'),
            item.get('详情').get('集数'),
            item.get('详情').get('单集片长'),
            item.get('详情').get('又名'),
            item.get('详情').get('IMDb链接')
        ]
        values = ','.join(['%s']*len(data))
        sql = 'INSERT INTO {table} values({values})'.format(table=table, values=values)
        try:
            if self.cur.execute(sql, data):
                print('数据已存入：', item.get('id'))
                self.conn.commit()
        except Exception as e:
            print('数据存入失败', item.get('id'))
            print(e)
            self.conn.rollback()
            return  False
        return True

    def _str2num(self, item):
        # 一些字符串字段转换成数字类型
        if item.get('id'):
            item['id'] = int(item.get('id'))
        if item.get('评分'):
            item['评分'] = float(item.get('评分'))
        if item.get('季数'):
            item['季数'] = int(item.get('季数'))
        if item.get('集数'):
            item['集数'] = item.get('集数')
        return item


class ProxyPipeline(object):
    def open_spider(self, spider):
        if spider.name not in  ['proxy_xici','proxy_kuai']:
            return
        proxy_file = httpproxy_file
        self.file = open(proxy_file, 'wb')
        self.exporter = JsonItemExporter(self.file, indent=0)   # 每一个item一行，无缩进
        self.exporter.start_exporting()

    def close_spider(self, spider):
        if spider.name not in  ['proxy_xici','proxy_kuai']:
            return
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        if spider.name not in  ['proxy_xici','proxy_kuai']:
            return item
        self.exporter.export_item(item)
        return item 