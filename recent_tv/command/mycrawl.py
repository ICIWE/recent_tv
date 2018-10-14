# -*- coding: utf-8 -*-
import os
from scrapy.commands import ScrapyCommand
from scrapy.utils.conf import arglist_to_dict
from scrapy.utils.python import without_none_values
from scrapy.exceptions import UsageError


class Command(ScrapyCommand):

    requires_project = True

    def syntax(self):
        return "[options]"   # 

    def short_desc(self):
        return "Run some spiders in order"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                          help="set spider argument (may be repeated)")
        parser.add_option("-o", "--output", metavar="FILE",
                          help="dump scraped items into FILE (use - for stdout)")
        parser.add_option("-t", "--output-format", metavar="FORMAT",
                          help="format to use for dumping items with -o")

    def process_options(self, args, opts):
        ScrapyCommand.process_options(self, args, opts)
        try:
            opts.spargs = arglist_to_dict(opts.spargs)
        except ValueError:
            raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)

    def run(self, args, opts):

        spider_loader = self.crawler_process.spider_loader
        for spidername in args or spider_loader.list():
            print('----crawl %s--' % spidername)
            # if len(args) < 1:
            #     raise UsageError()
            # elif len(args) > 1:
            #     raise UsageError("running 'scrapy crawl' with more than one spider is no longer supported")
            spname = spidername
            self.crawler_process.crawl(spname, **opts.spargs)

        self.crawler_process.start()