# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup


proxies = None
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}

def find_from_tencent(name):
    # 在腾讯视频寻找 电视剧
    base_url = 'https://v.qq.com/x/search/?q=%s'
    url = base_url % name

    resp = resp = requests.get(url, timeout=5, headers=headers, proxies=proxies)
    soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    tag = soup.select_one('h2.result_title a[href]')
    tag2 = soup.select_one('h2.result_title a em')
    tv_name = tag2.get_text()
    link = tag['href']
    return tv_name, link

def find_from_iqiyi(name):
    # 在爱奇艺寻找 电视剧
    base_url = 'https://so.iqiyi.com/so/q_%s?source=input'
    url = base_url % name

    resp = requests.get(url, timeout=5, headers=headers, proxies=proxies)
    soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    tag = soup.select_one('h3.result_title a["href"]')
    tv_name = tag.get_text().strip()
    link = tag['href']
    return tv_name, link

def find_from_youku(name):
    # 在优酷寻找 电视剧
    base_url = 'https://so.youku.com/search_video/q_%s'
    url = base_url % name
    resp = requests.get(url, timeout=5, headers=headers, proxies=proxies)
    string = resp.content.decode('utf-8')

    result = re.search('dtitle.*?title=\\\\"(.+?)\\\\"  href.*?(http.+?html)', string)
    tv_name = result.group(1)
    link = result.group(2)

    return tv_name, link

def ip():
    # 查看当前使用的ip 地址，返回ip 地址
    url = 'https://www.baidu.com/s?wd=ip'
    resp = requests.get(url, timeout=5, headers=headers, proxies=proxies)
    tag = soup.find_all(text=re.compile('本机IP.*?(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})'))[0]
    ip = re.findall('(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', tag)[0]
    return ip


if __name__ == '__main__':
    name = input('请输入电视剧名：')
    print('正在查找 ...')
    tv_name, link = find_from_tencent(name)
    if tv_name and link:
        print('---来自腾讯视频---')
        print(tv_name, link)
    tv_name, link = find_from_iqiyi(name)
    if tv_name and link:
        print('---来自爱奇艺视频---')
        print(tv_name, link)
    tv_name, link = find_from_youku(name)
    if tv_name and link:
        print('---来自优酷视频---')
        print(tv_name, link)