import logging

LOGS_FILE_NAME = 'logs.log'
ERROR_LEVELS = ('ERROR', 'WARNING')


def not_env_var_set_handler(variable_name: str, context='not context', error_level='WARNING') -> None:

    error_level = error_level.upper()

    if error_level not in ERROR_LEVELS:
        error_level = 'WARNING'

    error_message = f'[{error_level}] module - "settings.py" message - ' \
                    f'"{variable_name} is unset, context - {context}" (created without logging module)\n'

    logger = logging.getLogger(__name__)

    # write in console:
    if error_level == 'ERROR':
        logger.error(error_message)

    elif error_level == 'WARNING':
        logger.warning(error_message)

    # write in logs file:
    with open(LOGS_FILE_NAME, 'a+') as logs_file:
        logs_file.write(error_message)


def show_debug_toolbar(request) -> bool:
    return not request.user.is_anonymous and request.user.role == 4  # 4 - superuser
