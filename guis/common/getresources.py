################################################################################
################################################################################

import numpy as np  # has the most convenient csv parser for the task at hand
from pathlib import Path

# Resource manager, and the resources folder (package)
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

# Resources folder: where the paths.csv file is stored.
import resources, data

# Get a dictionary containing the important paths for this project.
# Read in the csv file containing the directory locations.
# Save them into a dictionary {name : path}.
# The paths are pathlib objs in absolute form: root_dir + relative_project_dir.
def GetProjectPaths():
    paths_file = ""
    with pkg_resources.path(resources, "paths.csv") as p:
        paths_file = p.resolve()
    paths = dict(np.loadtxt(paths_file, delimiter=",", dtype=str))
    # Make paths absolute. This txt file that holds the root/top dir of this
    # installation is created during setup.py.
    root = GetRootPath()

    # paths.update((k, Path(root + "/" + v)) for k, v in paths.items())
    for k, v in paths.items():
        # if special strawroom things
        if k == "leaktestresults" or k == "pallets" or k == "network_leaktest_raw_data":
            # save directly to the network
            # official production mode
            if "rds01.storage.umn.edu\cse_spa_mu2e\Data" in GetNetworkDatabasePath():
                paths.update({k: Path("X:/" + v)})
            # developer test mode
            else:
                paths.update({k: Path("X:/DeveloperTestArea/" + v)})
        else:
            # we want paths to remain on this machine
            paths.update({k: Path(root + "/" + v)})

    return paths


# list of strings ["COM1", "COM8", etc.]
def GetStrawLeakInoPorts():
    ports = pkg_resources.read_text(resources, "straw_leak_ino_ports.txt")
    return [i.strip() for i in ports.split("\n")]


def GetLocalDatabasePath():
    with pkg_resources.path(data, "database.db") as p:
        return str(p.resolve())


def GetNetworkDatabasePath():
    return pkg_resources.read_text(resources, "networkDatabasePath.txt")


def GetNetworkDataPath():
    return Path(GetNetworkDatabasePath()).parent


def GetRootPath():
    return pkg_resources.read_text(resources, "rootDirectory.txt")
