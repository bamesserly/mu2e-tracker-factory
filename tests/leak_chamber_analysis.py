# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import pandas as pd
from pathlib import Path
import sys

sys.path.append("/Users/Ben/Projects/mu2e-tracker-factory/")
import matplotlib.pyplot as plt

# ## Histogram of all leak tests -- one plot per chamber
# Questions:
# - are the chambers behaving well?
# - for the chambers that we've retired, can we bring them back?
#
# Answers: things are generally looking good.
#
# other things to look at:
# - measure of "gaussian-ness"
# - std dev
# - error (probably not useful)
#
# Conclusion: But this study is basically done.

leak_file = Path("all_leak_tests_2022-06.csv")
assert leak_file.is_file()
df = pd.read_csv(leak_file, sep=",")
nchambers = 25
chamber_data = {}
for chamber in range(nchambers):
    print("chamber", chamber)
    fig, ax = plt.subplots(1, 1)

    # binning
    bins = list(range(0, 21))
    bins = [x * 1e-5 for x in bins]
    # bins.append(20e-5)
    bins.append(50e-5)
    bins.append(200e-5)  # add overflow bin

    # data for just this chamber
    data = df[df.chamber == chamber]["rate"]

    # make the plot
    result = data.hist(figsize=(14, 7), bins=bins)

    # some properties of this hist
    bin_contents = data.squeeze().value_counts(bins=bins).sort_index()
    ymax = ax.get_ylim()[1]
    mean = round(data.mean(), 8)
    median = round(data.median(), 8)

    # median/mean line:
    plt.axvline(median, color="k", linewidth=1)
    ax.text(median + 0.5e-5, 0.8 * ymax, f"Median = {median}", fontsize=15, color="k")

    # pass/fail line
    plt.axvline(9.6e-5, color="r", linewidth=1)
    plt.text(
        10.0e-5, 0.5 * ymax, "pass threshold = 9.6e-5 sccm", fontsize=15, color="r"
    )

    # label overflow
    n_overflow = bin_contents.iat[-1]
    plt.text(46.0e-5, 0.25 * ymax, f"Overflow\n{n_overflow}", fontsize=15)
    overflow_rate = round(n_overflow / data.count(), 4)

    # label passing rate
    n_passing = bin_contents[:10].sum()
    pass_rate = round(n_passing / data.count(), 4)

    # Pack statistics into a dictionary.
    # Don't remember why I was doing this.
    chamber_data[chamber] = {}
    chamber_data[chamber]["n_passing"] = n_passing
    chamber_data[chamber]["n_total"] = data.count()
    chamber_data[chamber]["n_overflow"] = n_overflow
    chamber_data[chamber]["median"] = median
    chamber_data[chamber]["mean"] = mean

    # n total tests
    plt.text(
        40.0e-5, 0.95 * ymax, f"n total tests = {data.count()}", fontsize=15, color="k"
    )
    plt.text(
        40.0e-5,
        0.90 * ymax,
        f"overflow % = {round(overflow_rate*100,3)}%",
        fontsize=15,
        color="k",
    )
    plt.text(
        40.0e-5,
        0.85 * ymax,
        f"pass % = {round(pass_rate*100,3)}%",
        fontsize=15,
        color="k",
    )

    ax.set_xlim((0, 51e-5))
    # ax.set_ylim((0,25))
    # ax.set_yscale("log")
    ax.set_ylabel("n tests", fontsize=25)
    ax.set_xlabel("leak rate (sccm)", fontsize=25)
    ax.set_title(f"All Straw Leak Tests\nChamber {chamber}", fontsize=25)
    fig.savefig(f"leak_tests_all_Chamber{chamber}.png")
    plt.close(fig)
print(chamber_data)
