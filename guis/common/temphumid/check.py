import sys
import os
import time


def start_464():
    task2 = os.popen("schtasks /query /tn 464TempHumid").read()
    count = 0
    while count < 10 and not ("Running" in task2):
        os.system("schtasks /run /tn 464TempHumid")
        time.sleep(0.2)
        task2 = os.popen("schtasks /query /tn 464TempHumid").read()
        count += 1

    if count == 10:
        return True
    else:
        return False


def start_464B():
    task1 = os.popen("schtasks /query /tn 464B").read()
    count = 0
    while count < 10 and not ("Running" in task1):
        os.system("schtasks /run /tn 464B")
        time.sleep(0.2)
        task1 = os.popen("schtasks /query /tn 464B").read()
        count += 1

    if count == 10:
        return True
    else:
        return False


failed_464B = False
failed_464 = False

failed_464B = start_464B()
failed_464 = start_464()

if failed_464B and not failed_464:
    print("An arduino error has occured with 464B arduino")
    print("Unplug and replug in arduino")
    input("Press <ENTER> to continue after replugging in arduino")
    start_464B()

if not failed_464B and failed_464:
    print("An arduino error has occured with 464 arduino")
    print("Unplug and replug in arduino")
    input("Press <ENTER> to continue after replugging in arduino")
    start_464()

if failed_464B and failed_464:
    print("An arduino error has occured with both 464 and 464B arduinos")
    print("Unplug and replug in arduinos")
    input("Press <ENTER> to continue after replugging in arduinos")
    start_464()
    start_464B()

sys.exit(0)
