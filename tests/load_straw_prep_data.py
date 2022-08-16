from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv
import tests.straw_present_utils as straw_utils
import datetime
import os, time
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath

paths = GetProjectPaths()

def parse_files():
    failure_count = 0
    cpal_list = []
    straw_information = {}
    failure_cpals = []
    pp_grades=['A','B','C','D']
    cpal_prefix_list=[]
    problem_files=['CPAL0002.csv', 'CPAL0040.csv', 'CPAL0025.csv', 'prep_CPAL7653.csv', 'CPAL1234.csv', 'prep_CPAL1234.csv']

    
    # format: time, cpalid, cpal, paper pull time, worker
    straws = []
    
    for file in Path(paths['prepdata']).rglob('*.csv'):
            
        if file.name not in problem_files:
            name=file.name
            f = open(file,'r')
            reader = csv.reader(f)
            
            prefixes={'cpal':name[-8:-4]}
            
            # determine whether the straws have a horizontal or vertical layout in the csv file
            
            vertical_layout=False
            for row in reader:
                try:
                    if len(row[0]) != 0 and str(row[0]) == 'straw':
                        vertical_layout = True
                except:
                    pass
            
            f = open(file,'r')
            reader = csv.reader(f)
            for row in reader:
                # acquire cpal prefix information

                if (len(str(row[0])) == 16 or len(str(row[0])) == 19) and 2015 < int(str(row[0][0:4])) < 2023:
                    for i in row:
                        if len(str(i)) == 16 and 2015 < int(str(i[0:4])) < 2023:
                            time = datetime.datetime.strptime(i, "%Y-%m-%d_%H:%M")
                            time = datetime.datetime.timestamp(time)
                            prefixes['time'] = int(time)
                        if len(str(i)) == 19 and 2015 < int(str(i[0:4])) < 2023 and str(i)[10] == ' ':
                            time = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
                            time = datetime.datetime.timestamp(time)
                            prefixes['time'] = int(time)
                        if len(str(i)) == 19 and 2015 < int(str(i[0:4])) < 2023 and str(i)[10] == '_':
                            time = datetime.datetime.strptime(i, "%Y-%m-%d_%H:%M:%S")
                            time = datetime.datetime.timestamp(time)
                            prefixes['time'] = int(time)
                        if len(str(i)) == 8:
                            if str(i[0:6]).upper() == 'CPALID':
                                prefixes['cpalid'] = int(i[6:8])
                        if len(i) > 5 and str(i[-2]) == 'B':
                            prefixes['batch'] = str(i)
                        if str(i[0:3]).lower() == 'wk-':
                            prefixes['worker'] = str(i)
                    break
            if len(prefixes) > 1:
                cpal_prefix_list.append(prefixes)
            else:
                print('prefix fail:')
                print(name)



                    
            # acquire constituent straw information
            f = open(file,'r')
            reader = csv.reader(f)
            cpal_straws = []
            reached_data = False
            if vertical_layout is True:
                
                for row in reader:
                    if len(row) >= 1:
                        if str(row[0]) == 'straw':
                            reached_data = True
                        
                    if reached_data == True:
                        straw = {}
                        if len(row) >= 3:
                            for i in range(3):
                                if len(row[i]) == 7:
                                    if str(row[i])[0:2].lower() == 'st' and str(row[i][2].isnumeric()):
                                        straw['id'] = str(row[i]).lower()
                                if len(row[i]) > 3 and str(row[i][-2]) == 'B':
                                    straw['batch'] = str(row[i])
                                if len(str(row[i])) == 4 or len(str(row[i])) == 3:
                                    if str(row[i][0:2]).upper() == 'PP' or str(row[i]) == 'DNE':
                                        straw['grade'] = str(row[i]).upper()
                                
                            if len(straw) != 0:
                                straw['time'] = prefixes['time']
                                cpal_straws.append(straw)
                    
                pass
            else:
                
                inner_straw=[]
                inner_batch=[]
                inner_grade=[]
                
                eof=False
                for row in reader:
                    if len(row) != 0:
                        for i in row:
                            if len(i) == 7:
                                if str(i)[0:2].lower() == 'st' and str(i[2].isnumeric()):
                                    inner_straw.append(str(i))
                            if len(i) > 3 and str(i[-2]) == 'B':
                                inner_batch.append(str(i))
                            if len(i) == 4 or len(i) == 3:
                                if str(i[0:3]).upper() == 'PP.' or str(i).upper() == 'DNE':
                                    inner_grade.append(str(i).upper())
                
                if len(inner_straw) == len(inner_batch) or len(inner_straw) == len(inner_grade):
                    for i in range(len(inner_straw)):
                        straw={'id': inner_straw[i].lower()}
                        if len(inner_batch) == len(inner_straw):
                            straw['batch'] = str(inner_batch[i])
                        if len(inner_grade) == len(inner_straw):
                            straw['grade'] = str(inner_grade[i]).upper()
                        
                        cpal_straws.append(straw)
                
                    
                    
                    # use prefix batch information if appropriate
                    if len(inner_batch) != len(inner_straw):
                        for i in cpal_straws:
                            try:
                                i['batch'] = prefixes['batch']
                            except:
                                print(name)
                    
                    # add time to straw
                    for i in cpal_straws:
                        i['time'] = prefixes['time']
                    
                    
                else:
                    print(name)
                    print(len(inner_straw))
                    print(len(inner_batch))
                    print(len(inner_grade))
                
            
                
            
                                
            cpal_list.append(name)
            straw_information[name[-8:-4]] = cpal_straws

                        

    return failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list

def analyze_data():
    failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list = parse_files()
    
    '''
    for i in cpal_prefix_list:
        cpal = i['cpal']
        
        for i in straw_information[cpal]:
            try:
                temp = i['grade']
            except:
                print(cpal)
    '''
        
    

    
    

def update_straw_table(straw_information, cpal_prefix_list):
    database = GetLocalDatabasePath()
    engine = sqla.create_engine("sqlite:///" + database)
    connection = engine.connect()
    
    # add an item to each straw dictionary telling whether or not it's currently present in the db
    for i in cpal_prefix_list:
        cpal = i['cpal']
        for y in range(len(straw_information[cpal])):
            try:
                straw_information[cpal][y]['present_db'] = straw_utils.strawExists(straw_information[cpal][y]['id'][2::], connection)
                '''
                print(straw_utils.strawExists(straw_information[cpal][y]['id'][2::], connection))
                '''
            except:
                print('issue acquiring straw information on cpal ' + str(cpal))
    
    # for all straws not present in straw table, add them
    for i in cpal_prefix_list:
        cpal = i['cpal']
        for y in range(len(straw_information[cpal])):
            if straw_information[cpal][y]['present_db'] == False:
                straw_id = straw_information[cpal][y]['id'][2::]
                batch = straw_information[cpal][y]['batch']
                timestamp = int(straw_information[cpal][y]['time'])
                                   
                straw_utils.createStraw(straw_id, batch, timestamp, connection)
    
        


def save_db():
    failure_cpals, failure_count, cpal_list, straw_information, cpal_prefix_list = parse_files()
    
    
    update_straw_table(straw_information, cpal_prefix_list)
    
            

def run():
    save_db()
    
    
    
                    
    
if __name__ == "__main__":
    run()