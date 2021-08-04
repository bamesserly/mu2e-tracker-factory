# mu2e-tracker-factory
Software for the Mu2e tracker straw and panel production at the University of Minnesota.

## Repository Tour
The bulk of the software consists of several [QtPy](https://pypi.org/project/PyQt5/)-frontend, python-backend GUI's that collect user-inputted data and save it to an SQLite database.

In the `guis/` directory, there are guis for `straw/` and `panel/` production, as well as a powerful database viewer (`dbviewer/`) and a deprecated gui showing the production status in the lab (`labstatus/`).

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
1. LPAL loading
2. Prep
3. CO2
4. Resistance
5. Leak
6. Laser cutting/consolidation
7. Silver Epoxy
8. Verification.

![Straw Leak Test GUI](https://lh3.googleusercontent.com/pw/ACtC-3f8m36fC1DfN-UWOw9ltjvEOuHi-kFzVmMrdKiPKNziI5tEE3SOtMAL6skouxgd8wTv9vRQ4ad0YhdaQBsV794E0pLGhiaVVNpeWquA18BtkNoRRHn4uuQvtQGnYrQf5EWgTFl9sol2yZnPmHtaqjaa=w929-h573-no)

## Data Flow
Data collected by the guis is recorded simultaneously in text/csv files as well as a single SQLite database, both located in a `data/` directory.

In the guis, data flows like this:
`pangui` --> `common/dataProcessor` --> `common/databaseClasses` --> `common/databaseManager`

pangui save methods call both `dataProcessor::TxtDataProcessor` and `dataProcessor:SQLDataProcessor` methods. `TxtDataProcessor` methods are self-sufficient, while `SQLDataProcessor` methods rely on `databaseClasses` and `databaseManager` to interface with the database table-by-table and generically, respectively.

Among the text data, straw data is mostly available in the `data/` top directory, while panel data is mostly available in `data/Panel\ Data/`.

No straw data is currently collected in the database. Straw data is only collected in text files.

## Networking at UMN
_The_ authoritative `data/` directory lives on a UMN network. Approximately 20 computers in the lab have, on their `~/Desktop`, a clone of this repository and a proximate duplicate of the `data` directory. During a normal workday, most of these computers have pangui running all day. Data collected on each lab machine is recorded into its local `data/` folder --- into text files and into its database.

#### Database data upload --- AutoMerge
While pangui is running, a join command will automatically be run every 10 minutes (and triggered by critical actions, like shutdown), uploading new database lines to the network, and updating pre-existing lines (provided _t_local_ > _t_network_). This process is called `AutoMerge`. It is a one-way upload. No data is passed from the network to the local database. Text data is not affected whatsoever.

#### Database download and text upload --- Mergedown
`Mergedown` refers to a separate executable which first downloads the entire `data` directory (except for the database) from the network, skipping file overwrites when _t_local_ > _t_network_. Second, it downloads the network database to local, regardless of timestamp. Third and finally, it uploads from local to network the `data` directory (except for the database).
