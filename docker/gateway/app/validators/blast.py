from typing import Tuple, Union


def validate(job_params: dict) -> Tuple[bool, Union[bytes, None]]:
    if 'sample_experiment' not in job_params:
        return False, '`sample_experiment` is required for blast compute request'

    valid_srr_ids = ['SRR2931415', 'SRR5139395']
    if job_params['sample_experiment'] not in valid_srr_ids:
        return False, f'Unknown sample experiment: {job_params["sample_experiment"]}. Please use one of {", ".join(valid_srr_ids)}'

    return True, None