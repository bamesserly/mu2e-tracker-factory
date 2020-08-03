import shutil
from os import path, listdir

print("Initial PANGUI official production setup.")
print("This script only needs to be run once.")
print("\nCopying the Data/ dir and database.db from the network.")
print(
    """\nThis can take several minutes so it might be a good time to grab a
cup of coffee."""
)

source_dir = "\\\\spa-mu2e-network\Files\Development_Environment"
source_data_dir = path.abspath(path.abspath(path.join(source_dir, "Data/")))
source_database = path.abspath(
    path.abspath(path.join(source_dir, "Database/", "database.db"))
)

destination_dir = path.dirname(__file__)
destination_data_dir = path.abspath(path.abspath(path.join(destination_dir, "Data/")))
destination_database = path.abspath(
    path.abspath(path.join(destination_dir, "database.db"))
)


# copy the data directory from the network to here
print("\nBeginning copy of Data dir...")
try:
    shutil.copytree(source_data_dir, destination_data_dir)
    print("\nDone copying Data dir.")
except FileExistsError as e:
    print(
        """\nData dir already exists here! If things aren't working, you
might need to refresh this directory."""
    )
print("\nBeginning copy of the database.")

# copy the database from the network to here.
# this first line helps shutil remember that it's connected to the network?
listdir(path.abspath(path.join(source_dir, "Database/")))
if not path.isfile(destination_database):
    shutil.copy2(source_database, destination_dir)
    print("\nDone copying the database!")
else:
    print(
        """\nDatabase already exists here! Consider a mergedown before you
collect data, in case the dir is stale."""
    )

print("\nAll Done.")
