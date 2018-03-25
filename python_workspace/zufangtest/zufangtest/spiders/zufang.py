#encoding: utf-8

import scrapy
from zufangtest.items import ZufangtestItem
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class GanjiSpider(scrapy.Spider):

    # 爬虫的名字，scrapy list获取到的名字
    name = "zufangtest"
    start_urls = ['http://bj.ganji.com/fang1/chaoyang/']

    def parse(self, response):
        print(response)
        zf = ZufangtestItem()
        title_list = response.xpath(".//div[@class='f-list-item ershoufang-list']/dl/dd[1]/a/text()").extract()
        money_list = response.xpath(".//div[@class='f-list-item ershoufang-list']/dl/dd[5]/div[1]/span[1]/text()").extract()
        for i,j in zip(title_list, money_list):
            # print(i + "-------------" + j)
            zf['title'] = i
            zf['money'] = j
            yield zf