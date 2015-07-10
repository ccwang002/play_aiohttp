import colorlog
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

try:
    from pip._vendor.progress.bar import ShadyBar  # or IncrementalBar
except ImportError:
    # for pip < 6.0, no fancy progressbar is given
    # We build our own
    class ShadyBar(object):

        def __init__(self, *args, **kwargs):
            logger.error('progress bar requires pip 6.0+')
            self.description = ''
            self.index = 0
            self.max = kwargs.get('max', 100)

        def next(self, n=1):
            self.index += n
            self.update()

        def update(self):
            step = self.max // 10 or 1
            percentage = self.index / self.max * 100
            if self.index % step == 0:
                logger.info('Progess %04.1f%% reached' % percentage)

        def finish(self):
            logger.info('Progress done')
def colorify_log_handler(
        log_handler, log_lineno=True,
        time_fmt='%y-%m-%d %H:%M:%S', log_fmt=None
):
    """Helper function to setup colored log handler.


    Parameters
    ----------
    log_handler : logging.Handler
        The handler to be configured

    log_lineno : bool, True
        True will output the code lineno of the function if available.
        In IPython logging this is useless.

    time_fmt : str
        The time formatter passed to %(asctime)s using available fields
        given in strftime().

    log_fmt : str
        Override the builtin logging format. This option will make
        log_lineno useless.


    Notes
    -----
    It is usually used in console-like ouptut, e.g., stderr or IPython logging.
    For file log handler one should consider using plain text.


    Examples
    --------
    Quick plug-n-play setup for console logging which captures all existed
    logging events.

        >>> logger = logging.getLogger()
        >>> logger.setLevel(logging.DEBUG)  # capture all emitted events
        >>> ch = logging.StreamHandler()  # default goes to stderr
        >>> colorify_log_handler(ch)
        >>> logger.addHandler(ch)

    """
    if log_fmt is None:
        log_fmt = (
            '%(log_color)s%(asctime)s.%(msecs)d %(levelname).1s%(reset)s '
        )
        if log_lineno:
            log_fmt += '%(cyan)s[%(name)s %(funcName)s:%(lineno)d]%(reset)s '
        else:
            log_fmt += '%(cyan)s[%(name)s %(funcName)s]%(reset)s '
        log_fmt += '%(message)s'
    log_formatter = colorlog.ColoredFormatter(
        log_fmt,
        time_fmt,
        log_colors={
            'DEBUG': 'fg_white',
            'INFO': 'fg_bold_green',
            'WARNING': 'fg_bold_yellow',
            'ERROR': 'fg_bold_red',
            'CRITICAL': 'fg_bold_red',
        },
    )
    log_handler.setFormatter(log_formatter)


class ProgressBar(ShadyBar):
    message = "%(description)s"
    suffix = "%(percent).1f%% eta %(eta)s s"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = ''
