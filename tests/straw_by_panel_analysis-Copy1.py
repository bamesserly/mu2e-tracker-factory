# ---
# jupyter:
#   jupytext:
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

# # Many straw studies
# #

import pandas as pd
from pathlib import Path
import sys

sys.path.append("/Users/Ben/Projects/mu2e-tracker-factory/")
import matplotlib.pyplot as plt
from numpy.testing import suppress_warnings
from numpy import ComplexWarning

leak_file = Path("all_leak_tests_2022-06.csv")
assert leak_file.is_file()
df = pd.read_csv(leak_file, sep=",")

# ## Merge the straws-by-panel df with the leak rate-by-straw df

final_df = straws_df.merge(df, on=["straw"], how="left")

df.to_csv("all_straw_info_MN173_MN235.csv")

final_df

# ## for straws without leak rates, see if their daughter has a leak rate
# ### TODO

from numpy import nan

# +
# select straws without leak rates
final_df[final_df["rate"].isna()]

# drop straws without leak rates
test_df = final_df[final_df["rate"].notna()]

# get batch, leak info from parent, which = daughter_straw_no - 30000
# -

# ## Sum leak rates by panel

fig, ax = plt.subplots(1, 1)
final_df.groupby(["number"])["rate"].sum().plot(kind="bar", figsize=(15, 8), ax=ax)
ax.set_ylabel("integrated straw leaks", fontsize=20)
ax.set_xlabel("panel", fontsize=20)
# ax.set_title("all panels",fontsize=25)
fig.savefig(f"summed_straw_leaks_by_panel_2.png")
plt.close(fig)

# ## Mean leak rates by panel

fig, ax = plt.subplots(1, 1)
ax = final_df.groupby(["number"])["rate"].mean().plot(kind="bar", figsize=(15, 8))
ax.set_ylabel("mean straw leak rate", fontsize=20)
ax.set_xlabel("panel", fontsize=20)
fig.savefig(f"mean_straw_leak_rate_per_panel_2.png")
plt.close()

# ## Median leak rates by panel

fig, ax = plt.subplots(1, 1)
ax = final_df.groupby(["number"])["rate"].median().plot(kind="bar", figsize=(15, 8))
ax.set_ylabel("median straw leak rate", fontsize=20)
ax.set_xlabel("panel", fontsize=20)
fig.savefig(f"median_straw_leak_rate_per_panel_2.png")
plt.close()

# ## all straw leaks across all panels
# #### TODO make this a heat map/histogram

fig, ax = plt.subplots(1, 1)
final_df.plot.scatter(
    ax=ax, x="position_number", y="rate", ylim=(-2e-5, 22e-5), figsize=(15, 10)
)
ax.set_ylabel("individual straw leak rate", fontsize=25)
ax.set_xlabel("straw position on panel", fontsize=25)
ax.set_title("all panels", fontsize=25)
fig.savefig(f"all_straw_leaks_by_position.png")
plt.close(fig)

yvals = final_df["rate"].to_numpy()
xvals = final_df["position_number"].to_numpy()

# +
import numpy as np

fig, ax = plt.subplots(1, 1)
# Creating bins
x_min = np.min(xvals)
x_max = np.max(xvals)

y_min = np.min(yvals)
y_max = np.max(yvals)

x_bins = np.linspace(x_min, x_max, 50)
y_bins = np.linspace(y_min, y_max, 20)

ax.hist2d(xvals, yvals, bins=[x_bins, y_bins])
# ax.hist2d(final_df.position_number, final_df.rate, bins=100)
# final_df.plot.hist2d(ax = ax, x='position_number',y='rate') #,ylim=(-2e-5,22e-5),figsize=(15,10))
# axes[0, 0].hist2d(data[:, 0], data[:, 1], bins=100)

# +
# final_df[final_df['number']==192][['pos','rate']]
# -

# ## straw leaks by panel vs straw position

for panel in range(173, 175):
    fig, ax = plt.subplots(1, 1)
    try:
        with suppress_warnings() as sup:
            sup.filter(ComplexWarning)
            # bar
            final_df[final_df["number"] == panel][
                ["position_number", "rate", "rate_err"]
            ].plot(
                x="position_number",
                y="rate",
                yerr="rate_err",
                kind="bar",
                figsize=(20, 10),
                ax=ax,
                ylim=(0, 13e-5),
            )

            # scatter (eww)
            # final_df[final_df['number']==panel][['pos','rate','rate_err']].plot(
            #    x='pos',y='rate',
            #    yerr='rate_err',
            #    kind="scatter",
            #    figsize=(20,10), ax = ax,ylim=(0,13e-5),s=60
            # )
    except TypeError:
        print("NO DATA", panel)
        plt.close(fig)
        continue
    except ValueError:
        print("problem?", panel)
        plt.close(fig)
        continue

    # calculate mean
    heights = final_df[final_df["number"] == panel]["rate"]
    freq = heights.value_counts().sort_index()
    freq_frame = freq.to_frame()
    mean = round(heights.mean(), 8)
    median = heights.median()

    ax.set_ylabel("individual straw leak rate", fontsize=25)
    ax.set_xlabel("straw position on panel", fontsize=25)
    ax.set_title(f"MN{panel} (mean={mean})", fontsize=25)
    fig.savefig(f"MN{panel}_bar.png")
    plt.close(fig)

# ## Straw leaks by panel vs leak rate histogram

for panel in range(173, 175):
    fig, ax = plt.subplots(1, 1)
    try:
        with suppress_warnings() as sup:
            sup.filter(ComplexWarning)
            result = final_df[final_df.number == panel]["rate"].hist(
                figsize=(14, 7), bins=12
            )
    except TypeError:
        print("NO DATA", panel)
        plt.close(fig)
        continue
    except ValueError:
        print("problem?", panel)
        plt.close(fig)
        continue

    # calculate mean
    heights = final_df[final_df["number"] == panel]["rate"]
    freq = heights.value_counts().sort_index()
    freq_frame = freq.to_frame()
    mean = round(heights.mean(), 8)
    median = heights.median()

    # mean line
    plt.axvline(mean, color="k", linestyle="dashed", linewidth=1)
    # plt.axvline(median, color='k', linestyle='dashed', linewidth=1)
    ax.set_xlim((0, 1e-4))
    ax.set_ylim((0, 25))
    ax.set_ylabel("n straws", fontsize=25)
    ax.set_xlabel("leak rate (sccm)", fontsize=25)
    ax.set_title(f"MN{panel}", fontsize=25)
    fig.savefig(f"MN{panel}_leak_hist.png")
    plt.close(fig)

# ## Batch distribution per panel

# #### convert batches into categories and clean

from pandas.api.types import CategoricalDtype

batches = CategoricalDtype(
    categories=["oct", "nov", "dec", "g-2", "proto", "na"], ordered=True
)
codes = {
    "10": "oct",
    "11": "nov",
    "12": "dec",
    "08": "proto",
    "g2": "g-2",
    "na": "unknown",
}

# +
# final_df[final_df['number']==192][['position_number','rate']]
# final_df[final_df['number'] == 173]

# +
df2 = final_df.copy()
# df2

# list of all batch numbers
# print(df2.batch.astype('category').unique().tolist())

# clean up
df2["batch"] = df2["batch"].replace("\r\n", nan)
df2["batch"] = df2["batch"].replace("110917.B6\r\n", "110917B6")
df2["batch"] = df2["batch"].replace("110717.B5\r\n", "110717B5")
# print(df2.batch.astype('category').unique().tolist())

# convert g-2:
df2["batch"] = df2["batch"].replace("123456B1", "g2")

# parse just the first two digits
df2["batch_parsed"] = df2["batch"].astype(str).str[:2].astype("category", Ordered=True)
print("all batches:\n", df2.batch_parsed.unique())

# map to a readable string
df2["batch_cats"] = df2["batch_parsed"].map(codes)
print(df2.batch_cats.unique())
# -

# #### Straw Batch All Panels

# +
fig, ax = plt.subplots(1, 1)

# distribution of batches across all panels
df2["batch_cats"].value_counts(sort=False).plot.bar(rot=0, figsize=(15, 8))

ax.set_ylabel("n straws", fontsize=25)
ax.set_xlabel("Batch", fontsize=25)
ax.set_title(f"Straw Batch All Panels (MN170 - MN230)", fontsize=25)
fig.savefig(f"batch_composition_all_straws.png")

plt.close(fig)
# -

# #### Straw Batch Composition vs Panel

# +
fig, ax = plt.subplots(1, 1)

# distribution of batches vs panel
df2.groupby(["number", "batch_cats"])["batch_cats"].count().unstack().plot.bar(
    stacked=True,
    figsize=(15, 8),
    ax=ax,
)

# identical batches vs panel plot
# pd.crosstab(index=df2['number'], columns=df2['batch_cats'], values=df2['number'], aggfunc='count').plot.bar(
#        stacked=True,
#        figsize=(15,8)
#    )
ax.set_ylim((0, 130))
ax.set_ylabel("N Straws", fontsize=25)
ax.set_xlabel("Panel", fontsize=25)
ax.set_title(f"Batch Composition by Panel (MN170 - MN230)", fontsize=25)
fig.savefig(f"batch_composition_by_panel.png")

plt.close(fig)
# -

# ## Paper pull composition by panel

# grades = CategoricalDtype(categories=["A","B","C","nan"], ordered=True)
grade_codes = {"A": "A", "B": "B", "C": "C", "nan": "unknown"}
df2["ppg"] = df2["paper_pull_grade"].astype(str).astype("category", Ordered=True)
df2["ppg"] = df2["ppg"].map(grade_codes)
print("all grades:\n", df2.ppg.unique())

# #### ppg all panels

# +
# all grades all panels
fig, ax = plt.subplots(1, 1)

# distribution of batches across all panels
df2["ppg"].value_counts(sort=False).plot.bar(rot=0, figsize=(15, 8))

ax.set_ylabel("n straws", fontsize=25)
ax.set_xlabel("Paper Grade", fontsize=25)
ax.set_title(f"Straw Paper Grade All Panels (MN170 - MN230)", fontsize=25)
fig.savefig(f"ppg_composition_all_straws.png")

plt.close(fig)
# -

# #### ppg composition vs panel

# +
fig, ax = plt.subplots(1, 1)

# distribution of batches vs panel
df2.groupby(["number", "ppg"])["ppg"].count().unstack().plot.bar(
    stacked=True,
    figsize=(15, 8),
    ax=ax,
)

# identical batches vs panel plot
# pd.crosstab(index=df2['number'], columns=df2['batch_cats'], values=df2['number'], aggfunc='count').plot.bar(
#        stacked=True,
#        figsize=(15,8)
#    )
# ax.bar_label(ax.containers[0])
ax.set_ylim((0, 130))
ax.set_ylabel("N Straws", fontsize=25)
ax.set_xlabel("Panel", fontsize=25)
ax.set_title(f"Paper Grade Composition by Panel (MN170 - MN230)", fontsize=25)
fig.savefig(f"ppg_composition_by_panel.png")

plt.close(fig)
# -
