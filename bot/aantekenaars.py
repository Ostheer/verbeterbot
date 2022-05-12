import logging

from logging import FileHandler
from logging import Formatter

LOG_FORMAT = (
    "%(asctime)s [%(levelname)s]: %(message)s ")
LOG_LEVEL = logging.INFO

# messaging logger
LOG_FILE = "../aantekeningen.log"

aantekenaar = logging.getLogger("aantekenaar")
aantekenaar.setLevel(LOG_LEVEL)
aantekenaar_file_handler = FileHandler(LOG_FILE)
aantekenaar_file_handler.setLevel(LOG_LEVEL)
aantekenaar_file_handler.setFormatter(Formatter(LOG_FORMAT))
aantekenaar.addHandler(aantekenaar_file_handler)

