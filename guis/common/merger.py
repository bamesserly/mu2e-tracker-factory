import sqlite3, os, time, sys
from pathlib import Path
from datetime import datetime
import sqlalchemy as sqla

from guis.common.panguilogger import SetupPANGUILogger
from guis.common.advancedthreading import LoopingReusableThread
from guis.common.getresources import GetLocalDatabasePath, GetNetworkDatabasePath

import logging

logger = logging.getLogger("root")


class Merger:
    """
    __init__
        Initialization method:
            - Saves directories to both database files
            - Establishes connection with destination database
            - Attaches source database to that connection

        Input:
        src_db - Path to the database that Merger will take data from
        dst_db - Path to the database that Merger is inserting data into
    """

    def __init__(self, src_db, dst_db):
        # Save path addresses
        self.src_db = src_db
        self.dst_db = dst_db

        logger.log(1, f"Merging from database {src_db}")
        logger.info(f"Merging to database {dst_db}")

        # Allias used when attaching source database
        self.attach_alias = "att"  # Alias for source database

    def getTables(self):
        return [
            tpl[0]
            for tpl in self.__execute(
                "select name from sqlite_master where type = 'table' AND name not like 'sqlite?_%' escape '?'",
                fetchall=True,
            )
            if tpl[0] not in ["measurement_panel_leak", "supply_checked"]
        ]

    """
    merge
        Runs a SQL script against the database session that finds all entries in a given
        table that don't exist in the other database or have been updated (have a more
        recent timestamp). It then inserts or replaces these queried entries into the
        destination database

        Input:
            table   (str)   name of table to be merged
            execute (bool)  boolean indicating if written script should be executed

        Return:
            if execute  =>  (?)     result of self.executeScript()
            else        =>  (str)   script that merges the given table
    """

    def merge(self, table, execute=True):

        # Generate merge script
        script = self.mergeScript(
            table=table, attached_alias=self.attach_alias, into_attached=False
        )

        # Execute or return script
        if execute:
            return self.__execute(script)
        else:
            return script

    # Loop tables in target db, add (update) all source data to the target
    # tables when data is new (when t_source > t_target).
    #
    # A non-critical merge failure for a single table will not affect the
    # merging of other tables.
    #
    # e.g. non-critical failure: table exists in target but not source.
    def mergeAll(self):
        start = datetime.now()
        logger.debug("Beginning Automerge")
        # logger.debug("\n".join([self.merge(t,execute=False) for t in sorted(self.getTables())]))
        self.__execute(
            "\n".join([self.merge(t, execute=False) for t in self.getTables()])
        )
        # for t in self.getTables():
        #   logger.log(1, f"    {t}")
        #   self.__execute(
        #       self.merge(t, execute=False)
        #   )
        finish = datetime.now()
        dt = (finish - start).total_seconds()
        logger.debug(f"Automerge complete ({dt}s)")

    def __execute(self, script, fetchall=False):
        return self.executeScript(
            dst_db=self.dst_db,
            src_db=self.src_db,
            script=script,
            attach_alias=self.attach_alias,
            fetchall=fetchall,
        )

    @staticmethod
    def executeScript(dst_db, src_db, script, attach_alias, fetchall=False):
        # Open connection
        try:
            con = sqlite3.connect(dst_db, timeout=15)
        except Exception as e:
            logger.critical(f"FAILED TO CONNECT TO DATABASE, {dst_db}\nException: {e}")
            raise ConnectionError("Failed to connect to database")

        # Attach db2
        # print(src_db, attach_alias)
        con.executescript(f"ATTACH DATABASE '{src_db}' as {attach_alias};")
        ret = {}
        try:
            # Execute input script
            ret = {
                True: lambda script: con.execute(script).fetchall(),
                False: lambda script: con.executescript(script),
            }[fetchall](script)
        except Exception as e:
            logger.error(f"Script execution failed, Exception: {e}")

        # Commit script
        try:
            con.commit()
        except Exception as e:
            logger.error(f"Failed to commit merge script, Exception: {e}")

        # Close connection
        try:
            con.close()
        except Exception as e:
            logger.error(f"Failed to close database connection, Exception: {e}")

        # Return ret
        return ret

    @staticmethod
    def mergeScript(table, attached_alias, into_attached=False):
        # Determine database prefixes
        dst_prefix = f"{attached_alias}." if into_attached else str()
        src_prefix = f"{attached_alias}." if not into_attached else str()
        # Generate script
        # logger.debug(f'Script for {table}')
        # logger.debug(f"""
        #    INSERT OR REPLACE INTO
        #    {dst_prefix}{table}
        #    SELECT srct.* FROM
        #    {src_prefix}{table} srct
        #    LEFT OUTER JOIN
        #    {dst_prefix}{table} t ON srct.id = t.id
        #    WHERE
        #    srct.timestamp > t.timestamp
        #    OR
        #    t.id IS NULL;
        #    """)
        return f"""
            INSERT OR REPLACE INTO
            {dst_prefix}{table}
            SELECT srct.* FROM
            {src_prefix}{table} srct
            LEFT OUTER JOIN
            {dst_prefix}{table} t ON srct.id = t.id
            WHERE
            srct.timestamp > t.timestamp
            OR
            t.id IS NULL;
            """

    def main(self):
        try:
            return self.mergeAll()
        except sqla.exc.OperationalError:
            logger.error("DB Locked. Failed to attach local DB in executeScript.")


class AutoMerger(Merger, LoopingReusableThread):
    def __init__(self, src_db, dst_db, name=None, daemon=True, merge_frequency=1800):

        ## Initialize Merger
        Merger.__init__(self, src_db, dst_db)

        # print("AutoMerger::__init__ (src_db, dst_db) (", src_db, ", ", dst_db, ")")
        ## Initialize LoopingReusableThread Class
        LoopingReusableThread.__init__(
            self,
            target=self.main,
            name=name,
            daemon=daemon,
            execute_interval=merge_frequency,
        )

    def run(self):
        logger.info(
            "Automerger is running and will send data to the network every 10 min."
        )
        LoopingReusableThread.run(self)


def isolated_automerge():
    merger = Merger(src_db=GetLocalDatabasePath(), dst_db=GetNetworkDatabasePath())
    merger.mergeAll()


if __name__ == "__main__":
    logger = SetupPANGUILogger("root", "IsolatedAutoMerge", be_verbose=True)
    isolated_automerge()
