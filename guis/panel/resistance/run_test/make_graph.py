import matplotlib.pyplot as plt
import os, sys, math, re, time
import numpy as np
from itertools import islice
import csv
from guis.common.getresources import GetProjectPaths
from pathlib import Path

# Function that makes and saves a graph for visually summarizing
# the continuity test results.
def make_graph(filename, panelid, logfilename, stage_tag=""):
    idx_wires = []
    idx_straws = []
    resistances_wires = []
    resistances_straws = []
    with open(filename, "r") as infile:
        filt = islice(infile, 12, None)  # filter to skip 12 lines
        wr = csv.reader(filt)
        for line in wr:
            if line:
                index = line[0]
                wire = int(line[1])
                resistance = line[2]
                d_resistance = line[3]
                # not valid reading
                if resistance == "inf":
                    pass
                # valid reading
                else:
                    # check if the reading was made for wire or straw
                    if wire == 1:
                        idx_wires.append(int(index))
                        resistances_wires.append(float(resistance))
                    else:
                        idx_straws.append(int(index))
                        resistances_straws.append(float(resistance))
            else:
                pass

    # sort (wire, measurements) and (straw, measurements) in ascending order
    sorted_idx_wires = sorted(
        zip(idx_wires, resistances_wires), key=lambda x: int(x[0])
    )
    sorted_idx_straws = sorted(
        zip(idx_straws, resistances_straws), key=lambda x: int(x[0])
    )

    fig, ax = plt.subplots()
    x = [0, 20, 40, 60, 80, 100]
    y = [0, 50, 100, 150, 200, 250]
    # Get x and y values for wires and straws
    try:
        X_wires, Y_wires = zip(*sorted_idx_wires)
        X_straws, Y_strws = zip(*sorted_idx_straws)
    except:
        print("Wire measurements, straw measurements, or both are missing.")
        sys.exit()
    X_w = np.array(X_wires)
    Y_w = np.array(Y_wires)
    X_s = np.array(X_straws)
    Y_s = np.array(Y_strws)
    wires = plt.scatter(X_w, Y_w, s=50, facecolor="none", edgecolors="r")
    straws = plt.scatter(X_s, Y_s, marker="s", s=50, facecolor="none", edgecolors="b")
    fig.savefig(str(filename)[:-3] + "png")
    ax.legend([wires, straws], ["wires", "straws"], loc="upper right")
    plt.title("Panel ID " + panelid + " Resistance Test " + stage_tag)
    plt.xlabel("Straw number")
    plt.xticks(x)
    ax.set_yticks(y)
    ax.set_yticklabels(["0", "50", "100", "150", "200", "250"])
    plt.ylabel("Resistance")
    plt.yticks(y)
    maxy_s = Y_s[np.isfinite(Y_s)].max() + 20
    maxy_axis = max(maxy_s, 200)
    print(maxy_axis)
    plt.axis([0, 100, 0, maxy_axis])
    plt.show()
    outfilename = str(logfilename)[:-3] + "png"

    # Save the figure
    fig_outfile = GetProjectPaths()["panelresistancedata"] / "Plots" / f"MN{panelid}" / outfilename
    fig_outfile.parent.mkdir(exist_ok=True, parents=True)
    fig.savefig(str(fig_outfile))


if __name__ == "__main__":
    file_path = ""
    panelid = 0
    if len(sys.argv) < 3:
        print("Please specify the csv file to be used and the panel ID.\n")
        print(
            "Example: C:\\User\\Desktop\\Production\\Data\\Panel data\\FinalQC\\Resistance\\RawData\\name_of_file.csv"
        )
        print(
            "If you don't want to type all this, you can do right click -> Properties and copy the field location.\n"
        )
        file_path = Path(input("Path of the csv file: "))

        print("Example: 10")
        panelid = input("Panel id: ")

    else:
        file_path = Path(sys.argv[1])
        panelid = sys.argv[2]

    while not file_path.is_file():
        print("The csv specified does not exist")
        print("Please enter a valid csv file path or press Ctrl+C to quit")
        file_path = Path(input("Path of the csv file: "))

    logfile = file_path.name
    make_graph(file_path, panelid, logfile)
