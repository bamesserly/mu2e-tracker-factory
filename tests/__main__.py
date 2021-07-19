import tests.load_heat_csv_into_db as loader
from sys import argv


if __name__ == "__main__":
    loader.run(argv[1], argv[2])
