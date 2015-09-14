import scrapy
from scrapy.item import Field


class SfwItem(scrapy.Item):
    photo_url = Field()
    post_url = Field()
    file_name = Field()
