################################################################################
# Base/parent classes for classes representing sqlite tables
#
# All such classes inherit from sqlalchemy's declarative_base.
#
# See:
# https://docs.sqlalchemy.org/en/14/orm/tutorial.html
################################################################################

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    REAL,
    VARCHAR,
    ForeignKey,
    CHAR,
    BOOLEAN,
    and_,
    DATETIME,
    Table,
    TEXT,
    func,
)
from sqlalchemy.types import DateTime
from sqlalchemy.sql.functions import now, localtime
from sqlalchemy.sql.expression import true, false
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from guis.common.databaseManager import DatabaseManager
from datetime import datetime
from sys import modules, exit
from inspect import isclass, getmembers
from datetime import datetime
from time import time

import logging

logger = logging.getLogger("root")

# GLOBAL VARIABLES #
DM = DatabaseManager()
BASE = declarative_base()


class AutoCommit:
    def commit(self):
        return DM.commitEntry(self)

class Barcode:
    @staticmethod
    def barcode(prefix, digits, n):
        try:
            return f"{prefix}{format(n,f'0{digits}')}"
        except:
            return f"{prefix}0{digits}"
            
class Query:
    @classmethod
    def query(cls):
        return DM.query(cls)    


    """
    __queryWithId
    (class method)

        Runs an query on its class and filters by id.

        Input:  id  (int)   PK of object to be queried
        Return: (Query) object to be manipulated further.
    """

    @classmethod
    def __queryWithId(cls, id):
        return cls.query().filter(cls.id == id)

    """
    queryWithId
    (class method)

        Returns result of query by id.

        Input:  id  (int)   PK of object to be queried
        Return: (instance of cls)/(None) if a database entry is (found)/(not found) in this table having the given id.
    """

    @classmethod
    def queryWithId(cls, id):
        return cls.__queryWithId(id).one_or_none()

    """
    existsWithId
    (class method)

        Runs an "exists" query on its class.

        Input:  id  (int)   PK of object to be queried
        Return: (bool) indicating whether a class object having the given id exists in the database.
    """

    @classmethod
    def existsWithId(cls, id):
        return cls.exists(qry=cls.__queryWithId(id))

    """
    exists
    (static method)

        Runs the result of an "exists" query of the given query.

        Input:  qry (Query)   Query object.
        Return: (bool) indicating whether the given query found anything.
    """

    @staticmethod
    def exists(qry):
        return DM.query(qry.exists()).scalar()

    """
    queryCount
    (class method)

        Runs a query on this class that returns a count of the number of entries that match the
        specifications, but not the mapped objects themselves
    """

    @classmethod
    def queryCount(cls):
        return DM.query(func.count(cls.id))


ID_INCREMENT = 100


class ID:
    @staticmethod
    def ID(*args):
        return int(datetime.now().timestamp() * 1e6)

    # Use this type of id for objects that will be created in fast-succession
    @staticmethod
    def IncrementID():
        global ID_INCREMENT
        ID_INCREMENT += 1
        return int(f"{int(datetime.now().timestamp()*1e4)}{'%03d' % ID_INCREMENT}")


class Cast:
    def cast(self, new_class):
        self.__class__ = new_class


# OBJECT class pulls all other classes and methods together
class OBJECT(AutoCommit, Barcode, Query, ID, Cast):
    pass


###################################


def main():
    pass


if __name__ == "__main__":
    # main()
    MeasurementPan5pass
