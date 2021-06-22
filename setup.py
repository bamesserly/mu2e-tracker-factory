import shutil, os, sys, platform
from os import path, listdir
from pathlib import Path
from subprocess import Popen
from getpass import getuser
import argparse


def GetOptions():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--try_copy_data",
        action="store_true",
        default=False,
        help="Attempt to access \\rds01.umn.edu\ to download entire data directory. If this is official umn lab production, this defaults to True.",
    )
    parser.add_argument(
        "--dbv_db", help="Full path to database that DBViewer will use."
    )
    return parser.parse_args()


# root directory full path, save it in a file
def SetRootDir():
    root_dir = Path(__file__).parent
    root_dir = root_dir.resolve()
    root_dir_file = root_dir / "resources" / "rootDirectory.txt"
    with open(root_dir_file, "w") as f:
        f.write(str(root_dir))
    return root_dir


def Main():
    print("===============================================")
    print("== Initial PANGUI official production setup. ==")
    print("== This script only needs to be run once.    ==")
    print("===============================================")
    options = GetOptions()

    # ===============================================================================
    # 1. Determine key paths
    # ===============================================================================
    username = getuser()

    # root dir of this working area
    root_dir = SetRootDir()

    # umn network data area = authoritative area into which all local data merges
    network_top_dir = Path("\\\\rds01.storage.umn.edu\\cse_spa_mu2e")
    network_data_dir = network_top_dir / "Data"
    network_db = network_data_dir / "database.db"

    # local copy of data
    local_data_dir = root_dir / "data"
    local_db = local_data_dir / "database.db"

    # umn lab computers shalt install here
    official_lab_production_root = Path(
        "C:\\Users\\{0}\\Desktop\\Production".format(username)
    )

    # merge local data into network vs into dummy database
    is_official_lab_production = str(official_lab_production_root) in str(root_dir)
    if not is_official_lab_production:
        print("... Software development mode detected.")
        print("    Will not automerge with the official network database.")

    # network database location -- accessed by pangui -- stored in this txt file
    merge_destination_db_path_file = root_dir / "resources" / "networkDatabasePath.txt"

    # database -- accessed by database viewer -- stored in this txt file
    dbv_db_path_file = root_dir / "resources" / "dbvDatabasePath.txt"

    # ===============================================================================
    # 2. Make local copy of network data
    # TODO add exception(s), e.g. not connected to the internet
    # ===============================================================================
    if is_official_lab_production or options.try_copy_data:
        print("... Copying the Data/ dir from the network.")
        print("    This can take several minutes so grab a cup of coffee.")
        print("    Beginning copy of Data dir...")
        try:
            shutil.copytree(network_data_dir, local_data_dir)
            print("... Done copying Data dir.")
        except FileExistsError as e:
            print("... Data dir already exists here!")
            print(
                "    If things aren't working, you might need to refresh this directory."
            )
    else:
        print("... Local environment detected.")
        print("... Checking if Data directory exists")
        if os.path.isdir("data"):
            print("    Data directory was found.")
            print("    Setup script will continue running.")
            with open("data/__init__.py", "w") as file:
                pass
        else:
            print("    Data directory was not found.")
            print(
                "    If you intend to run pangui, please, download the data "
                "directory and add it to this folder."
            )
            exit()

    # ============================================================================
    # 3. Set locations of local and merge destination databases.
    #
    # Write them to txt files that databaseManager will read.
    #
    # For official lab panel production, the destination database IS the
    # database.db on the network. For software development, the destination
    # database is a dummy.db located in this directory.
    # =============================================================================
    # Merge destination depends on whether this is official lab panel production or
    # software development.
    # official --> merge with network
    # software --> merge with local dummy
    merge_destination_db = str(
        network_db
        if is_official_lab_production
        else path.join(local_data_dir, "dummy.db")
    )
    with open(merge_destination_db_path_file, "w") as f:
        f.write(merge_destination_db)

    # location of database that database viewer loads
    dbv_db = None
    if is_official_lab_production:
        dbv_db = str(network_db)
    elif options.dbv_db:
        dbv_db = options.dbv_db
    else:
        dbv_db = str(local_data_dir / "database.db")
    with open(dbv_db_path_file, "w") as f:
        f.write(dbv_db)

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
            try:
                shutil.copyfile(local_db, merge_destination_db)
            except FileNotFoundError:
                print("Local database not found. Not making a dummy merge target db.")

        print("... Finally, setting up autoformatter.")
        system = platform.system()
        cmd = 'cd "{0}"; pre-commit install'.format(root_dir)
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


if __name__ == "__main__":
    Main()
