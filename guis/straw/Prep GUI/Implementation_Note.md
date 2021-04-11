# Prep GUI Implementation Note (Last Updated: 08/26/20)

>Gaoxiang (Leon): If you can't see code block and organized syntax, which means you might not use a right app to open this markdown file. The easiest way is to view it on github. 

### Enviroment Setup
- Make sure you have `databaseClassesStraw.py` in `/Database` folder
- Make sure the 'straw' table in the database has 'location' colomn. If not, follow the following steps:
    - open `.db` file with SQLiteStudio, go to 'straw' table
    - click 'add colomn'
    - in the pop-up window, type 'location' to colomn name and 'INTEGER' to data type.
    - check 'foreign key', and click 'configure'
    - choose 'straw_location' as foreign table and 'id' as foreign colomn
- Make sure you have `/Data` folder. If not, run python script `setup.py`

### Implementing GUI file (`PrepGUI.py`)

###### Importing and Initializing
1. Import dataprocessor
```python
from dataProcessor import MultipleDataProcessor as DataProcessor
```
2. Add global variables
```python
######## Global variables ##########
# Set each true/false to save the data collected when this gui is run to that platform.
# Note: Both can be true.
SAVE_TO_TXT = True
SAVE_TO_SQL = True

# Indicate which data processor you want to use for data-checking (ex: checkCredentials)
# PRIMARY_DP =   'TXT'
PRIMARY_DP =   'SQL'

##Upload to Fermi Lab database, two modes: 'prod' and 'dev'
upload_mode = 'dev'
```
3. Search for `'prod'` and `'dev'`, change them to `upload_mode`
4. Make sure stationID is correct, such as prep, ohms, etc
e.g:
```python
self.stationID = 'prep'
```
5. Make sure paths of directories are correct for each GUI
e.g:
```python
self.workerDirectory = os.path.dirname(__file__) + '/../../../Data/workers/straw workers/straw prep/'
self.palletDirectory = os.path.dirname(__file__) + '/../../../Data/Pallets/' 
self.prepDirectory = os.path.dirname(__file__) + '/../../../Data/Straw Prep Data/'
self.boardPath = os.path.dirname(__file__) + '/../../../Data/Status Board 464/'
```
6. Initialite dataprocessor
```python
 # Data Processor
        self.DP = DataProcessor(
            gui         =   self,
            save2txt    =   SAVE_TO_TXT,
            save2SQL    =   SAVE_TO_SQL,
            sql_primary =   bool(PRIMARY_DP == 'SQL')
        )
```
---
###### function: Change_worker_ID
1. Change id to upper case before appending to worker list
```python
Current_worker = Current_worker.upper()
```
2. Login check to unlock GUI
```python
if PRIMARY_DP == 'SQL':
    if self.DP.validateWorkerID(Current_worker) == False:
        QMessageBox.question(self, 'WRONG WORKER ID','Did you type in the correct worker ID?', QMessageBox.Retry)
        return
elif PRIMARY_DP == 'TXT':
    if self.DP.checkCredentials() == False:
        QMessageBox.question(self, 'WRONG WORKER ID','Did you type in the correct worker ID?', QMessageBox.Retry)
        return
```
3. Save Login info to database
```python
self.DP.saveLogin(Current_worker)
```
4. Save Logout info to database (make sure worker IDs are upper case)
```python
self.justLogOut = self.Current_workers[portalNum].text().upper()
self.sessionWorkers.remove(self.Current_workers[portalNum].text().upper())
self.DP.saveLogout(self.Current_workers[portalNum].text().upper())
```
5. Change `self.saveworkers()` to `self.DP.saveWorkers()`
- This needs to be implemented in `dataProcessor.py` for both saving to local csv files and database. I didn't implement this part, but you can use the code in PrepGUI's `dataProcessor.py` in other GUIs. I think this portion of code is appliable to other GUIs. For txtProcessor implementation, you need to change the worker directory. For sqlProcessor implementation, you can just copy paste. 

###### function: saveData
1. Move the original code to `dataProcessor.py` under txtProcessor implementation of `saveData()`
2. Call `dp.saveData()` within this function and have some exception caught and print statement to indicate the success of saving. If succeessful, change UI elements (enable some buttons, disable some buttons). Also, PrepGUI has a global variable as a flag to indicate whether data is saved or not. 
3. Save comment to database, close handle of database, and reset GUI.
e.g:
```python
self.DP.saveComment(self.ui.commentBox.document().toPlainText())
self.DP.handleClose()
self.resetGUI()
```
4. I don't know about the upload function here. It was used to upload data to fermilab. This part it's better to check with current GUI team lead. 

###### function: resetGUI
1. copy paste the initialization of GUI class (SQL version)

###### function: closeEvent
1. make sure database handle is closed
```python
self.DP.handleClose()
```

###### Timing related: this is special for PrepGUI, implemented by Himanshu

1. Under `def __init__(self, webapp=None, parent=None):`
```python
#Timing info
self.timing = False
self.startTime = None
```

2. Under `def startTiming(self):`
```python
##Begin timing
self.startTime = time.time()
self.DP.saveStart()
self.timing = True
```
This happens when you hit the start button, how a program start may vary by different GUIs

3. Under `def timeUp(self):`
```python
self.timing = False # Stop timing
self.DP.saveFinish()
```
4. Under `def main(self):`
```python
if self.timing:
    if self.startTime == None:
        self.startTime = time.time()

    # Update time display
    self.running = time.time() - self.startTime
    self.ui.hour_disp.display(int(self.running/3600))
    self.ui.min_disp.display(int(self.running/60)%60)
     self.ui.sec_disp.display(int(self.running)%60)
```
5. Add a new function
```python
def getElapsedTime(self):
        return self.running
```

### Implementing  `dataProcessor.py`

###### class: `Class MultipleDataProcessor(DataProcessor):`
1. This class will call which method should be done by which processor.
2. One function should be implemented by both processors, which is `def saveData(self):`.
3. `saveWorkers` should be implemented for txtProcessor only, because sqlProcessor uses `saveLogin` and `saveLogout` for worker info.
4. `saveLogin`, `saveLogout`,`handleClose` should be implemented by sql processor
5. `saveComment` can be implemented for both, but PrepGUI save comment with `saveData` to local csv file, so `saveComment` only be used in sqlProcessor in prepGUI.
6. `validateWorkerID` successully check existing workerID from database, `checkCredentials` succesully check each worker's particular authorization from local csv files. In the future, this two function might need to merge together somehow, or further implemented. 
7. The other function signitures here I don't know about their functions. They might be redundant. 

###### saveData implementation for txtProcessor
1. copy paste the saveData function from old GUI file

###### saveData implementation for sqlProcessor
1. Majority of time will be spent here. If you know object-relational mapping (orm), that's great! If you don't, how you save to database is basically contructing a python class object and call commit() from sqlAlchemy.
2. The object class for the table you need to save to, you can find it on `databaseClassesStraw`. And you need to gather information that needed to construct this class from GUI class (inheritance). 

###### saveWorkers implementation for txtProcessor
1. You can copy paste the code from PrepGUI's `dataProcessor.py` under this function, and remember to change worker directory. This implementation is applicable to other GUIs.

>Gaoxiang (Leon): I will be busy next semester, so I don't have time to continue working on these GUIs. Therefore, I left this note. 

#### Resistance GUI (ohms) and CO2 Endpiece GUI (C-O2)
##### I've also implemented these two GUIs but has no time to test them. You can find them in lab computer #8 ```C:\Users\Mu2e\Documents\Leon's Code\```