import itertools
import logging
import operator
import pickle
import random
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.log
from tornado.options import define, options, parse_command_line
import tornado.web

__version__ = '2015.7'

define("port", default=9527, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("num_process", default=1, help="number of processes to fork", type=int)
define("pickle_pth", default='preprocess/parsed_1984.pkl',
       help='path to the parsed pickle file')

logger = logging.getLogger('random_quote_app')
logger.setLevel(logging.DEBUG)


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quotes = None

    def read_quotes(self, pkl_pth):
        logger.info('Reading quotes from %s' % pkl_pth)
        with open(pkl_pth, 'rb') as f:
            self.quotes = pickle.load(f)


class BaseHandler(tornado.web.RequestHandler):
    '''
    Base handler catches all error status code
    '''
    def write_error(self, status_code, **kwargs):
        self.write({
            'error': status_code,
        })

    @property
    def quotes(self):
        return self.application.quotes


class ErrorHandler(tornado.web.ErrorHandler, BaseHandler):
    """
    Default handler gonna to be used in case of 404 error

    Ref: http://stackoverflow.com/a/27108963/2016133
    """
    pass


class RootHandler(BaseHandler):

    def get(self):
        response = {
            'version': __version__,
            'env_details': {
                'quotes_pikle_pth': options.pickle_pth,
                'num_process': options.num_process,
            },
        }
        self.write(response)


class RandomQuoteHandler(BaseHandler):

    def get(self):
        effective_chapters = self.draw_chapter()
        rand_chp = random.choice(effective_chapters)
        rand_quote = random.choice(self.quotes[rand_chp])
        self.write({
            'quote': rand_quote,
            'source': {
                'part': rand_chp[0],
                'chapter': rand_chp[1],
            },
        })

    def draw_chapter(self):
        part = self.get_argument('part', None)
        chapter = self.get_argument('chapter', None)

        try:
            part = int(part) if part is not None else part
            chapter = int(chapter) if chapter is not None else chapter
        except ValueError:
            raise tornado.web.HTTPError(
                400,
                log_message='Invalid (part, chapter) given: (%r, %r)' %
                (part, chapter)
            )

        def quote_filter(t):
            p, chp = t
            if part is not None and p != part:
                return False
            if chapter is not None and chp != chapter:
                return False
            return True

        effective_chapters = list(filter(quote_filter, self.quotes.keys()))
        if not effective_chapters:
            raise tornado.web.HTTPError(
                400, log_message='None of chapters is selected'
            )
        return effective_chapters


class RandomQuoteUniformHandler(RandomQuoteHandler):

    def get(self):
        effective_chapters = self.draw_chapter()
        effecitve_quotes = list(itertools.chain.from_iterable(
            operator.itemgetter(*effective_chapters)(self.quotes)
        ))
        rand_quote = random.choice(effecitve_quotes)
        self.write({
            'quote': rand_quote,
        })


def main():
    parse_command_line()
    routing = [
        (r'^/$', RootHandler),
        (r'^/quote$', RandomQuoteHandler),
        (r'^/quote/uniform$', RandomQuoteUniformHandler),
    ]
    settings = {
        'default_handler_class': ErrorHandler,
        'default_handler_args': dict(status_code=404),
        'debug': options.debug,
    }
    app = Application(handlers=routing, **settings)
    logger.info('Application start, read quotes')
    app.read_quotes(options.pickle_pth)
    logger.info('Quotes loaded')

    # app.listen(options.port)
    server = HTTPServer(app)
    server.bind(options.port)
    server.start(options.num_process)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
