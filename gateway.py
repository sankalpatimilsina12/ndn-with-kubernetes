import sys
from ndn.app import NDNApp
from ndn.types import FormalName, InterestParam, BinaryStr

from config import LOGGER, GATEWAY_ROUTES


class Gateway:
    def __init__(self) -> None:
        self.app = NDNApp()

        try:
            self.app.run_forever(after_start=self._run())
        except (FileNotFoundError, ConnectionRefusedError):
            LOGGER.error('Could not connect to NFD. Is NFD running?')
            sys.exit()

    async def _run(self) -> None:
        LOGGER.info('Gateway running...')
        self.app.route(GATEWAY_ROUTES['DEPLOYMENT_NOTICE'])(
            self._on_deployment_notice)
        self.app.route(GATEWAY_ROUTES['DEPLOYMENT_STATUS'])(
            self._on_deployment_status)

    def _on_deployment_notice(self, int_name: FormalName, _int_param: InterestParam, _app_param: BinaryStr):
        # parse interest
        # create deployment.yaml and apply it to k8s
        pass


    def _on_deployment_status(self, int_name: FormalName, _int_param: InterestParam, _app_param: BinaryStr):
        pass


def main():
    Gateway()


if __name__ == '__main__':
    main()
