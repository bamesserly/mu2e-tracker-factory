import sys
import serial

def get_measurements(serial_connection):
    indexList = [
        [23, 19, 15, 11, 7, 3],
        [22, 18, 14, 10, 6, 2],
        [21, 17, 13, 9, 5, 1],
        [20, 16, 12, 8, 4, 0],
    ]
    measNum = 1  # position number minus 1
    index = 0
    measLet = "abcdefghijklmnop"
    for char in measLet:
        appendList = indexList[index]
        serial_connection.write(bytes(char + "r", "ascii"))
        rawData = serial_connection.readline().decode("utf-8").rstrip().split(",")
        print(rawData)
        if rawData[0] != char:
            return False
        del rawData[0]
        if measNum % 4 == 0:
            index += 1
        measNum += 1

for i in range(0,10):
    com = f"Com{i}"
    try:
        serial_connection = serial.Serial(com, 9600, timeout=10)
    except Exception as e:
        print(com, "failed")
        continue

    print(com, "connection success")

    try:
        get_measurements(serial_connection)
    except serial.serialutil.SerialException:
        print(f"{com} Serial exception")
    except FileNotFoundError as e:
        print(f"{com} File not found")
