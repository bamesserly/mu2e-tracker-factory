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

# # Clean and analyze HV data
# Never got very far on this.

# Multiple measurements may exist for a single channel.
# Need some way to choose between them, or remove certain duplicates.

# Next: combine current_left and current_right columns. We thought side might matter, but it doesn't.
# Not sure what to do when measurements exist for right and left sides.

# Then: make a new df where each panel only has 48 entries and we sum the current for n and n+1.

# +
import pandas as pd
from pathlib import Path

# read csv file into dataframe
# process 5 merged into process 6 at some point, and process 5 was deprecated.
# so process 5 measurements are also 1500V post-pin protectors.

# Here's query:
"""
SELECT straw_location.location_type, straw_location.number, procedure.station, measurement_pan5.position, measurement_pan5.current_left, measurement_pan5.current_right, measurement_pan5.is_tripped, measurement_pan5.timestamp 
FROM straw_location
INNER JOIN procedure on procedure.straw_location = straw_location.id
INNER JOIN measurement_pan5 on measurement_pan5.procedure = procedure.id
WHERE procedure.station = "pan6" OR procedure.station = "pan5"
"""

infile = Path("/Volumes/GoogleDrive/My Drive/all_mn_pro5_and_pro6_currents.csv")
df = pd.read_csv(infile)
df.head()
# -

# Let's just have a look at a single panel
df_test = df[df["number"] == 102]
df_test = df_test.sort_values(by=["position"])
df_test = df_test[
    ["position", "current_left", "current_right", "timestamp"]
]  # timestamp is seconds since the unix epoch
print(df_test.shape)
print(df_test.to_string())
