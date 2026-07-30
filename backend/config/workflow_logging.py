import json
import logging
from decimal import Decimal


logger = logging.getLogger('wellness.workflow')


def _json_default(value):
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def workflow_log(event, **fields):
    logger.info(json.dumps({'event': event, **fields}, default=_json_default, sort_keys=True))
