import os
import csv
from datetime import datetime

# Converts temperature in C to any
def tempConversion(temp, current_scale, desired_scale):
    current_to_C = {
        "F": lambda temp: (temp - 32) * (5 / 9),
        "C": lambda temp: temp,
        "K": lambda temp: temp - 273.15,
    }
    C_to_desired = {
        "F": lambda temp_C: temp_C * (9 / 5) + 32,
        "C": lambda temp_C: temp_C,
        "K": lambda temp_C: temp_C + 273.15,
    }
    return C_to_desired[desired_scale](current_to_C[current_scale](temp))


def getTempHumid(temp_scale="C"):
    directory = (
        os.path.dirname(__file__) + "\\..\\..\\..\\Data\\temp_humid_data\\464_main\\"
    )
    D = os.listdir(directory)
    filename = ""
    for entry in D:
        if entry.startswith("464_" + datetime.now().strftime("%Y-%m-%d")):
            filename = entry
    with open(directory + filename, "r") as file:
        data = csv.reader(file)
        i = "first"
        for row in data:
            if i == "first":
                i = "not first"
                continue
            else:
                temperature = tempConversion(float(row[1]), "C", temp_scale)
                humidity = float(row[2])
    return temperature, humidity


def getTemp(temp_scale="C"):
    return getTempHumid(temp_scale)[0]


def getHumid():
    return getTempHumid()[1]


def main():
    temp_scale = input("Enter desired temperature scale (F,C,K): ").strip().upper()
    if temp_scale not in ["F", "C", "K"]:
        temp_scale = "C"
    print("Temperature: " + format(getTemp(temp_scale), "5.2f") + " " + temp_scale)
    print("Humidity:    " + str(getHumid()) + "%")


if __name__ == "__main__":
    main()
