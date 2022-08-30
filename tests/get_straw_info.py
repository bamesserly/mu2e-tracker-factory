# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
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

# +
# Look up a straw's info: all of it's leak rates, batch, ppg, panel and position.
#
# Note 1: Only current up to 2022-06-12 at the moment.
#
# Note 2: MOST of the prep data is missing. Isaiah is pretty close to uploading
# all of that into the DB. (2022-08-30).
#
# Note 3: Panel/position info should be mostly good after panel 173. I don't
# remember where we're at with uploading the info for the previous panels.
# -

import pandas as pd
from pathlib import Path
from numpy import real

INPUT_FILE = Path("resources/all_straws_2022-06-13.csv")


class LeakTest:
    def __init__(self, df_entry):
        self.straw = df_entry.straw
        self.leak_data_file = Path(df_entry.leak_data_file).name
        self.leak_rate = df_entry.rate
        self.leak_rate_err = real(complex(df_entry.rate_err))
        self.status = df_entry.status
        try:
            self.panel = int(df_entry.number)
        except ValueError:
            self.panel = "NA"
        try:
            self.panel_position = int(df_entry.position_number)
        except ValueError:
            self.panel_position = "NA"
        self.batch = "NA" if pd.isna(df_entry.batch) else df_entry.batch
        self.ppg = df_entry.paper_pull_grade = (
            "NA" if pd.isna(df_entry.paper_pull_grade) else df_entry.paper_pull_grade
        )

    def __repr__(self):
        attrs = vars(self)
        return "\n".join("%s: %s" % item for item in attrs.items())


def get_straw_info(df, straw):
    straw_leak_tests = df.loc[df["straw"] == straw]
    return [LeakTest(test) for index, test in straw_leak_tests.iterrows()]


if __name__ == "__main__":
    assert INPUT_FILE.is_file()
    df = pd.read_csv(INPUT_FILE, sep=",", index_col=0)
    print("\nThis is the Straw Info Getter")
    while True:
        print("\n")
        try:
            straw = int(input("Enter straw ID> ")[-5:])
        except ValueError:
            print(
                "Invalid straw input. Must be 5 or 7 characters-long, like: ST01234 or 01234."
            )
            continue
        except KeyboardInterrupt:
            print("Goodbye")
            break
        leak_tests = get_straw_info(df, straw)
        print(len(leak_tests), "leak tests found for ST", straw, "\n")
        for leak_test in leak_tests:
            print(leak_test, "\n")
