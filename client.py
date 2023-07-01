import sys
import json
import argparse
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

from config import SUPPORTED_APP_PARAMS, LOGGER


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
        LOGGER.info(f'Expressing interest for {self.args.prefix}')

        app_param = {k: v for k, v in vars(self.args).items()
                     if k not in ['prefix']}

        try:
            await self.app.express_interest(
                self.args.prefix,
                app_param=json.dumps(app_param).encode(),
                must_be_fresh=True,
                lifetime=10000,
                can_be_prefix=True,
            )
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
    parser.add_argument('-p', '--prefix', required=True,
                        help='Interest name prefix')

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
