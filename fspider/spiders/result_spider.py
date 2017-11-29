# -*- coding: utf-8 -*-
import scrapy
from .. import YDHP_ScrapyRequester
import json
import requests
import parsel
from ..items import FspiderItem
from scrapy.utils.response import open_in_browser


# scrapy crawl result_spider -o result.json -t json -a keyword=<keyword> -a total_pages=<how many page your want to scrape>
class ResultSpiderSpider(scrapy.Spider):
    name = 'result_spider'
    allowed_domains = ['oasm.finanstilsynet.dk']

    def __init__(self, keyword=None, total_pages=None, *args, **kwargs):
        super(ResultSpiderSpider, self).__init__()

        self.requester = YDHP_ScrapyRequester.ScrapyRequester()
        if keyword is None:
            self.keyword = "Ledende medarbejderes og nærtståendes transaktioner"
        else:
            self.keyword = str(keyword)
        if total_pages is None:
            self.total_pages = str(100)
        else:
            self.total_pages = str(total_pages)
        self.ps = "10"
        self.publication = "%28pubafter:2007%2f6%2f01%20and%20pubbefore:2017%2f12%2f31%29"

    def start_requests(self):
        for page in range(0, int(self.total_pages)):
            # 拼装url
            url = "https://oasm.finanstilsynet.dk/Reserved/SearchSSS.aspx?"
            url += \
                "?t=%s&p=%s&ps=%s&publication=%s" % (self.keyword, str(page), self.ps, self.publication)
            yield self.requester.scrapy_requests(url, self.parse)

    def parse(self, response):
        open_in_browser(response)
        json_obj = json.loads(response.body_as_unicode())

        # 从json获得搜索结果
        spider_item = FspiderItem()
        for result in json_obj['ResultSet']:
            spider_item['title'] = result['IndexedFields']['title']['Value']
            spider_item['data_of_transaction'] = result['IndexedFields']['publicationdatetime']['Value']
            spider_item['name_of_company'] = result['IndexedFields']['announcercompany']['Value']

            # 从json获得交易文档下载地址
            transaction_detail_page_url = result['IndexedFields']['showurlen']['Value']
            detail_page_response = requests.get(transaction_detail_page_url)
            document_urls = parsel.Selector(text=detail_page_response.text).xpath\
                ("""//div[@class="pagecontent"]//div[@class="data"]/ul/li/div/a/@href""").extract()
            spider_item['transaction_documents'] = []
            for url in document_urls:
                spider_item['transaction_documents'].append("https://oasm.finanstilsynet.dk/dk/vismeddelelse.aspx"+url)

            yield spider_item






