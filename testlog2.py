import logging
logging.config.fileConfig('logger.config')
logger = logging.getLogger(__name__)

def printlog():
    logger.error('in testlog2 a')
    print('bla')