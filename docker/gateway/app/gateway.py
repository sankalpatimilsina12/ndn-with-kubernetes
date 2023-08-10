'''
This script is responsible for following sequence of actions:

1. Listen for incoming compute interests
2. Parse the interest and extract the following information:
    a. Memory requirement; if not present, default to 2GB
    b. CPU requirement; if not present, default to 2 core
    c. Disk requirement; if not present, default to 5GB
    d. Docker image name; if not present, return error
3. At this point, all the required information is present
4. Create a deployment object
'''

import json
import sys
import time

from ndn.app import NDNApp
from ndn.types import FormalName, InterestParam, BinaryStr
from ndn.encoding.name import Name
from kubernetes import client, config

from .settings import *
from .helpers import *


class Gateway:
    def __init__(self) -> None:
        # Wait for NFD to start
        # time.sleep(5)
        self.app = NDNApp()

        try:
            self.app.run_forever(after_start=self._run())
        except (FileNotFoundError, ConnectionRefusedError):
            LOGGER.error('Could not connect to NFD. Is NFD running?')
            sys.exit()

    async def _run(self) -> None:
        LOGGER.info('Gateway running...')
        self.app.route(GATEWAY_ROUTES['compute_request'])(
            self._on_compute_request)

    def _on_compute_request(self, int_name: FormalName, _int_param: InterestParam, _app_param: BinaryStr):
        LOGGER.info(f'Received interest: {Name.to_str(int_name)}')

        _app_param = json.loads(_app_param.tobytes())
        print(_app_param)

        # Create a job object
        job = create_job_object(f'job-{int(time.time())}', _app_param)

        self.app.put_data(int_name, b'Hello World', freshness_period=3000)


def main():
    Gateway()


if __name__ == '__main__':
    main()
