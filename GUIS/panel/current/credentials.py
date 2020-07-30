#
#   Credentials.py
#
#   Author: Joe Dill and
#   Email: dillx031@umn.edu
#
#   Python Class that verifies worker credentials for a given task (stationID) from a Google Sheet.

import typing, csv, os
import numpy as np
from pathlib import Path


class Credentials:
    def __init__(self, stationID, credentialsChecklist):

        # Dictionary where worker credentials are stored
        self.workerCredentials = {}
        self.stationID = stationID

        # Location of Credentials information
        # self.credentials_file = Path(__file__).parent / 'WorkerProficiencyChecklist.csv'
        # self.credentials_file = Path('../Credentials/WorkerProficiencyChecklist.csv').resolve()
        self.credentials_file = Path(credentialsChecklist).resolve()

        self.getWorkerCredentials()

    # Opens credentials file. Records proficiency of all workers for at given station in dictionary: self.workerCredentials
    def getWorkerCredentials(self):
        worksheet = []
        with open(self.credentials_file, "r") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                worksheet.append(row)
        worksheet = np.array(worksheet)

        # List of workers
        workers = worksheet[1:, 0]
        station_col = worksheet[:, np.where(worksheet[0] == self.stationID)[0]]
        proficiency = station_col[1:]

        # Save proficiency of each worker in dictionary: self.workerCredentials
        for i in range(len(workers)):
            verify = bool(proficiency[i] == "TRUE")
            self.workerCredentials[
                workers[i].upper().strip()
            ] = verify  # By default, save workerID's in CAPS and remove spaces

    # Returns proficiency of given workers at given test
    # Input:    (str) worker ID -or- (list) list of worker IDs
    # Returns:  (bool) indicating that (a) worker if proficient at that test
    def checkCredentials(self, workers):
        verify_worker = (
            lambda worker: worker.upper() in self.workerCredentials.keys()
            and self.workerCredentials[worker.upper()]
        )
        if type(workers) == list:
            proficiency = []
            for worker in workers:
                proficiency.append(verify_worker(worker))
            return any(proficiency)
        elif type(workers) == str:
            worker = workers.upper()
            return verify_worker(worker)
        else:
            return False

    # Returns first worker in list of workers that is certified at the current station
    # Input:    (list) of worker ID's
    # Returns:  (str) ID of worker proficient at that test
    def workerWithCredentials(self, workers: list) -> str:
        for worker in workers:
            if self.checkCredentials(worker):
                return worker
        return None

    # Re-calls getWorkerCredentials()
    def refresh(self):
        self.getWorkerCredentials()
