from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv
import tests.straw_present_utils as straw_utils
import datetime

paths = GetProjectPaths()

def parse_files():
    failure_count = 0
    cpal_list = []
    straw_information = {}
    failure_cpals = []
    pp_grades=['A','B','C','D']
    cpal_prefix_list=[]
    problem_files=['CPAL0002.csv', 'CPAL0025.csv', 'CPAL0040.csv', 'CPAL0040.csv', 'CPAL0413.csv']

    
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
                        time = datetime.datetime.strptime(i, "%Y-%m-%d_%H:%S")
                        time = datetime.datetime.timestamp(time)
                        prefixes['time'] = int(time)
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
                            if str(row[i][-2]) == 'B':
                                straw['batch'] = str(row[i])
                        if len(row[i]) == 4:
                            if str(row[i][0:3]).upper() == 'PP.' or str(i) == 'DNE':
                                straw['grade'] = str(row[i]).upper()
                        
                    if len(straw) != 0:
                        cpal_straws.append(straw)
            
            
            pass
        else:
            '''
            inner_straw=[]
            inner_batch=[]
            inner_grade=[]
            
            eof=False
            for row in reader:
                if len(row) != 0 and eof == False:
                    for i in row:
                        if len(i) == 7:
                            if str(i)[0:2].lower() == 'st' and str(i[2].isnumeric()):
                                inner_straw.append(str(i))
                        if len(i) == 9:
                            if str(i[-2]) == 'B':
                                inner_batch.append(str(i))
                        if len(i) == 4:
                            if str(i[0:3]).upper() == 'PP.' or str(i).upper() == 'DNE':
                                inner_grade.append(str(i).upper())
                                eof=True
            
            if len(inner_straw) == len(inner_batch) or len(inner_straw) == len(inner_grade):
                for i in range(len(inner_straw)):
                    straw={'id': inner_straw[i].lower()}
                    if len(inner_batch) == len(inner_straw):
                        straw['batch'] = str(inner_batch[i])
                    if len(inner_grade) == len(inner_straw):
                        straw['grade'] = str(inner_grade[i]).upper()
                    
                    cpal_straws.append(straw)
                
                    
            else:
                print(name)
            '''
        
                            
        cpal_list.append(name)
        straw_information[name] = cpal_straws

                    

    return failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list

def analyze_data():
    failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list = parse_files()
    
    print('length of cpal list: ' + str(len(cpal_list)))
    print('length of straw_information: ' + str(len(straw_information)))
    print('length of cpal prefix list: ' + str(len(cpal_prefix_list)))
    
    print(cpal_prefix_list)

def save_db():
    failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list = parse_files()
    
    print('     ')
    for i in cpal_list:
        problem=False
        for y in straw_information[i]:
            if len(y) != 3:
                problem=True
        if problem==True:
            print(i)
    
    
    '''
    for i in straw_information:
    # check to see if a straw id exists in the straw table
    val = straw_utils.strawExists()
    '''
    
            

def run():
    save_db()
    
    
    
                    
    
if __name__ == "__main__":
    run()