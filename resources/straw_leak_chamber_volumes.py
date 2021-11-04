from sys import exit

CONVERSION_RATE = 0.14

CHAMBER_VOLUME = [
    [594, 607, 595, 605, 595],
    [606, 609, 612, 606, 595],
    [592, 603, 612, 606, 567],
    [585, 575, 610, 615, 587],
    [611, 600, 542, 594, 591],
    [598, 451, 627, 588, 649],
    [544, 600, 534, 594, 612],
    [606, 594, 515, 583, 601],
    [557, 510, 550, 559, 527],
    [567, 544, 572, 561, 578],
]

CHAMBER_VOLUME_ERR = [
    [13, 31, 15, 10, 21],
    [37, 7, 12, 17, 15],
    [15, 12, 7, 4, 2],
    [8, 15, 6, 10, 11],
    [4, 3, 8, 6, 9],
    [31, 11, 25, 20, 16],
    [8, 8, 11, 8, 6],
    [6, 10, 8, 10, 8],
    [6, 8, 6, 9, 6],
    [7, 6, 8, 7, 6],
]


def chamber_from_row_col(row, col):
    return row * 5 + col


def row_col_from_chamber(chamber):
    (row, col) = divmod(chamber, 5)
    return row, col


def get_chamber_info(which_info, *args):
    if len(args) == 1:
        row, col = row_col_from_chamber(args[0])
        return which_info[row][col]
    elif len(args) == 2:
        return which_info[args[0]][args[1]]
    else:
        exit("Chamber info invalid parameters. Either (row, col) or chamber#.")


# pass either chamber number or chamber row,col
def get_chamber_volume(*args):
    return get_chamber_info(CHAMBER_VOLUME, *args)


# pass either chamber number or chamber row,col
def get_chamber_volume_err(*args):
    return get_chamber_info(CHAMBER_VOLUME_ERR, *args)


def calculate_leak_rate(slope, chamber_volume):
    return slope * chamber_volume * (10 ** -6) * 60 * CONVERSION_RATE


def calculate_leak_rate_err(
    leak_rate, slope, slope_err, chamber_volume, chamber_volume_err
):
    return (leak_rate / slope) ** 2 * slope_err ** 2 + (
        leak_rate / chamber_volume ** 2 * chamber_volume_err ** 2
    ) ** 0.5
