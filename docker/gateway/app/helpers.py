from kubernetes import client
from .settings import *


def create_job_object(job_name, job_params):
    # Configure Pod template container
    container = client.V1Container(
        name=job_name,
        image=job_params['application'],
        resources=client.V1ResourceRequirements(
            requests={'memory': job_params['mem'], 'cpu': job_params['cpu']},
            limits={'memory': job_params['mem'], 'cpu': job_params['cpu']}
        ),
        command=['/bin/bash', '-c', 'echo Hello Kubernetes! && sleep 30'],
        image_pull_policy='IfNotPresent'
    )

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={'app': job_name}),
        spec=client.V1PodSpec(restart_policy='Never', containers=[container]))

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4)

    # Instantiate the job object
    job = client.V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=client.V1ObjectMeta(name=job_name),
        spec=spec)

    return job


def create_job(api_instance, job, namespace):
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=namespace)
    LOGGER.info(f'Job created. status={str(api_response.status)}')
