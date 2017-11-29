# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class FspiderItem(Item):
    title = Field()
    data_of_transaction = Field()
    name_of_company = Field()
    transaction_documents = Field()

