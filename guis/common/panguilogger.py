from datetime import datetime
from os import getenv
import logging

# the order that these lines appear in is important!
def SetupPANGUILogger(name="root", tag="PANGUI", be_verbose=False, straw_location=None):
    sformatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    fformatter = logging.Formatter(
        "[%(asctime)s][%(levelname)-8s][%(threadName)-10s][%(module)-11s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    shandler = logging.StreamHandler()
    shandler.setFormatter(sformatter)
    shandler.setLevel(logging.INFO)
    if be_verbose:
        shandler.setLevel(1)

    logfile = "./logfiles/" + datetime.strftime(
        datetime.now(), f"%Y%m%d_%H%M%S_{tag}_{getenv('USERDOMAIN')}_log.txt"
    )
    if tag == "Methane":
        logfile = "./logfiles/" + datetime.strftime(
            datetime.now(),
            f"%Y%m%d_%H%M%S_{tag}_{getenv('USERDOMAIN')}_CPAL{straw_location}_log.txt",
        )
    fhandler = logging.FileHandler(logfile)
    fhandler.setFormatter(fformatter)
    fhandler.setLevel(logging.DEBUG)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if be_verbose:
        logger.setLevel(1)
    logger.addHandler(shandler)
    logger.addHandler(fhandler)

    logging.getLogger("matplotlib").disabled = True
    logging.getLogger("matplotlib.font_manager").disabled = True
    logging.getLogger("matplotlib.pyplot").disabled = True
    logging.getLogger("findfont").disabled = True

    logger.info(f"{tag} Logger Initialized")

    return logger
