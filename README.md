# mu2e-tracker-factory
Software for the Mu2e tracker straw and panel production at the University of Minnesota.

Several [PyQt](https://pypi.org/project/PyQt5/) "guis"/apps that guide users through straw processing and panel construction, and record data into and visualize data from a SQLite database (and redundantly to csv files).

Credit is owed to many unknown authors who contributed to an original codebase before it moved to github.

## Repository Tour
`guis/` contains mostly frontend code for `straw/`, `panel/`, `dbviewer/`, and `labstatus/` (deprecated) apps.

`guis/common/` folder holds process-specific data structure, app utilities, and database interface.

`resources/` holds installation-related constants like directory structure and database locations.

`setup.py` + `requirements.txt` setup script and pip requirements file.

## Requirements and Installation
Designed originally for Windows, but apps do work on linux and macOS using venv and the `requirements.txt`. That said, without access to the database and `data/` folder, the apps are not very useful.

## GUIs

#### pangui --- The repository's flagship product
`guis/panel/pangui/pangui.py` is a complete lab assistant for the seven _Processes_ of panel production.
* data collection --- session timers and worker IDs, part numbers, QC measurements, timestamps, comments, failures, and much more.
* step-by-step construction instructions including technical figures.
* launch external GUIs for specialized measurements.

![PANGUI --- Process 2](https://lh3.googleusercontent.com/pw/ACtC-3dTsZzlUhGG73GoMuhmO_F1-dhdr_xuTXSrebmTvAri-6kb0N0xEKXoLBnxo1BI7YfCCdfIPp2Q0rvZs5d2Lkqlj3LW2Jvifqnj0dHlhmNEZL4lJXutQLQqerHxfon5kVocMx3M8OMT5PCzBJ9RStkw=w1902-h975-no)

#### Specialized Panel Measurement GUIs
* `heater/` --- control the PAAS-heating arduino box, visualize data. Used in processes 1, 2, and 6.
* `hv/` --- form for recording current measurements. Used in processes 3 and 6
* `leak/` --- script for plotting panel leak data, which is collected by a separate LabView program. Used in process 8.
* `resistance/` --- control the straw-by-straw and wire-by-wire arduino box that measures resistance. Scripts for manipulating and visualizing data. Used in processes 3 and 8.
* `strawtensioner/` --- control the straw tensioning arduino box, visualize data. Used in process 2.
* `tensionbox/` --- control the arduino box that measures straw and wire tensions, visualize data. Used in processes 3, and 6.
* `wiretensioner/` --- control the wire tensioning arduino box, visualize data. Used in process 3.

#### DBViewer
Awesome product from (@adamarnett) to organize, visualize and download panel data from the DB in read-only mode. Now available for use on the mu2e fnal gpvms. Contact @bamesserly for usage details.

![DBViewer --- easily read, export, and plot panel data.](https://lh3.googleusercontent.com/pw/ACtC-3dpX3crEhW0Fj-Wstl5ZRSHnmbbrZCPf9DtSaYjKuClsf1GaOAo55U1uCa0b8IWEmjhD4tl0vyAoOVvvnj9VcQFFDGZJ2KA5BCrjmB-nhJO3YnjbTRvReLGsJpaE2hlAHchn3rsnYWoN2mnF7rvS10o=w1595-h882-no)

#### Straw GUIs
1. Prep -- straws and cutting pallets first recorded. Paper removed from straws.
2. CO2
3. Resistance
4. Leak
5. Laser cutting/consolidation
6. Silver Epoxy (deprecated)
7. Verification (deprecated)
8. LPAL loading

![Straw Leak Test GUI](https://lh3.googleusercontent.com/pw/ACtC-3f8m36fC1DfN-UWOw9ltjvEOuHi-kFzVmMrdKiPKNziI5tEE3SOtMAL6skouxgd8wTv9vRQ4ad0YhdaQBsV794E0pLGhiaVVNpeWquA18BtkNoRRHn4uuQvtQGnYrQf5EWgTFl9sol2yZnPmHtaqjaa=w929-h573-no)

## Data Flow
Data collected by the guis is recorded simultaneously in csv files as well as a single SQLite database, both located in a `data/` directory.

For the most part data flows from user-input to database + csv files like this:
`gui` --> `common/dataProcessor::sqlDataProcessor` --> `common/db_classes/*` --> `common/databaseManager` --> `database`
      --> `common/dataProcessor::txtDataProcessor` --> `csv files`

In `databaseClasses`, each database table is (approximately) represented by a class that inherits from [sqlalchemy](https://www.sqlalchemy.org/)'s [`declarative_base`](https://docs.sqlalchemy.org/en/14/orm/mapping_styles.html#orm-declarative-mapping).

`databaseManager` has generic tools that connect databaseClasses with the database itself -- performing reads, writes, joins, etc.

While all panel construction data is collected into csv files and the database, only straw prep data is collected into the database, while the rest of the straw data is recorded only in text files. Adding the rest of the straw processing data is undergoing active development.

Among the text data, straw data is mostly available in the `data/` top directory, while panel data is mostly available in `data/Panel\ Data/`.

## Networking at UMN
_The_ authoritative `data/` directory lives on a UMN network. Approximately 20 computers in the lab have, on their `~/Desktop`, a clone of this repository and a proximate duplicate of the `data/` directory. During a normal workday, most of these computers have pangui running all day. Data collected on each lab machine is recorded into its local `data/` folder --- into text files and into its database.

#### Database data upload --- AutoMerge
While pangui is running, a join command will automatically be run every 10 minutes (as well as after critical actions, like shutdown), uploading new database lines to the network, and updating pre-existing lines (provided _t_local_ > _t_network_). This process is called `AutoMerge`. It is a one-way upload. No data is passed from the network to the local database. Text data is not affected whatsoever by AutoMerge. Automerging runs on a separate thread from the guis and it is located in `guis/common/merger.py`.

#### Database download and text upload --- Mergedown
`Mergedown` refers to a separate executable program which first downloads the entire `data` directory (except for the database) from the network, skipping file overwrites when _t_local_ > _t_network_. Next, it downloads the network database to local, regardless of timestamp. And finally, it uploads from local to network the `data` directory (except for the database). There are a few different versions for this script -- for different lab rooms different types of data need not be accessed.

## Database Design, Terminology
* **Process** -- refers to a macro-step in straw processing or panel production. There are about 8 straw processes and 8 panel processes. An example of a panel process is "process 1 -- inner ring construction".
* **Stage** -- refers to whether a process is a "straw" or a "panel" process. Originally there was going to be a third stage -- QC -- but that hasn't been used.
* **Station** -- a station is what we now call a _process_ combined with a literal room in the PAN building. Indeed, in the database, _station_ is used in place of _process_, but in common practice/speak, a _station_ no longer a coherent idea. The term was invented and baked into the database back when we though certain processes would always be performed in certain rooms, in certain spots on the floor. Covid, as well as misc SOP changes, means that no longer applies. The idea of a room, in the database, is just basically no-longer useful, so _station_ is a stand-in for _process_.
* **Straw Location** -- a location where a straw may be located. Examples of straw locations are panel MN143, cutting pallet 91, loading pallet 2345, or storage.
* **Straw Position** -- a specific location within a straw location, for example panel MN143, position 83 or cutting pallet position 21.
* **Procedure** -- a procedure is defined by a (_straw location_, _process_) pair. Examples of procedures are (MN143, process 4) or (CPAL2345, straw leak test).
* **Session** -- a session is a chunk of time when a user is logged-in to a gui and working on a certain procedure. Sessions precede procedure's and they start/load procedures.
* **Straw Present** -- a simple boolean saying whether a specific straw is in fact in a straw position or not.



