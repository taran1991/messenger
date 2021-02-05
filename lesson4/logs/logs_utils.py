import logging
import logging.handlers

def create_logger(param):
    # создаём формировщик логов (formatter):
    formater = logging.Formatter(param['format'])

    # создаём потоки вывода логов
    stream_handler = logging.StreamHandler(param['stream_handler'])
    stream_handler.setFormatter(formater)
    stream_handler.setLevel(logging.ERROR)
    if param['timed_rotating']:
        log_file = logging.handlers.TimedRotatingFileHandler(param['logs_path'], encoding=param['encoding'],
                                                         interval=param['time_interval'], when=param['interval_type'])
    else:
        log_file = logging.FileHandler(param['logs_path'], encoding=param['encoding'])
    log_file.setFormatter(formater)

    # создаём регистратор и настраиваем его
    logger = logging.getLogger(param['app_name'])
    logger.addHandler(stream_handler)
    logger.addHandler(log_file)
    logger.setLevel(param['logging_level'])

    return logger

def test_logger(param):
    logger = create_logger(param)
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
