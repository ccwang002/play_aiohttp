# coding: utf-8
import aiohttp
import asyncio
from io import BytesIO, TextIOWrapper
import logging
import pickle
import re
import zipfile

logger = logging.getLogger('parse_1984')

@asyncio.coroutine
def get_zip(url):
    logger.debug('Downloading %s' % url)
    r = yield from aiohttp.request('get', url)
    if r.status == 200:
        zip_bytes = yield from r.read_and_close()
        logger.debug('%s downloaded' % url)
        return zip_bytes
    logger.error('Fetching url %s failed beacuse %s'
                 % (url, r.reason))
    return None

def read_zip_txt(zip_bytes):
    with zipfile.ZipFile(BytesIO(zip_bytes), 'r') as myzip:
        txt_files = [pth for pth in myzip.namelist() if pth.endswith('.txt')]
        for txt_pth in txt_files:
            with TextIOWrapper(myzip.open(txt_pth, 'r')) as txt_f:
                yield txt_f.read()

def parse_book(txt):
    start_of_part = re.compile(r'^\s*PART [A-Z]+\s*$').match
    start_of_chapter = re.compile(r'\s*Chapter [0-9]+\s*$').match
    end_of_content = re.compile(r'\s*THE END\s*$').match

    cur_part = 0
    cur_chapter = 0
    chapters = {}

    for line in txt.split('\n\n'):
        if start_of_part(line):
            if cur_part == 0:
                logger.info('Start reading the book')
                chapter_paragraphs = []
            else:
                # close last chapter of the last part
                chapters[(cur_part, cur_chapter)] = chapter_paragraphs
                chapter_paragraphs = []
                logger.debug('Closing part %d with %d chapters' %
                             (cur_part, cur_chapter))
            cur_part += 1
            cur_chapter = 0
        elif start_of_chapter(line):
            if cur_chapter > 0:
                # sotre the chapter's paragraphs
                chapters[(cur_part, cur_chapter)] = chapter_paragraphs
                chapter_paragraphs = []
            cur_chapter += 1
        elif end_of_content(line):
            # the final chapter of the final part
            # Yes, we skipped the APPENDIX
            chapters[(cur_part, cur_chapter)] = chapter_paragraphs
            logger.debug('Closing part %d with %d chpaters' %
                         (cur_part, cur_chapter))
            logger.info('Book ends')
            break
        elif cur_part > 0 and line:
            chapter_paragraphs.append(line.replace('\n', ' '))

    return chapters


def main():
    zip_1984_url = 'http://gutenberg.net.au/ebooks01/0100021.zip'

    logger.info('Downloading 1874 from %s' % zip_1984_url)
    logger.info('A reading-friendly version is available at %s' %
                'https://ebooks.adelaide.edu.au/o/orwell/george/o79n/')
    loop = asyncio.get_event_loop()
    r = loop.run_until_complete(get_zip(zip_1984_url))

    logger.info('Reading the zip')
    txt_1984 = next(read_zip_txt(r))

    logger.info('Parsing the book')
    chapters = parse_book(txt_1984)
    logger.info('Total %d chapters' % len(chapters))
    logger.debug('with chapters: %s ' % ', '.join(map(str, sorted(chapters))))
    logger.debug('Total paragraphs: %d' % sum(map(len, chapters.values())))

    out_pickle_pth = './parsed_1984.pkl'
    logger.info('Exported to pickle %s' % out_pickle_pth)
    with open(out_pickle_pth, 'wb') as f:
        pickle.dump(chapters, f)

    logger.info('Program ends')


if __name__ == '__main__':
    logging.basicConfig(
        format=(
            '%(asctime)s %(levelname).1s '
            '%(name)s [%(funcName)s:%(lineno)d] %(message)s'
        ),
        level=logging.DEBUG
    )
    main()
