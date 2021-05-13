import datetime, csv

def saveWorkers(worker_dir, current_workers, just_log_out):
    previousWorkers = []
    activeWorkers = []
    outfilename = datetime.datetime.now().strftime("%Y-%m-%d") + ".csv"
    outfile = worker_dir / outfilename
    exists = outfile.is_file()
    if exists:
        with open(outfile, "r") as previous:
            today = csv.reader(previous)
            for row in today:
                previousWorkers = []
                for worker in row:
                    previousWorkers.append(worker)

    for i in range(len(current_workers)):
        if current_workers[i].text() != "":
            activeWorkers.append(current_workers[i].text())

    for prev in previousWorkers:
        already = False
        for act in activeWorkers:
            if prev == act:
                already = True
        if not already:
            if prev != just_log_out:
                activeWorkers.append(prev)

    with open(outfile, "a+") as workers_file:
        if exists:
            workers_file.write("\n")
        if len(activeWorkers) == 0:
            workers_file.write(",")
        for i in range(len(activeWorkers)):
            workers_file.write(activeWorkers[i])
            if i != len(activeWorkers) - 1:
                workers_file.write(",")
