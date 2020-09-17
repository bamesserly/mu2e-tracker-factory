import sqlite3, os, time, sys
from pathlib import Path
from datetime import datetime

# Import LoopingReusableThread from Modules.advancedthreading
sys.path.insert(
    0, str(Path(__file__).resolve().parent)
)  # Insert path to this directory
from advancedthreading import LoopingReusableThread


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

        print("Merging to database", dst_db)

        # Allias used when attaching source database
        self.attach_alias = "att"  # Alias for source database

    def getTables(self):
        return [
            tpl[0]
            for tpl in self.__execute(
                "select name from sqlite_master where type = 'table'", fetchall=True
            )
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

    def mergeAll(self):
        self.__execute(
            "\n".join([self.merge(t, execute=False) for t in self.getTables()])
        )

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
        con = sqlite3.connect(dst_db)

        # Attach db2
        # print(src_db, attach_alias)
        con.executescript(f"ATTACH DATABASE '{src_db}' as {attach_alias};")

        # Execute input script
        ret = {
            True: lambda script: con.execute(script).fetchall(),
            False: lambda script: con.executescript(script),
        }[fetchall](script)

        # Commit script
        con.commit()

        # Close connection
        con.close()

        # Return ret
        return ret

    @staticmethod
    def mergeScript(table, attached_alias, into_attached=False):
        # Determine database prefixes
        dst_prefix = f"{attached_alias}." if into_attached else str()
        src_prefix = f"{attached_alias}." if not into_attached else str()
        # Generate script
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
        return self.mergeAll()


class AutoMerger(Merger, LoopingReusableThread):
    def __init__(self, src_db, dst_db, name=None, daemon=True, merge_frequency=600):

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
        # print(f'\n\nAutomerge into {self.dst_db}\n\n')
        print("Automerge has begun...")
        LoopingReusableThread.run(self)


if __name__ == "__main__":
    local = (
        "\\\\spa-mu2e-network\\Files\\Development_Environment\\Database\\database.db"
    )
    network = (
        "\\\\spa-mu2e-network\\Files\\Development_Environment\\Database\\network.db"
    )
    merger = AutoMerger(src_db=local, dst_db=network, merge_frequency=30)
    merger.start()
