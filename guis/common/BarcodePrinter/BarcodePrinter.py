###
# BarcodePrinter.py
#
# Opens Zebra Designer and prints barcodes
#
# Created by: Joe Dill, January 2019, dillx031@umn.edu
#
###

import pyautogui
import subprocess
import time
import os
from pathlib import Path


class BarcodePrinter:
    def __init__(self):
        self._default_click_position = (800, 450)
        # sys.path.insert(0, os.path.dirname(__file__) + '/../../../Modules/BarcodePrinter/')
        self._barcode_file = ("X:\\Data\\BarcodePrinter\\barcode.lbl")
        self._zebra_open = False

        self._bar_width = 3
        self._print_number = 1

    def _open_zebra(self):
        if not self._zebra_open:
            # Open lbl file
            subprocess.Popen(
                [
                    "X:\\Data\\BarcodePrinter\\barcode.lbl"
                ],
                shell=True,
            )
            time.sleep(6)
            self._zebra_open = True

    def _close_zebra(self):
        if self._zebra_open:
            pyautogui.click(1582, 12)
            pyautogui.press(["tab", "enter"])

    def print_barcode(
        self, string, bar_width=None, number=1, close_when_finished=False
    ):
        print("BP, print Barcode")
        self._open_zebra()
        self._change_label_text(string)
        self._adjust_size(bar_width)
        self._allign_label()
        self._change_label_text(string)
        self._adjust_size(bar_width)
        self._allign_label()
        self._print(number)
        if close_when_finished:
            self._close_zebra()

    def _print(self, number=1):
        pyautogui.hotkey("ctrl", "p")
        time.sleep(1)
        if number != self._print_number:
            pyautogui.typewrite(str(number))
            self._print_number = number
        pyautogui.press("enter")
        time.sleep(2)

    def _change_label_text(self, string):
        pyautogui.click(self._default_click_position, clicks=2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.typewrite(string)
        pyautogui.hotkey("shift", "tab")
        time.sleep(1)
        pyautogui.press("enter")

    def _adjust_size(self, bar_width=None):
        # Check if size adjstments are needed
        if bool(bar_width) and bar_width != self._bar_width:
            # Open 'Bar code properties'
            pyautogui.click(self._default_click_position, button="right")
            pyautogui.click(875, 608)
            time.sleep(2)
            # Change bar width
            pyautogui.click(875, 383)
            pyautogui.press("backspace")
            pyautogui.typewrite(str(bar_width))
            self._bar_width = bar_width

    def _allign_label(self):
        pyautogui.click(self._default_click_position, button="right")
        pyautogui.click(875, 560)
        time.sleep(1)
        pyautogui.press("enter")


def main():
    bp = BarcodePrinter()
    bp.print_barcode("CPAL8000", bar_width=3, number=2, close_when_finished=False)
    bp.print_barcode("SE.011019.02", bar_width=2, number=1, close_when_finished=False)
    bp.print_barcode("CO2.011019.02", bar_width=2, number=1, close_when_finished=True)
    # If this tries to print thousands of barcodes someone may have unchecked the "close after printing" checkbox in the print dialogue for the zebra printer.


if __name__ == "__main__":
    main()
