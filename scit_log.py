import logging
import logging.config
import os


#logger module
def initLogHandler(conf="confs/logger.conf"):
    logging.config.fileConfig("confs/logger.conf")
    logger = logging.getLogger("scit")

    return logger
