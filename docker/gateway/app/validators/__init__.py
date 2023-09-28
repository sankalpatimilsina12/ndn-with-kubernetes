from typing import Tuple, Union

from . import blast


def validate_application_params(application: str, job_params: dict) -> Tuple[bool, Union[str, None]]:
    validators = {
        'blast': blast.validate
    }

    if application in validators:
        return validators[application](job_params)
    else:
        return False, b'Unsupported application'
