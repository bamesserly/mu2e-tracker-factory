#
#   databaseManager.py
#
#   DatabaseManager class establishes connection with SQL database to commit entries and run queries.
#

from sqlalchemy.orm import sessionmaker as dbconnection
from sqlalchemy import create_engine

import logging

logger = logging.getLogger("root")

from guis.common.merger import AutoMerger
from guis.common.getresources import GetLocalDatabasePath, GetNetworkDatabasePath

# Load resources manager
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources
import data, resources


class DatabaseManager:
    def __init__(self, local_db=None, merge=True):

        ## Local Database File information
        self._local_db = GetLocalDatabasePath() if local_db is None else local_db
        logger.info("Reading and writing from database %s" % self._local_db)

        ## Connect to Local SQL database
        self._Connection = dbconnection()
        self._engine = create_engine(
            f"sqlite:///{self._local_db}",
            pool_pre_ping=True,
            connect_args={"timeout": 30},
        )
        self._Connection.configure(bind=self._engine)
        self._init_connection()

        ## Start Merger of Local DB with Network/Destination DB
        if merge:
            self.__merger = AutoMerger(
                src_db=self._local_db,
                dst_db=GetNetworkDatabasePath(),
                name="AutoMerger",
                daemon=True,
                merge_frequency=600,
            )
            self.__merger.start()

    def merge(self):
        self.__merger.main()

    def getLocalDatabasePath(self):
        return self._local_db

    def _init_connection(self):
        self._connection = self._Connection()

    ### QUERY METHOD ###
    def query(self, *mapped_class):
        return self._connection.query(*mapped_class)

    ### COMMIT ENTRY METHODS ###
    def commitEntry(self, entry):
        self._connection.add(entry)
        self._connection.commit()
        return True

    def commitEntries(self, entries):
        self._connection.add_all(entries)
        self._connection.commit()
        return True


if __name__ == "__main__":
    DatabaseManager()
