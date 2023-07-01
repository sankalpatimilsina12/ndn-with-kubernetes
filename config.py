import sys
import logging
from enum import Enum

DEBUG = True

class SUPPORTED_APP_PARAMS(Enum):
    MEM = 1
    CPU = 2
    DISK = 3
    DOCKER = 4

# LOG
LOGGER = logging.getLogger('NDN_K8S')
LOGGER.setLevel(logging.DEBUG if DEBUG else logging.INFO)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
LOGGER.addHandler(_console_handler)
LOGGER.propagate = False