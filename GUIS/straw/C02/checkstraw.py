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
    palletDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Pallets\\'
    workerDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\workers\\straw workers\\CO2 endpiece insertion\\'
    epoxyDirectory = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\CO2 endpiece data\\'
    boardPath = '\\\\MU2E-CART1\\Users\\Public\\Database Backup\\Status Board 464\\'

    def strawPass(self, CPAL, straw, step):
        PASS = False
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
                if CPAL + '.csv' == pallet:
                    with open(self.palletDirectory + palletid + '\\' + pallet, 'r') as file:
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
        PASS = False
        results = []
        steps = ['prep','ohms','C-O2','leak','lasr','leng','silv']
        for step in steps:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)

    def palletPass(self, CPAL, step):
        PASS = False
        results = []
        straws = []
        for palletid in os.listdir(self.palletDirectory):
            for pallet in os.listdir(self.palletDirectory + palletid + '\\'):
                if CPAL + '.csv' == pallet:
                    with open(self.palletDirectory + palletid + '\\' + pallet, 'r') as file:
                        dummy = csv.reader(file)
                        history = []
                        for line in dummy:
                            if line != []:
                                history.append(line)
                        for entry in history[len(history ) - 1]:
                            if entry.startswith('ST'):
                                straws.append(entry)
        for straw in straws:
            results.append(self.strawPass(CPAL, straw, step))
        if results == []:
            return False
        return all(results)

    def palletPassAll(self, CPAL):
        PASS = False
        results = []
        steps = ['prep','ohms','C-O2','leak','lasr','leng','silv']
        for step in steps:
            results.append(self.palletPass(CPAL, step))
        if results == []:
            return False
        return all(results)

    def check(self, CPAL, steps):
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
