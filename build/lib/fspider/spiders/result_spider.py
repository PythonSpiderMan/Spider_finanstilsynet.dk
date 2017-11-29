# -*- coding: utf-8 -*-
import scrapy
from .. import YDHP_ScrapyRequester
import json
import requests
import parsel
from ..items import FspiderItem


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
        url = "https://oasm.finanstilsynet.dk/Reserved/SearchSSS.aspx?"
        for page in range(0, int(self.total_pages)):
            # 拼装url
            url += \
                "?t=%s&p=%s&ps=%s&publication=%s" % (self.keyword, str(page), self.ps, self.publication)
            yield self.requester.scrapy_requests(url, self.parse)

    def parse(self, response):
        json_obj = json.loads(response.text)

        # 从json获得搜索结果
        spider_item = FspiderItem()
        for result in json_obj['ResultSet']['IndexedFields']:
            spider_item['title'] = result['title']['Value']
            spider_item['data_of_transaction'] = result['publicationdatetime']['Value']
            spider_item['name_of_company'] = result['announcercompany']['Value']

        # 从json获得交易文档下载地址
        transaction_detail_page_url = result['showurlen']['Value']
        detail_page_response = requests.get(transaction_detail_page_url)
        document_urls = parsel.Selector(text=detail_page_response.text).xpath\
            ("""xpath = //div[@class="pagecontent"]//div[@class="data"]/ul/li/div/a/@href""")
        spider_item['transaction_documents'] = []
        for url in document_urls:
            spider_item['transaction_documents'].append(response.urljoin(url))

        yield spider_item






