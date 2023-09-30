from typing import Tuple, Union

from ndn.types import BinaryStr
from kubernetes import client

from .settings import *


def prepare_app_params(_app_param: dict) -> dict:
    for k, v in SUPPORTED_APP_PARAMS.items():
        if k not in _app_param:
            _app_param[k] = v
    return _app_param


def create_job_object(job_params) -> Tuple[bool, Union[client.V1Job, Exception]]:
    # Prepare command
    command = SUPPORTED_APPS[job_params['application']]['command']
    try:
        formatted_command = [c.format(**job_params) for c in command]
    except Exception as e:
        return False, e

    image = SUPPORTED_APPS[job_params['application']]['image']

    # Configure Pod template container
    container = client.V1Container(
        name=job_params['job_name'],
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
        metadata=client.V1ObjectMeta(labels={'app': job_params['job_name']}),
        spec=client.V1PodSpec(restart_policy='Never', containers=[container], volumes=[volume]))

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=0)

    # Instantiate the job object
    job = client.V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=client.V1ObjectMeta(name=job_params['job_name']),
        spec=spec)

    return True, job
