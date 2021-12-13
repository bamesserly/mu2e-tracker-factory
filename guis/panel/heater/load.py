import guis.panel.heater.load_heat_csv_into_db as load, os, sys, pandas as pd, shutil, time
from pathlib import Path

def copy_csv(filename):
    rootdir = "data/Panel data/external_gui_data/heat_control_data/"
    copy_path = "guis/panel/heater/problem_files/"
    original = rootdir + filename
    target = copy_path + filename
    shutil.copyfile(original, target)

if __name__ == "__main__":
    
    # Get list of all files
    rootdir = "data/Panel data/external_gui_data/heat_control_data/"
    dirs = os.listdir(rootdir)
    date_format = "%Y-%m-%d"
    
    # Make dict {panel : (timestamp, process, file)}
    heat_files_info = {}
    bad_files = []
    for f in dirs:
        f = f.replace(".csv", "")
        parsed_filename = f.split("_")
    
        # Add messed up files to bad list and move on
        if len(parsed_filename) not in [2,3]:
            bad_files.append(f)
            continue
    
        # Parse info from filename
        panel_number = parsed_filename[0]
        date = parsed_filename[1]
        process = None if len(parsed_filename) == 2 else parsed_filename[2]
    
        # Validate parsed info
        # Send bad files to a bad list, add good entries to the dictionary
        try:
            panel_number = int(panel_number[2:]) # remove "MN", convert to int
            assert panel_number < 200 # require panel number < 200
            date = time.strptime(date, date_format)
            
        except: # catch invalid panel number or date format
            bad_files.append(f)
        else:
            if panel_number not in heat_files_info:
                heat_files_info[panel_number] = []
            heat_files_info[panel_number].append((date, process, f))
            
            
    

# Filter out panels with more than or fewer than 3 files:
    to_remove = []
    for key in heat_files_info:
        if len(heat_files_info[key]) != 3:
            to_remove.append(key)
            for i in heat_files_info[key]:
                bad_files.append(i[2])
    for i in to_remove:
        del heat_files_info[i]
        
# Loop panels in this dict:
# # if a panel's files have process explicitly in filename, add to a "good"
# # list or dict.
# # otherwise, compare the timestamps for each of the three entries  and assign
# # them a process
    good = {}
    for key in heat_files_info:
        timestamps = [time.mktime(heat_files_info[key][0][0]), time.mktime(heat_files_info[key][1][0]), time.mktime(heat_files_info[key][2][0])]
        output = sorted(range(len(timestamps)), key=lambda k: timestamps[k])
        
        # add correct processes and panel numbers to good dictionary
        good[key] = []
        good[key].append((heat_files_info[key][output[0]][2], 1))
        good[key].append((heat_files_info[key][output[1]][2], 2))
        good[key].append((heat_files_info[key][output[2]][2], 6))
        
        
# # run the script on the good list

for key in good:
    for i in good[key]:
    
        path = Path(rootdir + i[0] + ".csv").absolute()
        load.run(key, i[1], rootdir + i[0] + ".csv")

#
# Copy "bad" files to separate folder.

for i in bad_files:
    copy_csv(i + ".csv")
