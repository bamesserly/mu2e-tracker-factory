import shutil, os, sys, platform
from os import path, listdir
from pathlib import Path
from subprocess import Popen

print("===============================================")
print("== Initial PANGUI official production setup. ==")
print("== This script only needs to be run once.    ==")
print("===============================================")

# ===============================================================================
# 1. Determine key paths
# ===============================================================================
# TODO get this from a environmental variable
username = os.getenv("username")
official_lab_production_top_dir = "C:\\Users\\{0}\\Desktop\\Production".format(username)
network_top_dir = "\\\\rds01.storage.umn.edu\\cse_spa_mu2e"
network_data_dir = path.abspath(path.abspath(path.join(network_top_dir, "Data/")))
network_db = path.abspath(path.abspath(path.join(network_data_dir, "database.db")))

local_top_dir = Path(path.dirname(__file__)).resolve()
local_data_dir = path.abspath(path.abspath(path.join(local_top_dir, "Data/")))
local_db = path.abspath(path.abspath(path.join(local_data_dir, "database.db")))

# PANGUI looks in these files (which we will actually create later on) to find
# the location of the local and merge destination databases.
# TODO "network" isn't accurate. "merge destination" is better.
merge_destination_db_location_file = path.abspath(
    path.join(local_top_dir, "Database", "networkDatabasePath.txt")
)
local_db_location_file = path.abspath(
    path.join(local_top_dir, "Database", "localDatabasePath.txt")
)

# Being in "official lab production mode" means that we will automerge to THE
# network database.
#
# The alternative to being in "official lab production mode" is to be in
# developer mode, which means that we'll automerge to a dummy database.
#
# To determine official vs dev mode: if this code is in the Desktop/Production
# folder then it's official. Anywhere else and it's dev mode.
is_official_lab_production = official_lab_production_top_dir in str(local_top_dir)
if not is_official_lab_production:
    print("... Software development mode detected.")
    print("    Will not automerge with the official network database.")

# ===============================================================================
# 2. Copy Data from network to work area
# ===============================================================================
if is_official_lab_production:
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
        print("    Setup scrip will continue running.")
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

# Set local database location (never changes)
with open(local_db_location_file, "w") as f:
    f.write(local_data_dir)

# Merge destination depends on whether this is official lab panel production or
# software development.
# official --> merge with network
# software --> merge with local dummy
merge_destination_db = (
    network_db if is_official_lab_production else path.join(local_data_dir, "dummy.db")
)
with open(merge_destination_db_location_file, "w") as f:
    f.write(merge_destination_db)

# TODO: csv file with relevant paths. Needed for project restructure
with open("paths.csv", "w") as file:
    file.write("local," + str(local_top_dir) + ",\n")
    file.write("network," + network_top_dir + ",\n")
    file.write("merge_destination," + merge_destination_db + ",\n")
    file.write("data," + str(local_top_dir) + "\Data" + ",\n")
    file.write("root," + str(local_top_dir) + "\mu2e" + ",\n")
    file.write("diagrams," + str(local_top_dir) + "\Data\Panel data\diagrams" + ",\n")
    file.write("workers," + str(local_top_dir) + "\Data\workers\panel workers" + ",\n")
    file.write("panel," + str(local_top_dir) + "\Data\Panel data" + ",\n")

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
