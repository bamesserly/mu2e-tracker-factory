import shutil, os, sys
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
network_top_dir = "\\\\spa-mu2e-network\Files\Production_Environment"

network_data_dir = path.abspath(path.abspath(path.join(network_top_dir, "Data/")))
network_db = path.abspath(
    path.abspath(path.join(network_top_dir, "Database/", "database.db"))
)

local_top_dir = Path(path.dirname(__file__)).resolve()
local_data_dir = path.abspath(path.abspath(path.join(local_top_dir, "Data/")))
local_db = path.abspath(path.abspath(path.join(local_top_dir, "database.db")))

# TODO "network" isn't accurate. "merge destination" is better.
merge_destination_db_location_file = path.abspath(
    path.join(local_top_dir, "Database", "networkDatabasePath.txt")
)
local_db_location_file = path.abspath(
    path.join(local_top_dir, "Database", "localDatabasePath.txt")
)

is_official_lab_production = official_lab_production_top_dir in str(local_top_dir)
if not is_official_lab_production:
    print("... Software development mode detected.")
    print("    Will not automerge with the official network database.")

# ===============================================================================
# 2. Copy Data/ and database from network to work area
# ===============================================================================
print("... Copying the Data/ dir and database.db from the network.")
print("    This can take several minutes so grab a cup of coffee.")
print("    Beginning copy of Data dir...")
try:
    shutil.copytree(network_data_dir, local_data_dir)
    print("... Done copying Data dir.")
except FileExistsError as e:
    print("... Data dir already exists here!")
    print("    If things aren't working, you might need to refresh this directory.")

print("... Beginning copy of the database.")
# copy the database from the network to here.
# this first line helps shutil remember that it's connected to the network?
listdir(path.abspath(path.join(network_top_dir, "Database/")))
if not path.isfile(local_db):
    shutil.copy2(network_db, local_top_dir)
    print("... Done copying the database!")
else:
    print("... Database already exists here!")
    print("    Consider a mergedown before you collect data, in case the db is stale.")

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
    f.write(str(local_top_dir.resolve()))

# Merge destination depends on whether this is official lab panel production or
# software development.
# official --> merge with network
# software --> merge with local dummy
merge_destination_db = (
    network_db
    if is_official_lab_production
    else path.join(local_top_dir, "Database", "dummy.db")
)
with open(merge_destination_db_location_file, "w") as f:
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
    cmd = 'cd "{0}"; pre-commit install'.format(local_top_dir)
    p = Popen(["powershell.exe", cmd], stdout=sys.stdout)
    p.communicate()
    print("    Done setting up autoformatter.")


print("Done!")
