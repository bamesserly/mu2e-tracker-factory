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

# # Straw batch composition of each panel

import pandas as pd
from pathlib import Path
import sys
import matplotlib.pyplot as plt
from numpy.testing import suppress_warnings
from numpy import ComplexWarning
from numpy import nan
import string
from pandas.api.types import CategoricalDtype

sys.path.append("/Users/Ben/Projects/mu2e-tracker-factory/")

# ## Read input file into df

batch_file = Path("2022-08-17_straws_on_panels.csv")
assert batch_file.is_file()
raw_df = pd.read_csv(batch_file, sep=",", skipinitialspace=True, na_values="\r\n")
raw_df

# ## Clean up the batch categories

# +
df = raw_df.copy()

print(len(df.batch.astype("category").unique().tolist()), "unique batches")

df["batch"] = df["batch"].str.strip()
df["batch"] = df["batch"].replace(nan, "nan")
df["batch"] = df["batch"].str.replace("[^\w\s]", "", regex=True)  # remove punctuation

# print(df.batch.astype('category').unique().tolist())
# print("\n".join(sorted(df.batch.astype('category').unique().tolist())))

batches = CategoricalDtype(
    categories=["oct", "nov", "dec-06-B4", "dec-other", "g-2", "proto", "na"],
    ordered=True,
)
codes = {
    "10": "oct",
    "11": "nov",
    "XX": "dec-06-B4",
    "12": "dec-other",
    "g2": "g-2",
    "08": "proto",
    "na": "unknown",
}

# convert g-2:
for i in range(1, 7):
    df["batch"] = df["batch"].replace(f"123456B{i}", "g2")

# convert 12-06-17.B4
df["batch"] = df["batch"].replace("120617B4", "XX")

# new column with readable string
df["batch_cats"] = df["batch"].str[:2].astype("category").map(codes)

# print(df.batch_cats.unique())
# -

# ## Batch distribution per panel

# #### convert batches into categories and clean

# #### Straw Batch All Panels

# +
# final_df[final_df['number']==192][['position_number','rate']]
# final_df[final_df['number'] == 173]

# +
fig, ax = plt.subplots(1, 1)

# distribution of batches across all panels
df["batch_cats"].value_counts(sort=False).plot.bar(rot=0, figsize=(15, 8))

ax.set_ylabel("n straws", fontsize=25)
ax.set_xlabel("Batch", fontsize=25)
ax.set_title(
    f"Straw Batch All Panels (MN{df.number.min()} - MN{df.number.max()})", fontsize=25
)
fig.savefig(f"batch_composition_all_straws.png")

plt.show()
# plt.close(fig)
# -

# #### Straw Batch Composition vs Panel

# +
fig, ax = plt.subplots(1, 1)

# distribution of batches vs panel
df.groupby(["number", "batch_cats"])["batch_cats"].count().unstack().plot.bar(
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
ax.set_title(
    f"Batch Composition by Panel (MN{df.number.min()} - MN{df.number.max()})",
    fontsize=25,
)
fig.savefig(f"batch_composition_by_panel.png")

plt.show()
# plt.close(fig)
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
