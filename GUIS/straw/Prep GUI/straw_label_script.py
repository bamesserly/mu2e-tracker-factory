###
# straw_label_script.py: Used to make barcodes for initial straw prep
#   does not require any user input as it will automatically keep track of
#   all necessary information
# Created by: Matthew Heil, July 2018, heilx069@umn.edu
###

# 5/9/2018
# changed paths to absolute ones so this may be run from different directories. -SP
#
import pyautogui, subprocess
import time
import os
from datetime import datetime

# automatically keep track of the number of straw batches done in a day
# this also works if the program is closed
def update_daily_num():
    if os.path.exists("dailytotal.txt"):
        f = open("dailytotal.txt", "r")
    else:
        f = open("dailytotal.txt", "w+")
        f.write("0")

    data = f.read()
    f.close()
    f = open("dailytotal.txt", "w")
    num = int(data) + 1
    if num > 99:
        num = 0  # if 99 batches done, reset to 0
    if num < 10:
        strnum = "0" + str(num)
    else:
        strnum = str(num)
    ndata = data.replace(data, strnum)
    f.write(ndata)
    f.close()
    return strnum


def reset_daily_num():
    if os.path.exists("dailytotal.txt"):
        f = open("dailytotal.txt", "r")
    else:
        f = open("dailytotal.txt", "w+")
        f.write("0")

    f.write("00")
    f.close()


def update_cpal_num():
    f = open(
        os.path.dirname(__file__) + "/../../../Data/Straw Prep Data/cpalnum.txt", "r",
    )
    data = f.read()
    f.close()
    f = open(
        os.path.dirname(__file__) + "/../../../Data/Straw Prep Data/cpalnum.txt", "w",
    )
    num = int(data) + 1
    if num > 9999:
        num = 0  # reset cpal if it gets too far
    if num < 1000 and num >= 100:
        strnum = "0" + str(num)
    elif num < 100 and num >= 10:
        strnum = "00" + str(num)
    elif num < 10:
        strnum = "000" + str(num)
    else:
        strnum = str(num)
    ndata = data.replace(data, strnum)
    f.write(ndata)
    f.close()
    return strnum


def check_new_day():
    if os.path.exists("date.txt"):
        f = open("date.txt", "r")
    else:
        f = open("date.txt", "w+")

    data = f.read()
    f.close()
    if datetime.today().strftime("%m%d%y") != data:
        reset_daily_num()
        f = open("date.txt", "w")
        f.write(datetime.today().strftime("%m%d%y"))
        f.close()


# function to open the label template
def open_template(tmpt):
    pyautogui.click(x=1025, y=263)
    time.sleep(1)
    pyautogui.click(x=55, y=67)
    time.sleep(1)
    pyautogui.click(x=225, y=439)
    pyautogui.typewrite(tmpt)
    pyautogui.press("enter")
    time.sleep(1)


# prints the labels once in zebra
def lblprint(num):
    pyautogui.keyDown("ctrl")
    pyautogui.press("p")
    pyautogui.keyUp("ctrl")
    time.sleep(2)
    pyautogui.typewrite(str(num))
    pyautogui.press("enter")


# changes the size of the barcodes to fit label
def adjust_size(doer):
    if doer:
        pyautogui.moveTo(900, 460)
        pyautogui.click(button="right")
        pyautogui.click(x=900, y=625)
        time.sleep(5)
        pyautogui.click(x=865, y=387)
        pyautogui.press("backspace")
        pyautogui.press("2")
        pyautogui.press("enter")


# changes labels to say CO2..... or SE.......
def change_label(string, doer, count):
    global cur_date
    pyautogui.moveTo(835, 486)
    pyautogui.click(clicks=2)
    pyautogui.press("end")
    for _ in range(13):
        pyautogui.press("backspace")
    cur_date = datetime.today().strftime("%m%d%y")
    pyautogui.typewrite(string + str(cur_date) + "." + count)
    pyautogui.click(x=1000, y=625)
    adjust_size(doer)
    lblprint(1)


# main code
def print_barcodes():
    check_new_day()
    cpal_num = update_cpal_num()
    count = update_daily_num()
    zebra = subprocess.Popen(
        ["C:/Program Files (x86)/Zebra Technologies/ZebraDesigner 2/bin/design.exe"]
    )
    time.sleep(4)
    # Open template
    open_template("PalletBarcodes.lbl")
    # print first two CPAL number labels
    pyautogui.moveTo(835, 486)
    pyautogui.click(clicks=2)
    pyautogui.press("end")
    for _ in range(4):
        pyautogui.press("backspace")
    pyautogui.typewrite(cpal_num)
    pyautogui.click(x=1000, y=625)
    lblprint(2)
    time.sleep(2)
    # print CO2 label
    change_label("CO2.", True, count)
    time.sleep(2)
    # print SE label
    change_label("SE.", False, count)
    time.sleep(2)
    zebra.kill()


# if __name__ == "__main__":
#    print_barcodes()
