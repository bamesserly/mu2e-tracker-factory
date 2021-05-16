The facileDB is a GUI to help visualize data from the database in a quick and easy way.

The .ui file is essentially the graphics part of the GUI, and is pretty much just a lot of XML.
The facileDB.py file is a pythonic version of the .ui file.
facileDBMain.py is the launcher and back end of the GUI.
panelData.py is a class used by facileDBMain to organize panel data in a consistent and organized way.
The DB_VIEWER batch file launches the gui by excecuting the DB_VIEWER powershell script.

The mu2e.jpg is the mu2e logo, it gets put up in the lefthand corner of the window (opposite side of the "X" button)


List of significant widgets:
Name			Type		Description
panelLE			QLineEdit	User inputs panel id here
submitPB		QPushButton	Updates gui with info for panel number <panelLE.text()>
dataTabs		QTabWidget	All the tabs for each different measurement type (plus panel summary)
commentTabs		QTabWidget	All the tabs for each different process's comments and time events

List of repetitive widgets:
* indicates the presence of another widget with the same name but _2 added to the end, the doppleganger widget does the same
thing but on a different tab in the dataTabs widget.

<data> ∈ [heat, hv, straw, wire]
<data>ListWidget*	QListWidget	List of <data> measurements.  List of statistics (instead of measurements) for heat data.
<data>ExportButton*	QPushButton	Button that exports <data> data to a CSV file when clicked
<data>PlotButton*	QPushButton	Button that plots data on graph in new window when clicked
<data>GraphLayout	QVBoxLayout	Layout that a graph is inserted into if data is present (otherwise it stays blank)

heatProBox*		QComboBox	Controls the current heat process data that's being displayed
hvProBox*		QComboBox	Controls the current hv process/voltage data that's being displayed

<pan> ∈ [pan1, pan2, pan3, pan4, pan5, pan6, pan7]
<pan>ComList		QListWidget	List of comments for the <pro> process
<pan>STimeLE		QLineEdit	Displays start time of the <pan> process
<pan>TTimeLE		QLineEdit	Displays end time of the <pan> process
<pan>ETimeLE		QLineEdit	Displays elapsed time of the <pan> process
<pan>TimeList		QListWidget	List of time events (start, pause, resume, finish) for the <pan> process

partBASEPLATELE		QLineEdit	This and all of the following widgets display the part id for the part in their name
partMIRLE		QLineEdit
partBIRLE		QLineEdit
partPIRLALE		QLineEdit
partPIRLBLE		QLineEdit
partPIRLCLE		QLineEdit
partPIRRALE		QLineEdit
partPIRRBLE		QLineEdit
partPIRRCLE		QLineEdit
partALFLLE		QLineEdit
partALFRLE		QLineEdit
partPAASALE		QLineEdit
partPAASBLE		QLineEdit
partPAASCLE		QLineEdit
partFRAMELE		QLineEdit
partMIDDLERIB_1LE	QLineEdit
partMIDDLERIB_2LE	QLineEdit
partlpal_top_LE		QLineEdit
partlpal_top_LE		QLineEdit