import json
from typing import Tuple, Union

from ndn.types import BinaryStr
from kubernetes import client

from .settings import *
from .validators import validate_application_params


def extract_app_params(_app_param: BinaryStr) -> Tuple[bool, Union[bytes, dict]]:
    _app_param = json.loads(_app_param.tobytes())

    # Generic job validation
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

    # if 'disk' in _app_param:
    #     try:
    #         _app_param['disk'] = int(_app_param['disk'])
    #     except ValueError:
    #         return False, b'Invalid disk requirement'
    if _app_param['application'] not in SUPPORTED_APPS:
        return False, f'Application `{_app_param["application"]}` not supported. Supported applications: {", ".join(SUPPORTED_APPS.keys())}'.encode()

    # Application specific validation
    is_valid, error = validate_application_params(
        _app_param['application'], _app_param)
    if not is_valid:
        return False, error

    for k, v in SUPPORTED_APP_PARAMS.items():
        if k not in _app_param:
            _app_param[k] = v

    return True, _app_param


def create_job_object(job_name, job_params) -> Tuple[bool, Union[client.V1Job, Exception]]:
    # Prepare command
    command = SUPPORTED_APPS[job_params['application']]['command']
    try:
        formatted_command = [c.format(**job_params) for c in command]
    except Exception as e:
        return False, e

    image = SUPPORTED_APPS[job_params['application']]['image']

    # Configure Pod template container
    container = client.V1Container(
        name=job_name,
        image=image,
        resources=client.V1ResourceRequirements(
            requests={'memory': job_params['mem'], 'cpu': job_params['cpu']},
            limits={'memory': job_params['mem'], 'cpu': job_params['cpu']}
        ),
        command=formatted_command,
        image_pull_policy='Always',
        volume_mounts=[client.V1VolumeMount(
            mount_path='/fileserver_data', name='fileserver-data')],
    )

    # Add the volume to the pod
    volume = client.V1Volume(
        name='fileserver-data',
        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
            claim_name='datalake-storage-claim'))

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'app': job_name}),
        spec=client.V1PodSpec(restart_policy='Never', containers=[container], volumes=[volume]))

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=0)

    # Instantiate the job object
    job = client.V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=client.V1ObjectMeta(name=job_name),
        spec=spec)

    return True, job
