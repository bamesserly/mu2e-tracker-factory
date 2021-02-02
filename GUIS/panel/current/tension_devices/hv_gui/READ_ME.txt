HOW TO USE hvGUI:

First thing after opening it, enter the panel (MN***) you want to work on, the side you'll be
working on, and the voltage you'll be using.
Then hit "Start Session".

Now a bunch of numbers, lines, and checkboxes should appear in the right side of the gui.
None of them are editable (for now).  They just display previous measurements.

In the bottom left you'll see Straw, Current, and Trip Status.
Straw shows which straw you're entering data for.  You can change it with the arrows next to the
number, or type in a number.
Current is where you enter the current you measured.  If you type in a number then hit enter, it'll
be submitted and you'll move to the next straw.
Trip status is where you can indicate if the straw/wire is tripped (I don't know terminology well).
Hitting "Submit Straw" will submit the present data and move you to the next straw.

The gui saves whenever enter is pressed while the current entry box is selected and whenever
the "Submit Straw" button is pushed.

The save location is production/Data/Panel data/hv_data/csvName.csv, where csvName is:
	<panel id>_hv_data_<voltage used>_<date in mmddyyyy format>
So panel 555 at 1100V on June 9th, 1969 would be:
	MN555_hv_data_1100V_06091969