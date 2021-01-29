#
#   databaseManager.py
#
#   DatabaseManager class establishes connection with SQL database to commit entries and run queries.
#
#   Author: Joe Dill
#

from sqlalchemy.orm import sessionmaker as dbconnection
from sqlalchemy import create_engine
from os import listdir, path
import sys
from pathlib import Path
import csv

d = {}
with open("./paths.csv", "r") as infile:
    reader = csv.reader(infile)
    d = {rows[0]: rows[1] for rows in reader}

import logging

logger = logging.getLogger("root")

from .merger import AutoMerger


class DatabaseManager:
    def __init__(self, db_dir=None, db_file="database.db", merge=True):

        ## Database File information
        self._dir = self._loadLocalDatabasePath() if db_dir is None else db_dir
        self._db_file = db_file
        self._db_path = path.join(self._dir, self._db_file)

        logger.info("Reading and writing from database %s" % self._db_path)

        ## Connect to SQL database
        self._Connection = dbconnection()
        self._engine = create_engine(f"sqlite:///{self._db_path}")
        self._Connection.configure(bind=self._engine)
        self._init_connection()

        ## Start Merger
        if merge:
            self.__merger = AutoMerger(
                src_db=self._db_path,
                dst_db=self._loadNetworkDatabasePath(),
                name="AutoMerger",
                daemon=True,
                merge_frequency=600,
            )
            self.__merger.start()

    def merge(self):
        self.__merger.main()

    def _loadLocalDatabasePath(self):
        current_dir = path.dirname(__file__)
        return d["data"]

    def _loadNetworkDatabasePath(self):
        current_dir = path.dirname(__file__)
        return d["network"]

    def getDatabasePath(self):
        return self._db_path

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
