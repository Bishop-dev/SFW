BOT_NAME = 'sfw'

SPIDER_MODULES = ['sfw.spiders']
NEWSPIDER_MODULE = 'sfw.spiders'

RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 503, 504, 400, 404, 408]

ITEM_PIPELINES = ['sfw.pipelines.SfwPipeline']

MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'sfw'
MONGODB_COLLECTION = 'photos'
