from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv

paths = GetProjectPaths()

def parse_files():
    failure_count = 0
    cpal_list = []
    straw_information = {}
    failure_cpals = []
    pp_grades=['A','B','C','D']
    cpal_prefix_list=[]

    
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
        
        f = open(file,'r')
        reader = csv.reader(f)
        for row in reader:
            # acquire cpal prefix information

            if len(str(row[0])) == 16 and 2015 < int(str(row[0][0:4])) < 2023:
                for i in row:
                    if len(str(i)) == 16 and 2015 < int(str(i[0:4])) < 2023:
                        prefixes['time'] = str(i)
                    elif len(str(i)) == 8:
                        if str(i[0:7]).upper() == 'CPALID':
                            prefixes['cpalid'] = int(i[7:9])
                    elif len(str(i)) == 4:
                        if str(i[-2]) in pp_grades:
                            prefixes['batch'] = str(i)
                    elif str(i[0:3]).lower() == 'wk-':
                        prefixes['worker'] = str(i)
                break
        if len(prefixes) > 1:
            cpal_prefix_list.append(prefixes)
        else:
            print(name)


                
        # acquire constituent straw information
        f = open(file,'r')
        reader = csv.reader(f)
        cpal_straws = []
        if vertical_layout is True:
            for row in reader:
                straw = {}
                if len(row) >= 3:
                    for i in range(3):
                        if len(row[i]) == 7:
                            if str(row[i])[0:2].lower() == 'st' and str(row[i][2].isnumeric()):
                                straw['id'] = str(row[i]).lower()
                        if len(row[i]) == 9:
                            if str(row[i][-2]) in pp_grades:
                                straw['batch'] = str(i)
                        if len(row[i]) == 4:
                            if str(row[i][0:3]).upper() == 'PP.':
                                straw['grade'] = str(row[i]).upper()
                        
                    if len(straw) != 0:
                        cpal_straws.append(straw)
        else:
            pass
            
        cpal_list.append(name)
        straw_information[name] = cpal_straws
                    

    return failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list
            

def run():
    failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list = parse_files()
    
    '''
    print(cpal_list)
    print(straw_information)
    print(cpal_prefix_list)
    '''
    
    
    print('length of cpal list: ' + str(len(cpal_list)))
    print('length of straw_information: ' + str(len(straw_information)))
    print('failure count: ' + str(failure_count))
    print('length of cpal prefixes: ' + str(len(cpal_prefix_list)))
    
                    
    
if __name__ == "__main__":
    run()