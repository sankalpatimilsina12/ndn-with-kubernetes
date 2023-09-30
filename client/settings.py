import sys
import logging

DEBUG = True

# LOG
LOGGER = logging.getLogger('NDN_K8S_CLIENT')
LOGGER.setLevel(logging.DEBUG if DEBUG else logging.INFO)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
LOGGER.addHandler(_console_handler)
LOGGER.propagate = False
