# flake8: noqa
import aiohttp
import asyncio
from datetime import datetime
import logging
from utils import colorify_log_handler, ProgressBar

PY35_GREETINGS = '''\
For the brave ones. Welcome to Python 3.5. My greetings from 1984:

    For whom was he writing this diary?
    For the future, for the unborn.
'''


program = 'console_demo'
logger = logging.getLogger(program)
logger.setLevel(logging.DEBUG)


async def quote_with_lock(semaphore, url='http://localhost:5566/quote/uniform'):
    async with semaphore:  # equiv. to `with await semaphore`
        r = await aiohttp.request('GET', url)
        if r.status != 200:
            logger.error('Unsuccessful response [Status: %s (%d)]'
                         % (r.reason, r.status))
            r.close(force=True)
            return None
        quote_json = await r.json()
    r.close(force=True)
    return quote_json['quote']


async def quote_many(num_quotes=1, conn_limit=20, progress=None, step=10):
    if progress is None:
        progress = ProgressBar()
        progress.max = num_quotes // step

    logger.info('Process total %d quotes with max %d concurrent connections'
                % (num_quotes, conn_limit))
    logger.debug('... progress bar increment step size: %d coroutines' % step)

    semaphore = asyncio.Semaphore(conn_limit)

    coro_to_fut = asyncio.ensure_future
    futures = [
        coro_to_fut(quote_with_lock(semaphore))
        for i in range(num_quotes)
    ]

    t_start = datetime.today()
    for ith, fut in enumerate(asyncio.as_completed(futures), 1):
        if ith % step == 0:
            progress.next()
        await fut
    t_end = datetime.today()
    progress.finish()

    logger.info('All coroutines complete in {:.2f} seconds'.format(
        (t_end - t_start).total_seconds()
    ))
    quotes = [fut.result() for fut in futures]
    return quotes


def main():
    loop = asyncio.get_event_loop()
    quotes = loop.run_until_complete(
        quote_many(2000, conn_limit=100, step=20)
    )
    loop.close()
    out_pth = 'quotes.txt'
    logger.info('Write quotes to %s' % out_pth)
    with open(out_pth, 'w') as f:
        for quote in quotes:
            print(quote, file=f)
    logger.info('Done. Program ends.')


if __name__ == '__main__':
    ch = logging.StreamHandler()
    colorify_log_handler(ch, time_fmt='%H:%M:%S')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(ch)
    logger.info(PY35_GREETINGS)
    main()
