#made by Sam Penders (pende061@umn.edu) using existing Mu2e database programs
import csv
import os
import time
from DataLoader import DataLoader, DataQuery
from time import strftime
from datetime import datetime

# development database urls
"""
url = "https://dbweb5.fnal.gov:8443/hdb/mu2edev/loader"  #these are the same for all staw tables
queryUrl = "http://ifb-data.fnal.gov:9090/QE/hw/app/SQ/query"
password = "sdwjmvw"
"""

#production database urls
url = "https://dbweb6.fnal.gov:8443/hdb/mu2e/loader"
queryUrl ="http://ifb-data.fnal.gov:9090/QE/hw/app/SQ/query" 
password = "0cvkwic"

group = "Straw Tables"

def createLengthRow(row): # take row of data (in list) as argument
    return{'straw_barcode': str(row[0]),
    'worker_barcode' : str(row[1]),
    'workstation_barcode' : str(row[2]),
    'nominal_length' : row[3],
    'measured_length': row[4],
    'temperature' : str(row[5]),
    'humidity' : str(row[6]),
    'comments' : str(row[7]),
    'cut_length_timestamp' : str(row[8]), #Website gets real time somehow.
    }

def uploadLengths(data): # take list of data as argument    
    table = "straw_cut_lengths"
    dataLoader = DataLoader(password,url,group,table)
    dataLoader.addRow(createLengthRow(data))
    retVal,code,text =  dataLoader.send()
    if retVal:
        print "upload " + data[0] + " length successful!\n"
        print text
    else:
        print text
        
        dataLoader.clearRows()
        dataLoader.addRow(createLengthRow(data),'update')
        newRetval,code,text =  dataLoader.send()
        if newRetval:
            print "update " + data[0] + " length successful!\n"
            #print code
            print text
        else:
            print "update " + data[0] + " length failed!\n"
            #print code
            print text              
    dataLoader.clearRows()

# takes datafile in format of files in //MU2E-CART1/Database Backup/Laser cut data/ as input
def upload_data(savefile):  
    with open(savefile) as csvfile:
        filereader = csv.reader(csvfile,delimiter = ',')
        next(filereader)
        row = next(filereader)
        time = row[0]
        time = time[0:10]+' '+time[11:16]+':00'
        T = row[3]
        H = row[4]
        worker = row[5]
        straws = next(filereader)
        nominal_len = next(filereader)
        stn = 'ws-umn-Laser1' # real one
        #stn = 'wsb0001' # temp


        # worker = 'wk-spenders01' # delete for real database
        for straw, length in zip(straws,nominal_len):         
            # 0.0 for measured length until we start measuring
            data = [straw,worker,stn,round(float(length),2),0.0,T,H,'',time]
            uploadLengths(data)
            
            # try to upload with opposite format for name (i.e. stxxxxx -> STxxxxx)
            num = straw[2:]
            start = straw[0:2]
            new_start = 'ST'
            if start == 'ST':
                new_start = 'st'
            second_name = new_start  + num            
            second_data = [second_name,worker,stn,round(float(length),2),0.0,T,H,'inch; unmeasured',time]
            uploadLengths(second_data)

def upload_all():
    path = '//MU2E-CART1/Database Backup/Laser cut data/'
    for file in os.listdir(path):
        if file != 'CPAL0000.csv' and file != 'CPAL9999.csv':
            print('\n\n\n\n\n' + file)
            upload_data(path+file)

def main():
    # get most recent cut data to upload
    f = open('to_upload.txt','r')
    file = f.read()
    f.close()
    upload_data(file)

main()







































            
