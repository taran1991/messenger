import sys
import inspect


from logs.logs_utils import create_logger
if sys.argv[0].find('client') == -1:
    from logs.logs_config import SERVER_CONFIG as LOGGER_CONFIG
else:
    from logs.logs_config import CLIENT_CONFIG as LOGGER_CONFIG
LOGGER_CONFIG['format'] = f'%(asctime)s %(levelname)s {sys.argv[0]} %(message)s'
LOGGER = create_logger(LOGGER_CONFIG)


def log_cls(cls):
    def decorate(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            LOGGER.debug(f'Был вызван метод {func.__name__} класса {self.__class__.__name__} c параметрами {args}, {kwargs}. '
                         f'Вызов из модуля {inspect.getmodulename(inspect.getmodule(func).__file__)}.'
                         f'Вызов из функции {inspect.stack()[1][3]}')
            return result
        return wrapper

    for attr in dir(cls):
        if attr.startswith('__') or attr.startswith('_'):
            continue
        try:
            method = cls.__getattribute__(cls, attr)
            if inspect.isfunction(method):
                setattr(cls, attr, decorate(method))
        except:
            pass
    return cls
