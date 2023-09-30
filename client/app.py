import sys
import json
import argparse
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.encoding import Name

from .settings import *


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

        LOGGER.info(f'Expressing interest for {self.args.interest}...')
        app_param = {k: v for k, v in vars(self.args).items()
                     if k not in ['interest']}

        try:
            data_name, meta_info, content = await self.app.express_interest(
                self.args.interest,
                lifetime=1000,
                must_be_fresh=True,
                can_be_prefix=False,
                app_param=json.dumps(app_param).encode(),
            )
            LOGGER.info(
                f'Received data: {(Name.to_str(data_name))}')
            LOGGER.info(content.tobytes().decode())
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
    parser.add_argument('-i', '--interest', required=True,
                        help='Interest name')
    parser.add_argument('-a', '--application', required=False,
                        help='Application name')
    parser.add_argument('-jn', '--job_name', required=False,
                        help='Job name')
    parser.add_argument('-s', '--sample_experiment', required=False,
                        help='Sample experiment name')
    parser.add_argument('-m', '--mem', required=False,
                        help='Memory requirement')
    parser.add_argument('-c', '--cpu', required=False,
                        help='CPU requirement')
    args = parser.parse_args()

    # Filter out None values
    valid_args = {k: v for k, v in vars(args).items() if v is not None}
    args = argparse.Namespace(**valid_args)
    Client(args)


if __name__ == '__main__':
    main()
