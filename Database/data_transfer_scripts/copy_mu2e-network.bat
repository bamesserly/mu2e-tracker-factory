@ECHO OFF
REM=============================================================================
REM Mergedown -- This script syncs data (not code -- code is synced with git)
REM between network and local lab computers.
REM
REM (1) copy DOWN everything from the network to local UNLESS a file exists in
REM both locations and the network version is older than the local version
REM
REM (2) explicitly copy DOWN of the database from network to local regardless
REM of which is older or newer. See comment after (3).
REM
REM (3) finally, copy UP everything from local to network EXCEPT for the DB.
REM The primary purpose of this command is to (a) send new files up to the
REM network and (b) update files whose local timestamp is newer than its
REM network timestamp.
REM
REM Automerge shalt be the authoritative way to copy DB UP from local to
REM network. Automerge shalt be a separate system that is responsible for
REM itself. No good reason to copy DB wholesale UP to network.
REM
REM Two primary weaknesses: First, if (1) fails, network text and excel files
REM (DB is protected from this) could be overwritten with out-of-date local
REM versions. This is rare and low risk. Second, bad behavior when multiple
REM machines simultaneously edit txt & excel files.
REM=============================================================================

ECHO MERGEDOWN IN PROGRESS.
ECHO DO NOT CLOSE THIS WINDOW.
ECHO WINDOW WILL CLOSE AUTOMATICALLY WHEN MERGEDOWN IS FINISHED.

REM=============================================================================
REM Collect YYYMMDD-HHMMSS int a variable
REM=============================================================================
set CUR_YYYY=%date:~10,4%
set CUR_MM=%date:~4,2%
set CUR_DD=%date:~7,2%
set CUR_HH=%time:~0,2%
if %CUR_HH% lss 10 (set CUR_HH=0%time:~1,1%)
set CUR_NN=%time:~3,2%
set CUR_SS=%time:~6,2%
set CUR_MS=%time:~9,2
set SUBFILENAME=%CUR_YYYY%%CUR_MM%%CUR_DD%-%CUR_HH%%CUR_NN%%CUR_SS% 

REM=============================================================================
REM call the sub command and pass its output to a logfile
REM=============================================================================
call :sub > C:\Users\%USERNAME%\Desktop\MergeDownLogs\mergedown_%SUBFILENAME%.txt
exit /b

REM=============================================================================
REM Define the sub command:
REM=============================================================================
:sub
robocopy \\rds01.storage.umn.edu\cse_spa_mu2e\Data C:\Users\%USERNAME%\Desktop\Production\Data /e /xo /xf *.db ~*
robocopy \\rds01.storage.umn.edu\cse_spa_mu2e\Data C:\Users\%USERNAME%\Desktop\Production\Data *.db /e
robocopy C:\Users\%USERNAME%\Desktop\Production\Data \\rds01.storage.umn.edu\cse_spa_mu2e\Data /e /xf *.db ~*
