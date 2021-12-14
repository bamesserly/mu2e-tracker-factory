import guis.panel.leak.load_leak_csv_into_db as load, os, shutil
from pathlib import Path

    # function to copy files to problem_files folder
def copy_file(filename, filepath):
    rootdir = "data/Panel data/FinalQC/Leak/RawData/"
    copy_path = "guis/panel/leak/problem_files/"
    original = filepath
    target = copy_path + filename
    print(target)
    shutil.copyfile(original, target)



if __name__ == "__main__":
    rootdir = "data/Panel data/FinalQC/Leak/RawData/"
    
    # iterate through files in directory and subdirectories, attempting to save them to the DATABASE
    # otherwise, copy them to the problem_files folder
    for root, dirs, files in os.walk(rootdir):
        for filename in files:
            try:
                filepath = Path(os.path.join(root, filename)).absolute()
                load.main(filepath)
            except:
                copy_file(filename, filepath)