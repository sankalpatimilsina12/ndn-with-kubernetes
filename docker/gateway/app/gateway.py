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

from typing import Union, Tuple

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

    def _extract_app_params(self, _app_param: BinaryStr) -> Tuple[bool, Union[bytes, dict]]:
        _app_param = json.loads(_app_param.tobytes())

        # Validation
        if 'mem' in _app_param:
            try:
                _app_param['mem'] = int(_app_param['mem'])
            except ValueError:
                return False, b'Invalid memory requirement'
        if 'cpu' in _app_param:
            try:
                _app_param['cpu'] = int(_app_param['cpu'])
            except ValueError:
                return False, b'Invalid cpu requirement'
        if 'disk' in _app_param:
            try:
                _app_param['disk'] = int(_app_param['disk'])
            except ValueError:
                return False, b'Invalid disk requirement'
        if _app_param['application'] not in SUPPORTED_IMAGES:
            return False, f'Application `{_app_param["application"]}` not supported. Supported applications: {", ".join(SUPPORTED_IMAGES.keys())}'.encode()

        for k, v in SUPPORTED_APP_PARAMS.items():
            if k not in _app_param:
                _app_param[k] = v
        return True, _app_param

    def _on_compute_request(self, int_name: FormalName, _int_param: InterestParam, _app_param: BinaryStr):
        LOGGER.info(f'Received interest: {Name.to_str(int_name)}')

        valid, _app_param = self._extract_app_params(_app_param)
        if not valid:
            self.app.put_data(int_name, _app_param, freshness_period=3000)
            return

        # Create a job object
        job = create_job_object(f'job-{int(time.time())}', _app_param)

        # Respond
        self.app.put_data(int_name, b'Hello World', freshness_period=3000)


def main():
    Gateway()


if __name__ == '__main__':
    main()
