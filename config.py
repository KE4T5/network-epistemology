import os


PATH_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_LOGS = os.path.join(PATH_ROOT_DIR, 'data', 'logs.txt')

LOGGER_MESSAGE_FORMATTER = '%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d  —  %(message)s'
