import sqlalchemy as sqla
import matplotlib

matplotlib.use("TkAgg")  # or 'Qt5Agg', 'Agg'
import matplotlib.pyplot as plt
import pandas as pd
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

import matplotlib.pyplot as plt


def make_pie_chart(df):
    total_straws = 96

    # Calculate the percentage of present straws for each panel
    df["percentage"] = df["num_present_straws"] / total_straws * 100

    # Define the bins
    bins = [0, 25, 51, 95, 100]
    labels = ["0-25% full", "25-51% full", "51-95% full", "> 95% full"]

    # Categorize the data based on the bins
    df["category"] = pd.cut(
        df["percentage"], bins=bins, labels=labels, include_lowest=True, right=True
    )

    # Count the number of panels in each category
    category_counts = df["category"].value_counts(sort=False)

    print(category_counts)

    # Create the pie chart with raw counts in the labels
    labels_with_counts = [
        f"{label} ({count})" for label, count in zip(labels, category_counts)
    ]

    print(labels_with_counts)

    # Create the pie chart
    tol_colors = ["#BBCCEE", "#CCEEFF", "#CCDDAA", "#EEEEBB", "#FFCCCC", "#DDDDDD"]
    plt.figure(figsize=(8, 8))
    plt.pie(
        category_counts,
        labels=labels_with_counts,
        autopct="%1.1f%%",
        colors=tol_colors[: len(category_counts)],
    )
    plt.title("Panel Straw Population in DB")
    plt.savefig("panel_straw_percentage_pie_chart.png")


# Access the database in read-only mode
database = GetLocalDatabasePath()
engine = sqla.create_engine(
    "sqlite:///" + database + "?mode=ro",
    execution_options={"schema_translate_map": {None: None}},
)

# Define the query
query = """
SELECT straw_location.number, COUNT(*) as num_present_straws
FROM straw
INNER JOIN straw_present ON straw.id = straw_present.straw
INNER JOIN straw_position ON straw_present.position = straw_position.id
INNER JOIN straw_location ON straw_position.location = straw_location.id
WHERE straw_location.location_type = "MN"
AND straw_present.present = 1
GROUP BY straw_location.number;
"""

# Execute the query and fetch the results into a pandas DataFrame
with engine.connect() as connection:
    result = connection.execute(sqla.text(query))
    data = result.fetchall()
    df = pd.DataFrame(data, columns=["straw_location_number", "num_present_straws"])

# fill in the df with missing panels
n_total_panels = 283
all_panels = pd.DataFrame({"straw_location_number": range(1, n_total_panels + 1)})
df = all_panels.merge(df, on="straw_location_number", how="left").fillna(0)
df["num_present_straws"] = df["num_present_straws"].astype(int)

make_pie_chart(df)

# also plot the results in a histogram
plt.figure(figsize=(20, 6))
plt.bar(df["straw_location_number"], df["num_present_straws"], color="skyblue")
plt.xlabel("Straw Location Number")
plt.ylabel("Number of Present Straws")
plt.title("Number of Present Straws on MN Straw Locations")
x_ticks = range(0, len(df["straw_location_number"]), 10)
plt.xticks(x_ticks, [df["straw_location_number"].iloc[i] for i in x_ticks], rotation=45)
plt.tight_layout()
# plt.savefig("panel_straw_count_histogram.png")
plt.show()
