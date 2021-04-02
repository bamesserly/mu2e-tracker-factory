# import pyautogui
# import time

# screenWidth, screenHeight = pyautogui.size() # Get the size of the primary monitor.
# print("W {} H {}".format(screenWidth, screenHeight))

# print("Moving mouse")
# pyautogui.moveTo(960,540)
# print("Should be at x {} y {}".format(960,540))

# currentMouseX, currentMouseY = pyautogui.position() # Get the XY position of the mouse.
# print("W {} H {}".format(currentMouseX, currentMouseY))
# moves = [[100,200], [500,800], [1000,500]]

# for i in range(len(moves)):
#     pyautogui.moveTo(moves[i])
#     print("Should be at x {} y {}".format(moves[i][0],moves[i][1]))
#     X, Y = pyautogui.position()
#     print("Mouse is at x {} y {}".format(X,Y))
#     time.sleep(2)

# print("Moving mouse to the right side")
# pyautogui.moveTo(1200,900)
# pyautogui.click()

# print("Trying to open new file")
# pyautogui.hotkey("ctrl", "o")
# time.sleep(2)

# print("Moving mouse to cancel")
# pyautogui.moveTo(888,508)
# pyautogui.click()

# print("Trying to open laser cut by selecting it from the task bar menu")
# pyautogui.moveTo(714,1060)
# print("Should be at x {} y {}".format(714,1060))
# X, Y = pyautogui.position()
# print("Mouse is at x {} y {}".format(X,Y))
# time.sleep(2)
# print("Move mouse up a couple pixels to select window")
# pyautogui.move(0,-80)
# pyautogui.click()
# time.sleep(2)

# print("Laser program should be opened")
# print("Trying to open file")
# pyautogui.hotkey("ctrl", "o")

# print("Trying to move mouse")
# pyautogui.moveTo(1000,500)
# print("Should be at x {} y {}".format(1000,500))
# X, Y = pyautogui.position()
# print("Mouse is at x {} y {}".format(X,Y))

string = "../Cut File"
print(string[2:])
