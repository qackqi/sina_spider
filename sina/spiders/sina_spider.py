# -*- coding: utf-8 -*-
import scrapy
import re
import requests
from sina.items import SinaItem

class SinaSpiderSpider(scrapy.Spider):
    name = 'sina_spider'
    allowed_domains = ['m.weibo.cn']
    start_urls = ['https://s.weibo.com/top/summary']
    r = requests.get("https://s.weibo.com/top/summary")
    r.encoding = 'utf-8'
    html = r.text
    base_url1 = 'https://m.weibo.cn/api/container/getIndex?containerid=231522type%3D1%26q%3D%23'
    base_url2 = '&page_type=searchall'
    base_newurl = 'https://m.weibo.cn/detail/'
#    name = re.findall(r'target=\"_blank\">.*?</a>',r.text)

    def parse(self, response):
        name = response.xpath("//div[@id='pl_top_realtimehot']//td[@class='td-02']/a/text()")
        for url in name:
            try:
                jsonurl = self.base_url1 + url.get() + self.base_url2
                r = requests.get(jsonurl)
                result = re.search(r'\"id\":\"\d{16}\"', r.text)
                id = eval(result.group(0).split(":")[1])
                newurl = self.base_newurl + id
                yield scrapy.Request(newurl, callback = self.parse_stock)
            except:
                print("失败。")
                continue

    def parse_stock(self, response):
        html = response.body.decode('utf-8')
        result = re.search(r'\"text\": \".*\",\n', html)
        result2 = re.search(r'\"screen_name\": \".*?\"', html)
        author = eval(result2.group(0).split(':')[1])
        html = result.group(0)[9:-3]
        new_html = "".join((re.sub("\n", " ", html)).split(" "))
        content = re.sub('<.*?>', '', new_html)
        item = SinaItem(author = author, content = content)
        yield  item