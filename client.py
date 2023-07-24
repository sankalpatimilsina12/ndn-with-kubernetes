import sys
import json
import argparse
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name

from docker.gateway.settings import SUPPORTED_APP_PARAMS, LOGGER


class Client:
    def __init__(self, args) -> None:
        self.app = NDNApp()
        self.args = args

        try:
            self.app.run_forever(after_start=self.run())
        except (FileNotFoundError, ConnectionRefusedError):
            LOGGER.error('Could not connect to NFD. Is NFD running?')
            sys.exit()

    async def run(self):
        LOGGER.info('Client started successfully...')

        LOGGER.info(f'Expressing interest for {self.args.request}...')
        app_param = {k: v for k, v in vars(self.args).items()
                     if k not in ['request']}

        try:
            data_name, meta_info, content = await self.app.express_interest(
                self.args.request,
                app_param=json.dumps(app_param).encode(),
                lifetime=1000,
                must_be_fresh=True,
                can_be_prefix=False,
            )
            LOGGER.info(
                f'Received data: {(Name.to_str(data_name))}')
        except InterestNack as e:
            LOGGER.error(f'Nacked with reason={e.reason}')
        except InterestTimeout:
            LOGGER.error(f'Timeout')
        except InterestCanceled:
            LOGGER.error(f'Canceled')
        except ValidationFailure:
            LOGGER.error(f'Data failed to validate')


def main():
    parser = argparse.ArgumentParser(
        description='Express NDN interest', prog='python -m client')
    parser.add_argument('-r', '--request', required=True,
                        help='Interest name')

    args, unknown = parser.parse_known_args()

    app_param = {}
    for i in range(0, len(unknown), 2):
        k = unknown[i].lstrip('-')
        v = unknown[i+1]

        if k in SUPPORTED_APP_PARAMS.__members__:
            app_param[k] = v

    args = argparse.Namespace(**vars(args), **app_param)
    Client(args)


if __name__ == '__main__':
    main()
