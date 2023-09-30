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
from kubernetes.client.exceptions import ApiException

from .settings import *
from .helpers import *
from .validators import *


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
        self.app.route(GATEWAY_ROUTES['compute_request'])(
            self._on_compute_request)
        self.app.route(GATEWAY_ROUTES['compute_status'])(
            self._on_compute_status)

    def _on_compute_request(self, int_name: FormalName, _int_param: InterestParam, _app_param: BinaryStr):
        LOGGER.info(f'Received interest: {Name.to_str(int_name)}')

        _app_param = json.loads(_app_param.tobytes())
        # Generic job validation
        if 'mem' in _app_param:
            try:
                _app_param['mem'] = int(_app_param['mem'])
            except ValueError:
                self.app.put_data(
                    int_name, b'Invalid memory requirement', freshness_period=3000)
                return
        if 'cpu' in _app_param:
            try:
                _app_param['cpu'] = int(_app_param['cpu'])
            except ValueError:
                self.app.put_data(
                    int_name, b'Invalid cpu requirement', freshness_period=3000)
                return
        # if 'disk' in _app_param:
        #     try:
        #         _app_param['disk'] = int(_app_param['disk'])
        #     except ValueError:
                #   self.app.put_data(int_name, b'Invalid disk requirement', freshness_period=3000)
                #   return
        if 'application' not in _app_param:
            self.app.put_data(
                int_name, b'`application` is required', freshness_period=3000)
            return

        # Application specific validation
        is_valid, error = validate_request(
            _app_param['application'], _app_param)
        if not is_valid:
            self.app.put_data(int_name, error.encode(), freshness_period=3000)
            return False, error

        _app_param = prepare_app_params(_app_param)
        # Job name
        _app_param['job_name'] = f'ndnk8s-job-{int(time.time())}'
        success, response = create_job_object(_app_param)
        if not success:
            LOGGER.error(f'Failed to create job: {response}')
            self.app.put_data(int_name, b'Bad request', freshness_period=3000)
            return

        config.load_incluster_config()
        instance = client.BatchV1Api()
        response = instance.create_namespaced_job(
            body=response, namespace=NAMESPACE)
        LOGGER.info(f'Job created. status={str(response.status)}')

        sanitized_response = instance.api_client.sanitize_for_serialization(
            response)
        response_data = {
            'message': 'Job created successfully',
            'name': sanitized_response['metadata']['name'],
        }
        return self.app.put_data(int_name, json.dumps(response_data).encode(),
                                 freshness_period=3000)

    def _on_compute_status(self, int_name: FormalName, _int_param: InterestParam, _app_param: BinaryStr):
        LOGGER.info(f'Received interest: {Name.to_str(int_name)}')

        _app_param = json.loads(_app_param.tobytes())
        if 'job_name' not in _app_param:
            self.app.put_data(
                int_name, b'`job_name` is required for status request', freshness_period=3000)
            return

        config.load_incluster_config()
        instance = client.BatchV1Api()
        try:
            job_status = instance.read_namespaced_job_status(
                name=_app_param['job_name'], namespace=NAMESPACE)
            sanitized_response = instance.api_client.sanitize_for_serialization(
                job_status)
            response_data = {}
            status = sanitized_response['status']
            active_pods = status.get('active', 0)
            succeeded_pods = status.get('succeeded', 0)
            failed_pods = status.get('failed', 0)
            if succeeded_pods > 0:
                job_state = 'Completed'
                # Tailored response for BLAST.
                # TODO: Generalize.
                response_data[
                    'message'] = f'Job completed successfully. Result available at /ndn/k8s/data/{_app_param["job_name"]}_blast.gz'
            elif failed_pods > 0:
                job_state = 'Failed'
            elif active_pods > 0:
                job_state = 'Running'
            else:
                job_state = 'Pending'
            response_data['status'] = job_state
            return self.app.put_data(int_name, json.dumps(response_data).encode(),
                                     freshness_period=3000)
        except ApiException as e:
            if e.status == 404:
                LOGGER.error(f'Job {_app_param["job_name"]} not found: {e}')
                return self.app.put_data(int_name, b'Job not found', freshness_period=3000)
            else:
                LOGGER.error(f'Failed to get job status: {e}')
                return self.app.put_data(int_name, b'Server error', freshness_period=3000)
        except Exception as e:
            LOGGER.error(f'Failed to get job status: {e}')
            return self.app.put_data(int_name, b'Server error', freshness_period=3000)


def main():
    Gateway()


if __name__ == '__main__':
    main()
