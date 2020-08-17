import pyautogui
import time
import os
import csv
import sys

class StrawFailedError(Exception):
    # Raised when attempting to test a straw that has failed a previous step, but was not removed
    def __init__(self, message):
        super().__init__(self, message)
        self.message = message

class Check:
    palletDirectory = os.path.dirname(__file__) + '/../../../Data/Pallets/' 
    workerDirectory = os.path.dirname(__file__) + '/../../../Data/workers/straw workers/CO2 endpiece insertion/'
    epoxyDirectory =  os.path.dirname(__file__) + '/../../../Data/CO2 endpiece data/'
    boardPath = os.path.dirname(__file__) + '/../../../Data/Status Board 464/'

    def __init__(self):
        self.path = ''
        self.history = []
        self.straws = []

    def strawPass(self, CPAL, straw, step, found = False):
        PASS = False

        if found:
            for line in self.history:
                if line[1] == step:
                    for index in range(len(line)):
                        if line[index] == straw and line[index + 1] == 'P':
                            PASS = True
                if line[1] == 'adds':
                    for index in range(len(line)):
                        if line[index] == straw and line[index + 1].startswith('CPAL'):
                            PASS = self.strawPass(line[index + 1], straw, step)
                        if line[index] == straw and line[index + 1].startswith('ST'):
                            PASS = self.strawPass(CPAL, line[index + 1], step)
        else:
            for palletid in os.listdir(self.palletDirectory):
                for pallet in os.listdir(self.palletDirectory + palletid + '/'):
                    if CPAL + '.csv' == pallet:
                        with open(self.palletDirectory + palletid + '/' + pallet, 'r') as file:
                            dummy = csv.reader(file)
                            history = []
                            for line in dummy:
                                if line != []:
                                    history.append(line)
                            for line in history:
                                if line[1] == step:
                                    for index in range(len(line)):
                                        if line[index] == straw and line[index + 1] == 'P':
                                            PASS = True
                                if line[1] == 'adds':
                                    for index in range(len(line)):
                                        if line[index] == straw and line[index + 1].startswith('CPAL'):
                                            PASS = self.strawPass(line[index + 1], straw, step)
                                        if line[index] == straw and line[index + 1].startswith('ST'):
                                            PASS = self.strawPass(CPAL, line[index + 1], step)
        return PASS

    def strawPassAll(self, CPAL, straw):
        results = []
        steps = ['prep','ohms','C-O2','leak','lasr','leng','silv']
        for step in steps:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)

    def palletPass(self, CPAL, step):
        results = []
        
        for straw in self.straws:
            results.append(self.strawPass(CPAL, straw, step, True))
        if results == []:
            return False
        return all(results)

    def palletPassAll(self, CPAL):
        results = []
        steps = ['prep','ohms','C-O2','leak','lasr','leng','silv']
        for step in steps:
            results.append(self.palletPass(CPAL, step))
        if results == []:
            return False
        return all(results)

    def getPath(self):
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '/'):
                if self.CPAL + '.csv' == pallet:
                    self.path = self.palletDirectory + palletid + '/' + self.CPAL + '.csv'
                    return

    def getStraws(self):
        with open(self.path, 'r') as file:
            dummy = csv.reader(file)
            for line in dummy:
                if line != []:
                    self.history.append(line)
            for entry in self.history[len(self.history ) - 1]:
                if entry.startswith('ST'):
                    self.straws.append(entry)

    def check(self, CPAL, steps):
        self.CPAL = CPAL
        self.getPath()
        self.getStraws()

        results = [self.palletPass(CPAL, s) for s in steps]
        steps1 = ['made','prep','ohms','C-O2','infl','leak','lasr','leng','silv']
        steps2 = ['Straw Made','Straw Prep','Resistance Test','CO2 End Piece Epoxy','Inflation','Leak Test','Laser Cut','Length Measurement','Silver Epoxy']

        steps_dict = {}

        for index, step in enumerate(steps1):
            steps_dict[step] = steps2[index]

        if all(results):
            return
        else:
            failed = []
            for i, step in enumerate(steps):
                if not results[i]:
                    failed.append(step)
            names = list(map(lambda x : steps_dict[x], failed))        
            raise StrawFailedError(CPAL + " failed step(s): " + ', '.join(names))
