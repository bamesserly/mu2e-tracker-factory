from datetime import datetime
from guis.common.getresources import GetProjectPaths, GetNetworkDataPath, GetRootPath
import logging
import subprocess
from guis.common.panguilogger import SetupPANGUILogger

logger = logging.getLogger("root")

# DANGER: if you haven't "automerged" your latest changes, they'll be overwritten
def run():
    local_data_path = str(GetProjectPaths()["datatop"])
    network_data_path = str(GetNetworkDataPath())
    root_path = GetRootPath()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")

    logger.info("Doing a slim mergedown (i.e. just the DB file).")
    output = subprocess.run(
        ["robocopy", network_data_path, local_data_path, "database.db", "/np"],
        capture_output=True,
        text=True,
    )

    logger.info(output.stdout)
    logger.info("standalone slim mergedown complete")


if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "SlimMergedown")
    run()
