# This script takes a log file produced by run_test.py and produces a .csv file
# that is more human-readable and suitable for plotting.

import sys, numpy, uncertainties

calibration_resistor = uncertainties.ufloat(149.8, 0.3)


def parse_log(infilename):
    outfilename = infilename.replace(".log", ".csv")

    # Open the files.
    infile = open(infilename, "r")
    outfile = open(outfilename, "w")

    # Loop over all the lines in the input file.
    for line in infile:
        # Copy comment lines directly into the output file.
        # Modify the header – don't write ADCs, do write err on resistance.
        if line.startswith("#"):
            if line == "# Position, wire/straw, ADC values..., resistance, PASS?":
                line = "# Position, wire/straw, resistance, err, PASS?"
            outfile.write(line)
            continue

        # Now tokenize the line, and skip blank ones.
        tokens = line.split(",")
        if len(tokens) == 0:
            continue

        # Position, wire/straw, ADC values..., resistance, PASS?
        position = int(tokens[0])
        wirestraw = int(tokens[1])
        data = sorted(map(int, tokens[2:-2]))
        arduinoresistance = float(tokens[-2])
        passfail = tokens[-1]

        # Reproduce the filtered mean from run_test, but this time for saving to a
        # data file instead of for printing to the user.
        if sum(data) > 0:
            filtered_data = [d for d in data if d != 0]
            n_items = len(filtered_data)

            filtered_mean = sum(filtered_data) / float(n_items)
            filtered_sigma = numpy.std(filtered_data)
            filtered = uncertainties.ufloat(filtered_mean, filtered_sigma)
        else:
            filtered = uncertainties.ufloat(0, 0)
            n_items = float("nan")

        # Convert average ADC value to resistance, accounting for divide-by-zero.
        try:
            resistance = calibration_resistor * (1023 / filtered - 1)
        except ZeroDivisionError:
            resistance = uncertainties.ufloat(float("inf"), float("inf"))

        # Write the line to the file.
        outfile.write(
            "%d,%d,%g,%g,%g\n"
            % (
                position,
                wirestraw,
                resistance.nominal_value,
                resistance.std_dev,
                n_items,
            )
        )

    infile.close()
    outfile.close()
    return outfilename


if __name__ == "__main__":
    logfilename = sys.argv[1]
    print("Parsing", logfilename)
    sys.stdout.flush()
    parse_log(logfilename)
    print("done.")
    sys.stdout.flush()
