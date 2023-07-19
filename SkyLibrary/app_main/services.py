import logging
from datetime import datetime

from django.core.exceptions import ImproperlyConfigured

LOGS_FILE_NAME = 'logs.log'
ERROR_LEVELS = ('ERROR', 'WARNING', 'CRITICAL')


def env_var_not_set_handler(variable_name: str, context='no context', error_level='WARNING') -> None:

    error_level = error_level.upper()

    if error_level not in ERROR_LEVELS:
        error_level = 'WARNING'

    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    error_message = f'[{error_level}] [{now_time}] module - "settings.py" message - ' \
                    f'"{variable_name} is unset, context - "{context}"" (created without logging module)\n'

    logger = logging.getLogger(__name__)

    # write in console:
    if error_level == 'ERROR':
        logger.error(error_message)

    elif error_level == 'WARNING':
        logger.warning(error_message)

    elif error_level == 'CRITICAL':
        logger.critical(error_message)

    # write in logs file:
    with open(LOGS_FILE_NAME, 'a+') as logs_file:
        logs_file.write(error_message)

    if error_level in ['CRITICAL', 'ERROR']:
        raise ImproperlyConfigured(error_message)
