import matplotlib.pyplot as plt
import os, sys, math, re, time
import numpy as np

# Function that makes and saves a graph for visually summarizing
# the continuity test results.
def make_graph(filename, panelid):
    idx_wires = []
    idx_straws = []
    resistances_wires = []
    resistances_straws = []
    with open(filename, "r") as infile:
        for line in infile:
            if not line.startswith("#"):
                index, wire, resistance, d_resistance = line.replace(" ", "").split(",")
                # not valid reading
                if resistance == "inf":
                    pass
                # valid reading
                else:
                    # check if the reading was made for wire or straw
                    if wire == "1":
                        idx_wires.append(int(index))
                        resistances_wires.append(float(resistance))
                    else:
                        idx_straws.append(int(index))
                        resistances_straws.append(float(resistance))

    # sort (wire, measurements) and (straw, measurements) in ascending order
    sorted_idx_wires = sorted(
        zip(idx_wires, resistances_wires), key=lambda x: int(x[0])
    )
    sorted_idx_straws = sorted(
        zip(idx_straws, resistances_straws), key=lambda x: int(x[0])
    )

    fig, ax = plt.figure()
    x = [0, 20, 40, 60, 80, 100]
    y = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
    # Get x and y values for wires and straws
    X_wires, Y_wires = zip(*sorted_idx_wires)
    X_straws, Y_strws = zip(*sorted_idx_straws)
    X_w = np.array(X_wires)
    Y_w = np.array(Y_wires)
    X_s = np.array(X_straws)
    Y_s = np.array(Y_strws)
    plt.scatter(X_w, Y_w, s=50, facecolor="none", edgecolors="r")
    plt.scatter(X_s, Y_s, marker="s", s=50, facecolor="none", edgecolors="b")
    fig.savefig(filename[:-3] + "png")
    plt.legend(loc="upper right")
    plt.title("Panel ID " + panelid + " Resistance Test")
    plt.xlabel("Straw number")
    plt.xticks(x)
    ax.set_yticks(y)
    ax.set_yticklabels(
        ["0", "50", "100", "150", "200", "250", "300", "350", "400", "450", "500"]
    )
    plt.ylabel("Resistance")
    plt.yticks(y)
    plt.axis([0, 100, 0, 500])
    plt.show()
    fig.savefig(filename[:-3] + "png")


if __name__ == "__main__":
    make_graph()
