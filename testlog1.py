import logging.config
import testlog2


#logging.config.fileConfig('logger.config')
logger = logging.getLogger(__name__)

def main():
    logger.error('dfafdtest1')
    testlog2.printlog()

if __name__=='__main__':
    main()
