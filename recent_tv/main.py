import os
import time
import logging


if __name__ == '__main__':

    logging.info('准备执行爬虫 proxy')
    os.system("scrapy crawl proxy")
    time.sleep(2)
    logging.info('准备执行爬虫 douban_tv')
    os.system("scrapy crawl douban_tv")
    time.sleep(2)
    logging.info('准备执行爬虫 find_tv')
    os.system("python ./spiders/find_tv.py")