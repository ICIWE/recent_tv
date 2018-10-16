# -*- coding: utf-8 -*-

import requests
import re
import pymysql
import logging
from bs4 import BeautifulSoup


class FindTV(object):
    def __init__(self):
        self.proxies = None
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}

    def find_from_tencent(self, name):
        # 在腾讯视频寻找 电视剧
        base_url = 'https://v.qq.com/x/search/?q=%s'
        url = base_url % name

        resp = resp = requests.get(url, timeout=5, headers=self.headers, proxies=self.proxies)
        soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
        tag = soup.select_one('h2.result_title a[href]')
        tag2 = soup.select_one('h2.result_title a em')
        tv_name = tag2.get_text()
        link = tag['href']

        if tv_name is None or link is None:
            return 
        return tv_name, link

    def find_from_iqiyi(self, name):
        # 在爱奇艺寻找 电视剧
        base_url = 'https://so.iqiyi.com/so/q_%s?source=input'
        url = base_url % name

        resp = requests.get(url, timeout=5, headers=self.headers, proxies=self.proxies)
        soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
        tag = soup.select_one('h3.result_title a["href"]')
        tv_name = tag.get_text().strip()
        link = tag['href']

        if tv_name is None or link is None:
            return 
        return tv_name, link

    def find_from_youku(self, name):
        # 在优酷寻找 电视剧
        base_url = 'https://so.youku.com/search_video/q_%s'
        url = base_url % name
        resp = requests.get(url, timeout=5, headers=self.headers, proxies=self.proxies)
        string = resp.content.decode('utf-8')

        result = re.search('dtitle.*?title=\\\\"(.+?)\\\\"  href.*?(http.+?html)', string)

        if result is None:
            return
        tv_name = result.group(1)
        link = result.group(2)

        if tv_name is None or link is None:
            return 
        return tv_name, link

    def ip(self):
        # 查看当前使用的ip 地址，返回ip 地址
        # 备用
        url = 'https://www.baidu.com/s?wd=ip'
        resp = requests.get(url, timeout=5, headers=headers, proxies=proxies)
        soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
        tag = soup.find_all(text=re.compile('本机IP.*?(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})'))[0]
        ip = re.findall('(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', tag)[0]
        return ip


class Save(object):
    def __init__(self):
        self.sql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '0000',
            'db': 'oo',
            'charset': 'utf8mb4'  
            }
        self.table = 'tv_source'

    def create_table(self):

        sql = '''CREATE TABLE IF NOT EXISTS {}(
            id  int(11) primary key,
            片名 varchar(30),
            腾讯视频 text,
            爱奇艺视频 text,
            优酷视频 text,
            其他  text
            )
            '''.format(self.table)
        try:
            self.cur.execute(sql)
        except Exception as e:
            logging.error('数据库表格创建失败:%s' %e)

    def insert_item(self, item):
        if item is None or len(item) == 0:
            return
        data = [
            item.get('id'),
            item.get('片名'),
            item.get('腾讯视频'),
            item.get('爱奇艺视频'),
            item.get('优酷视频'),
            item.get('其他')
        ]
        key = ','.join(['%s']*len(data))
        sql = 'INSERT INTO {} values({})'.format(self.table, key)
        try:
            if self.cur.execute(sql, data):
                self.conn.commit()
                logging.info('数据 %s已存入数据库，表格%s' %(item.get('id'), self.table))
        except Exception as e:
            logging.info('%s 存入失败：%s' %(item.get('id'), e))
            self.conn.rollback()

    def _connect_sql(self):
        self.conn = pymysql.connect(**self.sql_config)
        self.cur = self.conn.cursor()
    
    def _close_sql(self):
        self.conn.close()
       

class LoadTV(object):
    def __init__(self):
        self.sql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '0000',
            'db': 'oo',
            'charset': 'utf8mb4'  
            }
        self.table = 'tv'           #  电视剧储存的表格

    def load_tv(self):
        sql = 'SELECT id, 片名 FROM {}'.format(self.table)
        try:
            self.cur.execute(sql)
            results = self.cur.fetchall()
        except Exception as e:
            logging.info('发生错误: %s' % e)
            print(e)
            return
        else:
            logging.info('电视剧信息读取完成，准备搜索 ...')
            return results

    def _connect_sql(self):
        self.conn = pymysql.connect(**self.sql_config)
        self.cur = self.conn.cursor()
    
    def _close_sql(self):
        self.conn.close()


def main():
    item = {}
    load_tv = LoadTV()
    find_tv = FindTV()
    save = Save()

    load_tv._connect_sql()
    tv_i = load_tv.load_tv()
    load_tv._close_sql()

    save._connect_sql()
    save.create_table()
    for row in tv_i:
        logging.info('正在查找：%s' %row[1])
        result_t = find_tv.find_from_tencent(row[1])
        result_i = find_tv.find_from_iqiyi(row[1])
        result_y = find_tv.find_from_youku(row[1])

        if result_t is None:
            item['腾讯视频'] = None
        else:
            item['腾讯视频'] = '|'.join(result_t)

        if result_i is None:
            item['爱奇艺视频'] = None
        else:
            item['爱奇艺视频'] = '|'.join(result_i)

        if result_y is None:
            item['优酷视频'] = None
        else:
            item['优酷视频'] = '|'.join(result_y)

        item['id'] = row[0]
        item['片名'] = row[1]
        item['其他'] = None
        save.insert_item(item)
    logging.info('搜索并保存完毕')
    save._close_sql()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()