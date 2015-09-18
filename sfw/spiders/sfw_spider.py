from scrapy import Spider, Request, FormRequest, Selector
from sfw.items import SfwItem
from sfw.mogno_service import MongoService
import urllib

"""
Check duplicates:
db.photos.aggregate(
    { $group: {
        _id: { photo_url: "$photo_url" },
        count: { $sum:  1 },
        docs: { $push: "$_id" }
    }},
    { $match: {
        count: { $gt : 1 }
    }}
)
"""
class SFW_Spider(Spider):
    name = 'sfw'
    allowed_domains = ['sfw.so']
    start_urls = ['http://sfw.so/']
    girls_url = 'http://sfw.so/girls/'
    girls_url_pattern = 'http://sfw.so/girls/page/{0}/'
    photo_url_pattern = 'http://sfw.so'
    photos_hard_drive_path = '/Users/sashko/Documents/sfw_photos/{0}_{1}.jpg'
    # photos_hard_drive_path = '/Volumes/SP PHD U3/sfw_photos/{0}_{1}.jpg'
    mongo = MongoService()
    # xpath
    last_page_xpath = '//a[starts-with(@href, "http://sfw.so/girls/page/")]/text()'
    posts_list_xpath = '//div[@class="short_title"]/a/@href'
    images_list_xpath2 = '//div[starts-with(@id, "news-id-")]/div[1]/img/@src'
    images_list_xpath = '//img[starts-with(@src, "/uploads/posts/") and not(contains(@src, ".gif")) and not(contains(@src, "_logo.jpg")) ]/@src'

    def start_requests(self):
        yield Request(url='http://sfw.so/', callback=self.login)

    def login(self, response):
        return FormRequest.from_response(response, formdata={'login': 'submit', 'login_name': 'Falcone',
                                                             'login_password': 'x7yhe7af01c'},
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        yield Request(url=self.girls_url, dont_filter=True, callback=self.open_girls)

    def open_girls(self, response):
        xhs = Selector(response)
        pages_amount = xhs.xpath(self.last_page_xpath).extract()[-1]
        for i in range(1, int(pages_amount) + 1):
            yield Request(url=self.girls_url_pattern.format(i), callback=self.parse_page, dont_filter=True)

    def parse_page(self, response):
        xhs = Selector(response)
        posts_links = xhs.xpath(self.posts_list_xpath).extract()
        for link in posts_links:
            yield Request(url=link, callback=self.parse_post, dont_filter=True)

    def parse_post(self, response):
        xhs = Selector(response)
        photos_list = xhs.xpath(self.images_list_xpath).extract()
        if not photos_list:
            photos_list = xhs.xpath(self.images_list_xpath2)
        if not photos_list:
            self.mongo.save_empty_post(response.url)
        if self.mongo.check_post(response.url, len(photos_list)):
            return
        post_id = response.url.split('-')[0].split('/')[3]
        for i, photo_url_end in enumerate(photos_list):
            photo_link = self.photo_url_pattern + photo_url_end
            if not self.mongo.check_photo(photo_link):
                continue
            photo_path = self.photos_hard_drive_path.format(post_id, i)
            urllib.urlretrieve(photo_link, photo_path)
            item = SfwItem()
            item['photo_url'] = photo_link
            item['post_url'] = response.url
            item['file_name'] = photo_path
            self.mongo.process_item(item, self)
