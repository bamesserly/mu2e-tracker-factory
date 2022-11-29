from os import listdir
from re import search
from time import sleep
from tests.load_lpal_again import load
from guis.common.panguilogger import SetupPANGUILogger
import logging

logger = logging.getLogger("root")

def run():
    files = []
    statusMessages = []
    succ = 0
    err = 0

    for thing in listdir("./data/Loading Pallets"):
        if search("LPAL\d{4}_LPALID\d{2}.csv", thing):
            files.append(f"./data/Loading Pallets/{thing}")

    for file in files:
        logger.info(f'Loading {file}...')
        numErrors = load(file, manual=False)
        if numErrors > -1:
            logger.info(f'Loaded {file}.  {numErrors} errors.\n\n\n\n\n')
            statusMessages.append(f'{file} loaded with {numErrors} errors.')
            succ += 1
        else:
            logger.info(f'Could not load {file}.  LPAL not found in database.\n\n\n\n\n')
            statusMessages.append(f'{file} was not loaded.')
            err += 1


    logger.info(f'Loaded {succ} files.  Could not load {err} files.')
    for message in statusMessages:
        logger.info(message)

    return 0

if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadLPALToStrawPresentData")
    run()