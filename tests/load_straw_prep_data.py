from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv

paths = GetProjectPaths()

def parse_files():
    failure_count = 0
    cpal_list = []
    straw_information = {}
    failure_cpals = []

    
    # format: time, cpalid, cpal, paper pull time, worker
    straws = []
    
    for file in Path(paths['prepdata']).rglob('*.csv'):
        name=file.name
        f = open(file,'r')
        reader = csv.reader(f)
        
        prefixes={'cpal':name[-8:-4]}
        
        # determine whether the straws have a horizontal or vertical layout in the csv file
        
        vertical_layout=True
        for row in reader:
            try:
                if len(row[0]) != 0 and str(row[0])[0:3].lower() == 'pp.':
                    vertical_layout = False
            except:
                pass
            
        
        try:
            f = open(file,'r')
            reader = csv.reader(f)
            for row in reader:
                # acquire cpal prefix information
                if len(str(row[0])) == 16 and 2015 < int(str(row[0][0:4])) < 2023:
                    for i in row:
                        if len(str(i)) == 16 and 2015 < int(str(i[0:4])) < 2023:
                            prefixes['time'] = str(i)
                        elif str(i[0:7]).upper() == 'CPALID':
                            prefixes['cpalid'] = int(i[7:9])
                        elif str(i[-2]) == 'B':
                            prefixes['batch'] = str(i)
                        elif str(i[0:3]).lower() == 'wk-':
                            prefixes['worker'] = str(i)
                    break

                    
            # acquire constituent straw information
            f = open(file,'r')
            reader = csv.reader(f)
            cpal_straws = []
            if vertical_layout is True:
                for row in reader:
                    straw = {}
                    if len(row) != 0:
                        if str(row[0])[0:2].lower() == 'st':
                            straw['id'] = str(row[0]).lower()
                        if str(row[1][-2]) == 'B':
                            straw['batch'] = str(i)
                        if str(row[2][0:3]).upper() == 'PP.':
                            straw['grade'] = str(i[3]).upper()
                        
                        if len(straw) != 0:
                            cpal_straws.append(straw)
            else:
                pass
                
            cpal_list.append(name)
            straw_information[name] = cpal_straws
                        
            '''        
            print(prefixes)
            
            print(vertical_layout)
            
            print(cpal_straws)
            '''
        except:
            failure_cpals.append(name)
            failure_count += 1
    return failure_cpals, failure_count, cpal_list, straw_information
            

def run():
    failure_cpals, failure_count, cpal_list, straw_information = parse_files()
    print(cpal_list)
    print(straw_information)
    print('length of cpal list: ' + str(len(cpal_list)))
    print('length of straw_information: ' + str(len(straw_information)))
    print('failure count: ' + str(failure_count))
                    
    
if __name__ == "__main__":
    run()