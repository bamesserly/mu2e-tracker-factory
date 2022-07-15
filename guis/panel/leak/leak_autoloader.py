# Purpose of this script is to call the db-loading function on all leak rate
# files.
# Mostly writing it to run it once on all the old data that never got loaded in
# the first place.
import guis.panel.leak.load_leak_csv_into_db as load
import os, shutil
from pathlib import Path
from guis.common.getresources import GetProjectPaths

from guis.common.panguilogger import SetupPANGUILogger

logger = SetupPANGUILogger("root", "load_all_leak")

if __name__ == "__main__":
    rootdir = GetProjectPaths()["panelleakdata"]

    # iterate through files in directory and subdirectories, attempting to save them to the DATABASE
    # otherwise, copy them to the problem_files folder
    for f in rootdir.rglob("*.txt"):
        try:
            load.main(f)
        except KeyboardInterrupt:
            logger.error(f"load interrupted for {f.parent.name}/{f.name}")
        except ValueError as e:
            logger.error(f"load failed for {f.parent.name}/{f.name}\n\t{e}")
        except Exception as e:
            logger.error(f"load failed for {f.parent.name}/{f.name}\n\t{e}")
