# The purpose of this script is to check the time differences between duplicate
# straw_present entries.
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the SQLite database
conn = sqlite3.connect("file:data/database.db?mode=ro", uri=True)

# Read the straw_present table into a DataFrame
query = "SELECT * FROM straw_present"
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# All the unique groups of straw, position, and present, and only those groups
# that have more than one entry (i.e. duplicates).
# There are, like, 50 groups with more than 2 entries. Most only have 2.
grouped = df.groupby(["straw", "position", "present"]).filter(lambda x: len(x) == 2)

a_count = 0 # first entry has time_out
b_count = 0 # first entry does not have time_out
c_count = 0 # how often second entry doesn't have a time_out

# Calculate time differences
# In "_, group", _ is the unique triplet of straw, position, and present,
# and group is the DataFrame containing all the entries for that triplet
time_diffs = []
for _, group in grouped.groupby(["straw", "position", "present"]):
    sorted_group = group.sort_values(by="time_in")
    if pd.isnull(sorted_group["time_out"].iloc[1]):
        c_count += 1
    if pd.isnull(sorted_group["time_out"].iloc[0]):
        b_count += 1
        #time_diff = sorted_group["time_in"].iloc[1] - sorted_group["time_in"].iloc[0]
        #time_diffs.append(time_diff)
        #if(time_diff > 200_000):
        #    print(sorted_group)
    else:
        a_count += 1
        time_diff = sorted_group["time_out"].iloc[0] - sorted_group["time_in"].iloc[0]
        time_diffs.append(time_diff)

print("first entry has a time_out:", a_count)
print("first entry does not have a time_out:", b_count)
print("second entry doesn't have a time_out:", c_count)


"""
# Identify duplicate entries
duplicates = df[df.duplicated(subset=['straw', 'position', 'present'], keep=False)]
print(len(duplicates))

# Calculate time differences
time_diffs = []
for _, group in duplicates.groupby(['straw', 'position', 'present']):
    sorted_group = group.sort_values(by='time_in')
    for i in range(1, len(sorted_group)):
        time_diff = sorted_group['time_in'].iloc[i] - sorted_group['time_in'].iloc[i - 1]
        time_diffs.append(time_diff)
    #if len(group) > 1:
    #    sorted_group = group.sort_values(by='time_in')
    #    #print(sorted_group)
    #    #time_diff = sorted_group['time_out'].iloc[0] - sorted_group['time_in'].iloc[1]
    #    time_diff = sorted_group['time_out'].iloc[0] - sorted_group['time_in'].iloc[0]
    #    time_diffs.append(time_diff)
"""

# Create a DataFrame for time differences
#time_diff_df = pd.DataFrame(time_diffs, columns=["time_difference"])

time_diffs = [time_diff for time_diff in time_diffs if time_diff <= 150_000]

time_diff_df = pd.DataFrame(time_diffs, columns=['time_difference'])


# Plot the distribution of time differences
plt.hist(time_diff_df["time_difference"], bins=100, edgecolor="k", alpha=0.7)
plt.xlabel("Time Difference (seconds)")
plt.ylabel("Frequency")
plt.yscale('log')
plt.title("Distribution of Time Differences")
plt.show()

# Display the DataFrame
time_diff_df
