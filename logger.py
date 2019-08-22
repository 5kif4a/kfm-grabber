import logging
import sys


logger = logging.getLogger('KFM-grabber')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('console.log')
# create console handler with a higher log level
ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(name)s: [%(levelname)s] - %(asctime)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)
