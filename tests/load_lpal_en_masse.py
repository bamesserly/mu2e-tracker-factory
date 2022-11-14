from os import listdir
from re import search
from tests.load_lpal_again import load
from guis.common.panguilogger import SetupPANGUILogger
import logging

logger = logging.getLogger("root")

def run():
    files = []

    for thing in listdir("./data/Loading Pallets"):
        if search("LPAL\d{4}_LPALID\d{2}.csv", thing):
            files.append(f"./data/Loading Pallets/{thing}")

    for file in files:
        logger.info(f'Loading {file}...')
        load(file, manual=False)
    
    return 0

if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "LoadLPALToStrawPresentData")
    run()