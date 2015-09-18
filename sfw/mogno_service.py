import pymongo
from scrapy import log
from scrapy.conf import settings


class MongoService():
    def __init__(self):
        connection = pymongo.MongoClient(host=settings['MONGODB_SERVER'], port=settings['MONGODB_PORT'])
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        self.empty_posts_coll = db[settings['MONGODB_EMPTY_POSTS_COLL']]

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        log.msg('Item wrote to MongoDB database %s/%s' % (settings['MONGODB_DB'], settings['MONGODB_COLLECTION']), level=log.DEBUG, spider=spider)

    def check_photo(self, link):
        return self.collection.find_one({'photo_url': link}) is None

    def check_post(self, post_link, amount_of_photos):
        return self.collection.count({'post_url': post_link}) == amount_of_photos

    def save_empty_post(self, post_url):
        self.empty_posts_coll.insert({'post_url': post_url})
