import guis.panel.heater.load_heat_csv_into_db as load, os, sys, pandas as pd, shutil


def copy_csv(filename):
    rootdir = "data/Panel data/external_gui_data/heat_control_data/"
    copy_path = "guis/panel/heater/problem_files/"

    original = rootdir + filename
    target = copy_path + filename
    shutil.copyfile(original, target)





if __name__ == "__main__":
    rootdir = "data/Panel data/external_gui_data/heat_control_data/"
    dirs = os.listdir(rootdir)
    
    panel_numbers = []
    timestamps = []
    status = []
    process = []
    
    # initialize status
    for file in dirs:
        status.append("valid")

    # collect data on files
    count = 0
    for file in dirs:
        items = file.split("_")
        
        # save panel numbers
        panel_numbers.append(items[0][2:])
        
        # save timestamp
        timestamps.append(os.path.getmtime(rootdir + file))
        
        # determine if panel is valid or test
        if len(items[0][2:]) != 0:
            if int(items[0][2:]) >= 200:
                status[count] = "invalid"
        
        count += 1
    
    # mark files with too many of same number as invalid
    count = 0
    for i in panel_numbers:
        if panel_numbers.count(i) > 3:
            status[count] = "invalid"
        count += 1
    
    # determine processes
    outercount = 0
    for x in panel_numbers:
        temp_indices = []
        temp_numbers = []
        count = 0
        for y in panel_numbers:
            if x == y:
                temp_indices.append(count)
                count += 1
                
        # get ranking of timestamp in list
        older = 0
        for i in temp_indices:
            if timestamps[i] < timestamps[outercount]:
                older += 1
        if older == 0:
            process.append(1)
            print(1)
        elif older == 1:
            process.append(2)
            print(2)
        elif older == 2:
            process.append(6)
            print(6)
        else:
            process.append(10)
            print("problem")
        
        outercount += 1
            
    # sort through folder, acting upon previously collected data    
    count = 0
    for file in dirs:
        if status[count] == "valid":
            try:
                path = os.path.abspath(file)
                path = path.split("\\")
                path = path[0:-1]
                rejoin = ""
                for i in path:
                    rejoin = rejoin + i + "\\"
                path = rejoin + "data\\Panel data\\external_gui_data\\heat_control_data\\"
                
                load.run(panel_numbers[count], process[count], path + file)
                
            except:
                status[count] = "invalid"        
        else:
            copy_csv(file)    
        count += 1