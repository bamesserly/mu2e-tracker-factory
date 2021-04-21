import shutil, os, sys, platform
from os import path, listdir
from pathlib import Path
from subprocess import Popen
from getpass import getuser

print("===============================================")
print("== Initial PANGUI official production setup. ==")
print("== This script only needs to be run once.    ==")
print("===============================================")

# Define root directory of this installation. Save it in a text file.
root_dir = Path(__file__).parent
root_dir_file = root_dir / "resources" / "rootDirectory.txt"
with open(root_dir_file, "w") as f:
    f.write(str(root_dir.resolve()))

# ===============================================================================
# 1. Determine key paths
# ===============================================================================
username = getuser()
network_top_dir = Path("\\\\rds01.storage.umn.edu\\cse_spa_mu2e")
network_data_dir = network_top_dir / "Data"
network_db = network_data_dir / "database.db"
local_data_dir = root_dir / "Data"
local_db = local_data_dir / "database.db"

# PANGUI looks in this file (which we will actually create later on) to find
# the location of the merge destination databases.
merge_destination_db_path_file = root_dir / "resources" / "networkDatabasePath.txt"

# is_official_lab_production means attempt to sync local db with THE network db.
# Alternatively, just sync ("merge") with a local dummy db. TODO: just turn off
# the sync.
#
# Crude way to determine this bool: is this installation in Desktop/Production?
official_lab_production_root = Path(
    "C:\\Users\\{0}\\Desktop\\Production".format(username)
)
is_official_lab_production = str(official_lab_production_root) in str(root_dir)
if not is_official_lab_production:
    print("... Software development mode detected.")
    print("    Will not automerge with the official network database.")

# ===============================================================================
# 2. Copy Data from network to work area
# ===============================================================================
if is_official_lab_production or sys.argv[1] == "copy_data":
    print("... Copying the Data/ dir from the network.")
    print("    This can take several minutes so grab a cup of coffee.")
    print("    Beginning copy of Data dir...")
    try:
        shutil.copytree(network_data_dir, local_data_dir)
        print("... Done copying Data dir.")
    except FileExistsError as e:
        print("... Data dir already exists here!")
        print("    If things aren't working, you might need to refresh this directory.")
else:
    print("... Local environment detected.")
    print("... Checking if Data directory exists")
    if os.path.isdir("Data"):
        print("    Data directory was found.")
        print("    Setup script will continue running.")
    else:
        print("    Data directory was not found.")
        print("    Please, download the Data directory and add it to this folder.")
        exit()
# TODO add exception(s) for when we're (a) not connected to the internet, (b)
# not connected to network_data_dir, and (c) other.

# ===============================================================================
# 3. Set locations of local and merge destination databases.
#
# Write them to txt files that databaseManager will read.
#
# For official lab panel production, the destination database IS the
# database.db on the network. For software development, the destination
# database is a dummy.db located in this directory.
# ===============================================================================
# Merge destination depends on whether this is official lab panel production or
# software development.
# official --> merge with network
# software --> merge with local dummy
merge_destination_db = (
    network_db if is_official_lab_production else path.join(local_data_dir, "dummy.db")
)
with open(merge_destination_db_path_file, "w") as f:
    f.write(merge_destination_db)

# ===============================================================================
# 4. Finally, if this is software development, we need to make the dummy.db
# and setup autoformatter.
# ===============================================================================
if not is_official_lab_production:
    if not path.isfile(merge_destination_db):
        print(
            "... Copying the local database as dummy.db, which we'll set as the automerge destination."
        )
        print("    Again, this might take a few minutes.")
        shutil.copyfile(local_db, merge_destination_db)

    print("... Finally, setting up autoformatter.")
    system = platform.system()
    cmd = 'cd "{0}"; pre-commit install'.format(local_top_dir)
    if system == "Windows":
        p = Popen(["powershell.exe", cmd], stdout=sys.stdout)
        p.communicate()
    elif system == "Darwin" or system == "Linux":
        p = Popen(cmd, stdout=sys.stdout, shell=True)
        p.communicate()
    else:
        print("    Unknown operating system.")
        print("    Please, contact a GUI developer if you see this message.")
        exit()
    print("    Done setting up autoformatter.")

# ===============================================================================
# 5. Create an empty folder to dump logfiles in.
# ===============================================================================
try:
    os.mkdir("logfiles")
except OSError as error:
    pass

print("Done!")
