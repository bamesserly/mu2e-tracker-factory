from datetime import datetime
import logging

# the order that these lines appear in is important!
def SetupPANGUILogger(name="root"):
    sformatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    fformatter = logging.Formatter(
        "[%(asctime)s][%(levelname)-8s][%(threadName)-10s][%(module)-11s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    shandler = logging.StreamHandler()
    shandler.setFormatter(sformatter)
    shandler.setLevel(logging.INFO)

    logfile = "logfiles/" + datetime.strftime(
        datetime.now(), "%Y%m%d_%H%M%S_PANGUI_log.txt"
    )
    fhandler = logging.FileHandler(logfile)
    fhandler.setFormatter(fformatter)
    fhandler.setLevel(logging.DEBUG)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(shandler)
    logger.addHandler(fhandler)

    logging.getLogger("matplotlib").disabled = True
    logging.getLogger("matplotlib.font_manager").disabled = True
    logging.getLogger("matplotlib.pyplot").disabled = True
    logging.getLogger("findfont").disabled = True

    return logger
