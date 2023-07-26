import sys
import time

from ndn.app import NDNApp
from ndn.types import FormalName, InterestParam, BinaryStr

from .settings import LOGGER, GATEWAY_ROUTES


class Gateway:
    def __init__(self) -> None:
        # Wait for NFD to start
        time.sleep(5)
        self.app = NDNApp()

        try:
            self.app.run_forever(after_start=self._run())
        except (FileNotFoundError, ConnectionRefusedError):
            LOGGER.error('Could not connect to NFD. Is NFD running?')
            sys.exit()

    async def _run(self) -> None:
        LOGGER.info('Gateway running...')
        self.app.route(GATEWAY_ROUTES['COMPUTE_REQUEST'])(
            self._on_compute_request)

    def _on_compute_request(self, int_name: FormalName, _int_param: InterestParam, _app_param: BinaryStr):
        pass


def main():
    Gateway()


if __name__ == '__main__':
    main()
