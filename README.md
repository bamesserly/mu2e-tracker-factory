# mu2e-tracker-factory
Software for the Mu2e tracker panel production at the University of Minnesota.

## Repository Tour
The bulk of the software consists of several [QtPy](https://pypi.org/project/PyQt5/)-frontend, python-backend GUI's that collect user-inputted data and save it to an SQLite database.

The various GUIs live in their respective subfolders of the `GUIS/` directory.

### PANGUI --- The repository's flagship product
 `GUIS/panel/current/PANGUI.py` runs constantly during panel construction as a complete lab and logbook assistant, guiding the users through each of 7 panel production _Processes_:
* Records lots of data: worker IDs, material/part serial numbers, timers, important production QC measurements, observations and failures, timestamps for everything, etc.
* Provides step-by-step instructions --- including instructional technical figures --- for each process.
* Launches specialized GUIs for measuring tensions, currents, and temperatures.

![PANGUI --- Process 2](https://lh3.googleusercontent.com/pw/ACtC-3dTsZzlUhGG73GoMuhmO_F1-dhdr_xuTXSrebmTvAri-6kb0N0xEKXoLBnxo1BI7YfCCdfIPp2Q0rvZs5d2Lkqlj3LW2Jvifqnj0dHlhmNEZL4lJXutQLQqerHxfon5kVocMx3M8OMT5PCzBJ9RStkw=w1902-h975-no)

### DBViewer
Awesome product from (@adamarnett) to organize, visualize and download panel data from the DB in read-only mode.

![DBViewer --- easily read, export, and plot panel data.](https://lh3.googleusercontent.com/pw/ACtC-3dpX3crEhW0Fj-Wstl5ZRSHnmbbrZCPf9DtSaYjKuClsf1GaOAo55U1uCa0b8IWEmjhD4tl0vyAoOVvvnj9VcQFFDGZJ2KA5BCrjmB-nhJO3YnjbTRvReLGsJpaE2hlAHchn3rsnYWoN2mnF7rvS10o=w1595-h882-no)

### Straw GUIS
Various GUIs that assist in straw processing and associated data collection. One GUI for (1) LPAL loading, (2) Prep, (3) CO2, (4) Resistance, (5) Leak, (6) Laser Cutting, (7) Silver Epoxy, and (8) Verification.

![Straw Leak Test GUI](https://lh3.googleusercontent.com/pw/ACtC-3f8m36fC1DfN-UWOw9ltjvEOuHi-kFzVmMrdKiPKNziI5tEE3SOtMAL6skouxgd8wTv9vRQ4ad0YhdaQBsV794E0pLGhiaVVNpeWquA18BtkNoRRHn4uuQvtQGnYrQf5EWgTFl9sol2yZnPmHtaqjaa=w929-h573-no)

### LabViewer

## History of Tracker Production Software

## Data Flow
