from typing import Tuple, Union

from . import blast
from ..settings import SUPPORTED_APPS

# Add validators
SUPPORTED_APPS['blast']['validator'] = blast.validate

def validate_request(application: str, job_params: dict) -> Tuple[bool, Union[str, None]]:
    if application in SUPPORTED_APPS:
        if 'validator' in SUPPORTED_APPS[application]:
            return SUPPORTED_APPS[application]['validator'](job_params)
        else:
            return True, None
    else:
        return False, f'Application `{application}` not supported. Supported applications: {", ".join(SUPPORTED_APPS.keys())}'
