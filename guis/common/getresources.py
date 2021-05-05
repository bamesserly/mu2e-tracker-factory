################################################################################
# Get a dictionary containing the important paths for this project.
# Read in the csv file containing the directory locations.
# Save them into a dictionary {name : path}.
# The paths are pathlib objs in absolute form: root_dir + relative_project_dir.
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
import resources


def GetProjectPaths():
    paths_file = ""
    with pkg_resources.path(resources, "paths.csv") as p:
        paths_file = p.resolve()
    paths = dict(np.loadtxt(paths_file, delimiter=",", dtype=str))
    # Make paths absolute. This txt file that holds the root/top dir of this
    # installation is created during setup.py.
    root = pkg_resources.read_text(resources, "rootDirectory.txt")
    paths.update((k, Path(root + "/" + v)) for k, v in paths.items())
    return paths
