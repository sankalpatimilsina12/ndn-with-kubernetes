import sys
import logging

DEBUG = True

SUPPORTED_APP_PARAMS = {
    'mem': 2,
    'cpu': 2,
    'disk': 5,
}

SUPPORTED_IMAGES = {
    'blast': 'ncbi/blast'
}

# LOG
LOGGER = logging.getLogger('NDN_K8S_GATEWAY')
LOGGER.setLevel(logging.DEBUG if DEBUG else logging.INFO)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
LOGGER.addHandler(_console_handler)
LOGGER.propagate = False

# PREFIXES
GATEWAY_ROUTES = {
    'compute_request': '/ndn/k8s/compute',
    'deployment_notice': '/ndn-k8s/deployment/notice',
    'deployment_status': '/ndn-k8s/deployment/status'
}
