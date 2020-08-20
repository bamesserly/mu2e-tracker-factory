import os, time
from distutils.dir_util import copy_tree
from datetime import datetime

src = "C:/Users/mu2e/Desktop/Mu2e-Factory/Straw lab GUIs/Leak Test GUI/Leak Test Results/"
tgt = "//spa-mu2e-network/Production_Environment/Data/Leak test data/Leak Test Results/"

print("Copy and Backup of C:/Users/mu2e/Desktop/Mu2e-Factory/Straw lab GUIs/Leak Test GUI/Leak Test Results\n")
while True:
    now = datetime.now()
    hr = now.hour
    if (hr % 6) == 0: # Check every hour if its been a quarter of the day
        print("Starting Copy and Backup")
        try:
            copy_tree(src,tgt,update=1) #Most efficient update tool, does not handle removed files
        except:
            print("Unable to copy tree, files possibly in use.")
        print("Finished Copy and Backup\n")
        print("Please do not close me\n")
    time.sleep(3600)


