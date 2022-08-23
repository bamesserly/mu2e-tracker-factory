from pathlib import Path
from guis.common.getresources import GetProjectPaths, pkg_resources
import csv
import tests.straw_present_utils as straw_utils
import datetime
import os, time, sys
import sqlalchemy as sqla
from guis.common.getresources import GetProjectPaths, GetLocalDatabasePath
from guis.common.db_classes.straw import Straw
from guis.common.db_classes.straw_location import StrawLocation, CuttingPallet, Pallet
from guis.common.db_classes.procedure import Procedure, StrawProcedure
from guis.common.db_classes.station import Station
from guis.common.db_classes.procedures_straw import Prep
paths = GetProjectPaths()

def determine_prefix(item):
    return_val = None
    type=''
    if len(item) == 16 and 2015 < int(item[0:4]) < 2023:
        time = datetime.datetime.strptime(item, "%Y-%m-%d_%H:%M")
        time = datetime.datetime.timestamp(time)
        type = 'time'
        return_val = int(time)
    elif len(item) == 19 and 2015 < int(item[0:4]) < 2023 and item[10] == ' ':
        time = datetime.datetime.strptime(item, "%Y-%m-%d %H:%M:%S")
        time = datetime.datetime.timestamp(time)
        return_val = int(time)
        type = 'time'
    elif len(item) == 19 and 2015 < int(item[0:4]) < 2023 and item[10] == '_':
        time = datetime.datetime.strptime(item, "%Y-%m-%d_%H:%M:%S")
        time = datetime.datetime.timestamp(time)
        return_val = int(time)
        type = 'time'
    elif len(item) == 8:
        if item[0:6].upper() == 'CPALID':
            return_val = int(item[6:8])
            type = 'cpalid'
    elif len(item) > 5 and item[-2] == 'B':
        return_val = str(item)
        type = 'batch'
    elif item[0:3].lower() == 'wk-':
        return_val = item
        type = 'worker'
    
    return return_val, type
    
def parse_vertical_straw_row(row, reached_data, prefixes):
    if reached_data == True:
        straw = {}
        if len(row) >= 3:
            for i in range(3):
                if len(row[i]) == 7:
                    if str(row[i])[0:2].lower() == 'st' and str(row[i][2].isnumeric()):
                        straw['id'] = str(row[i]).lower()
                elif len(row[i]) > 3 and str(row[i][-2]) == 'B':
                    straw['batch'] = str(row[i])
                elif len(str(row[i])) == 4 or len(str(row[i])) == 3:
                    if str(row[i][0:2]).upper() == 'PP' or str(row[i]) == 'DNE':
                        straw['grade'] = str(row[i]).upper()

                
            if len(straw.keys()) != 0:
                straw['time'] = prefixes['time']
                return straw

    return False

def parse_horizontal_straw_rows(reader, prefixes):
    inner_straw = []
    inner_batch = []
    inner_grade = []
    cpal_straws = []
    
    eof = False
    
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
                    print('batch prefix assignment failed: ' + name)
        
        # add time to straw
        for i in cpal_straws:
            i['time'] = prefixes['time']
        
        return cpal_straws
        
    else:
        return False

def get_cpal_prefix(problem_files, file):
    prefixes=False
    
    if file.name not in problem_files:
        name=file.name
        f = open(file,'r')
        reader = csv.reader(f)
        
        prefixes={'cpal':name[-8:-4]}
        
        f = open(file,'r')
        reader = csv.reader(f)
        print(file.name)
        for row in reader:
            # acquire cpal prefix information
            if (len(str(row[0])) == 16 or (len(str(row[0])) == 19) and 2015 < int(str(row[0][0:4])) < 2023):
                for i in row:
                    return_val, type = determine_prefix(i)
                    if type != '':
                        prefixes[type] = return_val
                break
    return prefixes


def get_straws(problem_files):
    cpal_list=[]
    straw_information={}
    cpal_prefix_list=[]
    problem_straws=[]
    
    for file in Path(paths['prepdata']).rglob('*.csv'):
        name = file.name
        f = open(file,'r')
        reader = csv.reader(f)
        # determine whether the straws have a horizontal or vertical layout in the csv file
        
        vertical_layout=False
        for row in reader:
            try:
                if len(row[0]) != 0 and str(row[0]) == 'straw':
                    vertical_layout = True
            except:
                pass
                
                
        prefixes = get_cpal_prefix(problem_files, file)
        if prefixes != False:
            cpal_prefix_list.append(prefixes)
                
            # acquire constituent straw information
            f = open(file,'r')
            reader = csv.reader(f)
            reached_data = False
            if vertical_layout is True:
                cpal_straws = []
                for row in reader:
                    if len(row) >= 1:
                        if str(row[0]) == 'straw':
                            reached_data = True
                    straw = parse_vertical_straw_row(row, reached_data, prefixes)
                    if straw is not False and straw['grade'] != 'DNE':
                        cpal_straws.append(straw)
                if len(cpal_straws) == 0:
                    print('Problem acquiring straw data on cpal ' + str(name))

            else:
                cpal_straws = parse_horizontal_straw_rows(reader, prefixes)
                
                if cpal_straws is False:
                    print('Problem acquiring straw data on cpal ' + str(name))
                                
            cpal_list.append(name)
            straw_information[name[-8:-4]] = cpal_straws
    
    return cpal_list, straw_information, cpal_prefix_list
    
def parse_files():
    cpal_list = []
    straw_information = {}
    pp_grades=['A','B','C','D']
    problem_files=['CPAL0002.csv', 'CPAL0040.csv', 'CPAL0025.csv', 'prep_CPAL7653.csv', 'CPAL1234.csv', 'prep_CPAL1234.csv', 'CPAL0010.csv', 'CPAL0056',
    'CPAL3945.csv', 'CPAL6997.csv', 'CPAL0484.csv', 'CPAL9119.csv', 'CPAL0312.csv', 'CPAL9999.csv', 'CPAL1551.csv', 'prep_CPAL0591.csv',
    'prep_CPAL7474.csv', 'prep_CPAL8476.csv', 'CPAL1008.csv', 'prep_CPAL0615.csv', 'CPAL2929.csv', 'prep_CPAL0659.csv',
    'CPAL7326.csv', 'prep_CPAL0666.csv', 'prep_CPAL0668.csv', 'prep_CPAL0669.csv', 'prep_CPAL2081.csv', 'prep_CPAL2082.csv']

    cpal_list, straw_information, cpal_prefix_list = get_straws(problem_files)

    return cpal_list, straw_information, cpal_prefix_list

    
    
def update_straw_table(straw_information, cpal_prefix_list):
    database = GetLocalDatabasePath()
    engine = sqla.create_engine("sqlite:///" + database)
    connection = engine.connect()
    
    # for all straws not present in straw table, add them
    for i in cpal_prefix_list:
        cpal = i['cpal']
        for y in range(len(straw_information[cpal])):
            straw_id = straw_information[cpal][y]['id'][2::].lstrip('0')
            batch = straw_information[cpal][y]['batch']
            timestamp = int(straw_information[cpal][y]['time'])
            
            straw = Straw.Straw(straw_id, batch, timestamp)

    print('done updating straw table')
    
def update_straw_location_table(cpal_prefix_list):
    for i in cpal_prefix_list:
        cpal = i['cpal']
        cpalid = i['cpalid']
        time = i['time']
    
        straw_location = StrawLocation.query().filter(StrawLocation.location_type == 'CPAL').filter(StrawLocation.number == cpal).all()
        if len(straw_location) == 0:
            location = StrawLocation('CPAL',cpal,cpalid,None,False,time)
    
    print('done updating straw location table')
    
def update_measurement_prep_table(cpal_prefix_list, straw_information):
    for i in cpal_prefix_list:
        cpal = i['cpal']
        cpalid = i['cpalid']
        time = i['time']
        
        for y in range(len(straw_information[cpal])):
            straw_id = straw_information[cpal][y]['id'][2::].lstrip('0')
            batch = straw_information[cpal][y]['batch']
            paper_pull = straw_information[cpal][y]['grade']
            timestamp = int(straw_information[cpal][y]['time'])
        
            
            procedure = Procedure.StrawProcedure(2,cpalid,cpal,timestamp)
            
            print('paper pull: ' + str(paper_pull))
            prep_measurement = Prep.StrawPrepMeasurement(procedure, straw_id, paper_pull[-1], 1, timestamp)
            prep_measurement.commit()

            
def update_straw_present_table(cpal_prefix_list, straw_information):
    for i in cpal_prefix_list:
        cpal = i['cpal']
        cpalid = i['cpalid']
        time = i['time']
        
        straw_location = StrawLocation.query().filter(StrawLocation.location_type == 'CPAL').filter(StrawLocation.number == cpal).all()[0]
        
        for y in range(len(straw_information[cpal])):
            straw_id = straw_information[cpal][y]['id'][2::].lstrip('0')
            timestamp = int(straw_information[cpal][y]['time'])
            
            
            straw_location.forceAddStraw(straw_id, y, True, True, timestamp)
        
        
        positions = StrawLocation.queryStrawPositions(straw_location.number).all()
        
        
def save_db():
    cpal_list, straw_information, cpal_prefix_list = parse_files()
    #
    
    update_straw_table(straw_information, cpal_prefix_list)
    
    update_straw_location_table(cpal_prefix_list)
    
    update_measurement_prep_table(cpal_prefix_list, straw_information)
    
    update_straw_present_table(cpal_prefix_list, straw_information)
    
            

def run():
    save_db()
    
    
    
                    
    
if __name__ == "__main__":
    run()