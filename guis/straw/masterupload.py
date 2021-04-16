# Ben Hiltbrand - <hiltb004@umn.edu>
# Master upload file to upload all data that failed initial data upload
# Each class corresponds to a mechanism for uploading data for each test

from dataloader import DataLoader, DataQuery
import csv, datetime, os

master_worker = "wk-bhiltbra01"
all_steps = [
    "makestraw",
    "resistance",
    "co2epoxy",
    "leak",
    "measurement",
    "silverepoxy",
]
all_stationids = ["make", "ohms", "C-O2", "leak", "leng", "silv"]


def workerIDError(worker):
    return (
        f'DETAIL:  Key (worker_barcode)=({worker}) is not present in table "workers".'
    )


def strawIDError(straw):
    return f'DETAIL:  Key (straw_barcode)=({straw}) is not present in table "straws".'


class UploadFailedError(Exception):
    # Raised when a straw is not uploaded to the database successfully
    def __init__(self, message):
        super().__init__(self, message)
        self.message = message


class MakeUpload:
    def __init__(self, mode):
        self.table = "straws"
        self.mode = mode
        self.failed_path = (
            os.path.dirname(__file__) + "..\\..\\Data\\Failure Data\\Upload Failure"
        )
        self.data_path = os.path.dirname(__file__) + "..\\..\\Data\\Make Straw Data"

        if self.mode == "dev":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2edev/loader"  # dev url
            self.password = "sdwjmvw"  # dev password

        elif self.mode == "prod":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2e/loader"  # prod url
            self.password = "0cvkwic"  # prod password

        self.queryUrl = "http://ifb-data.fnal.gov:9090/QE/hw/app/SQ/query"
        self.group = "Straw Tables"

    def createRow(self, data):
        return {
            "straw_barcode": str(data[0]),
            "batch_number": str(data[1]),
            "worker_barcode": data[2],
        }

    def beginUpload(self, straw, batch, worker, cpal, source="gui"):
        if source == "gui":
            t = datetime.datetime.now().strftime("%Y-%m-%d")
            path = self.failed_path + "\\" + t + "_" + cpal + "_makestraw_errors.txt"
            errors = open(path, "a+")

        failed = False

        data = [straw, batch, worker]

        dataLoader = DataLoader(self.password, self.url, self.group, self.table)
        dataLoader.addRow(self.createRow(data))
        retVal, code, text = dataLoader.send()

        if not retVal:
            if source == "gui":
                errors.write(str(data[0]) + " FAILED upload\n")
                errors.write(code + "\n")
                errors.write(text.decode("unicode_escape") + "\n\n")

            failed = True

        dataLoader.clearRows()

        if source == "gui":
            errors.close()

            if os.stat(path).st_size == 0:
                os.remove(path)

        if failed:
            raise UploadFailedError(text.decode("unicode_escape"))

    def findDataAndUpload(self, failed_straws, CPAL, worker):
        for file in os.listdir(self.data_path):
            filename = os.fsdecode(file)
            if CPAL in filename:
                path = self.data_path + "\\" + filename
                with open(path, "r") as f:
                    data_file = csv.reader(f)
                    for index, row in enumerate(data_file):
                        if index == 2:
                            straws = row
                        elif index == 3:
                            batches = row

                for index, straw in enumerate(straws):
                    if straw in failed_straws:
                        try:
                            self.beginUpload(
                                straw, batches[index], worker, CPAL, "master"
                            )
                        except UploadFailedError as error:
                            t = datetime.datetime.now().strftime("%Y-%m-%d")
                            original_message = error.message

                            if error.message[125:-1] == workerIDError(worker):
                                try:
                                    self.beginUpload(
                                        straw,
                                        batches[index],
                                        master_worker,
                                        CPAL,
                                        "master",
                                    )
                                except UploadFailedError:
                                    errors = open(
                                        self.failed_path
                                        + "\\"
                                        + t
                                        + "_masterupload_errors.txt",
                                        "a+",
                                    )
                                    errors.write(straw + " FAILED UPLOAD\n")
                                    errors.write(original_message)
                                    errors.write("\n")
                                    errors.close()
                            else:
                                errors = open(
                                    self.failed_path
                                    + "\\"
                                    + t
                                    + "_masterupload_errors.txt",
                                    "a+",
                                )
                                errors.write(straw + " FAILED UPLOAD\n")
                                errors.write(original_message)
                                errors.write("\n")
                                errors.close()
            else:
                continue


class ResistanceUpload:
    def __init__(self, mode):
        table = "straw_resistance_measurements"
        self.mode = mode
        self.failed_path = (
            os.path.dirname(__file__) + "/../../Data/Failure Data/Upload Failure"
        )
        self.data_path = os.path.dirname(__file__) + "/../../Data/Resistance Testing"

        if self.mode == "dev":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2edev/loader"  # dev url
            self.password = "sdwjmvw"  # dev password

        elif self.mode == "prod":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2e/loader"  # prod url
            self.password = "0cvkwic"  # prod password

        self.queryUrl = "http://ifb-data.fnal.gov:9090/QE/hw/app/SQ/query"
        self.group = "Straw Tables"

    def createRow(self, data):
        # print str(data[0])
        return {
            "straw_barcode": str(data[0]),
            "create_time": data[1],
            "worker_barcode": data[2],
            "workstation_barcode": str(data[3]),
            "resistance": data[4],
            "temperature": data[5],
            "humidity": data[6],
            "resistance_measurement_type": str(data[7]),
            "comments": str(data[8]),
        }

    def beginUpload(
        self,
        straw,
        worker,
        temp,
        humidity,
        resistance,
        resistance_type,
        position,
        cpal,
        source="gui",
    ):
        if source == "gui":
            t = datetime.datetime.now()
            create_time = t.strftime("%m-%d-%Y %H:%M:%S")
            tf = t.strftime("%Y-%m-%d")
            path = self.failed_path + "\\" + tf + "_" + cpal + "_resistance_errors.txt"
            errors = open(path, "a+")

        failed = False

        if self.mode == "dev":
            workstation = "wsb0001"  # dev workstation
        elif self.mode == "prod":
            workstation = "ws-umn-ohm{0:02d}".format(position)  # prod workstation

        if resistance_type[0] == "i":
            test_type = "bench inside"
        else:
            test_type = "bench outside"

        resistance = round(resistance, 1)

        create_time = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")

        data = [
            straw,
            create_time,
            worker,
            workstation,
            resistance,
            temp,
            humidity,
            test_type,
            resistance_type,
        ]

        dataLoader = DataLoader(password, url, group, table)
        dataLoader.addRow(self.createRow(data))
        retVal, code, text = dataLoader.send()

        if not retVal:
            if source == "gui":
                errors.write(str(data[0]) + " " + resistance_type + " FAILED upload\n")
                errors.write(code + "\n")
                errors.write(text.decode("unicode_escape") + "\n\n")

            failed = True

        dataLoader.clearRows()

        if source == "gui":
            errors.close()

            if os.stat(path).st_size == 0:
                os.remove(path)

        if failed:
            raise UploadFailedError(text.decode("unicode_escape"))

    def findDataAndUpload(self, failed_straws, CPAL, worker):
        straws = []
        tests = []

        test_dict = {
            "inside-inside": "ii",
            "inside-outside": "io",
            "outside-inside": "oi",
            "outside-outside": "oo",
        }

        for entry in failed_straws:
            straw = entry[0]
            test = entry[1]

            straws.append(straw)
            tests.append(test)

        for file in os.listdir(self.data_path):
            filename = os.fsdecode(file)

            if "Straw_Resistance" not in filename:
                continue

            lower_bound = int(filename.upper()[36:43].strip("ST"))
            upper_bound = int(filename.upper()[44:51].strip("ST"))
            in_range = []

            for straw in straws:
                num = int(straw.strip("ST"))
                in_range.append(num >= lower_bound and num <= upper_bound)

            if any(in_range):
                path = self.data_path + "\\" + filename
                with open(path, "r") as f:
                    data_file = csv.reader(f, skipinitialwhitespace=True)
                    for index, row in enumerate(data_file):
                        if index == 0:
                            continue

                        straw = row[0]

                        try:
                            i = straws.index(straw)
                        except ValueError:
                            continue

                        test_name = row[7]
                        test = test_dict[test_name]

                        if test in tests[i]:
                            resistance = row[4]
                            temp = row[5]
                            humid = row[6]
                            position = int((index - 1) / 4)

                            try:
                                self.beginUpload(
                                    straw,
                                    worker,
                                    temp,
                                    humid,
                                    resistance,
                                    test,
                                    position,
                                    CPAL,
                                    "master",
                                )
                            except UploadFailedError as error:
                                t = datetime.datetime.now().strftime("%Y-%m-%d")
                                original_message = error.message

                                if error.message[125:-1] == workerIDError(worker):
                                    try:
                                        self.beginUpload(
                                            straw,
                                            master_worker,
                                            temp,
                                            humid,
                                            resistance,
                                            test,
                                            position,
                                            CPAL,
                                            "master",
                                        )
                                    except UploadFailedError:
                                        errors = open(
                                            self.failed_path
                                            + "\\"
                                            + t
                                            + "_masterupload_errors.txt",
                                            "a+",
                                        )
                                        errors.write(
                                            straw + " " + test + " FAILED UPLOAD\n"
                                        )
                                        errors.write(original_message)
                                        errors.write("\n")
                                        errors.close()

                                elif error.message[125:-1] == strawIDError(straw):
                                    try:
                                        self.beginUpload(
                                            straw,
                                            worker,
                                            temp,
                                            humid,
                                            resistance,
                                            test,
                                            position,
                                            CPAL,
                                            "master",
                                        )
                                    except UploadFailedError:
                                        if error.message[125:-1] == workerIDError(
                                            worker
                                        ):
                                            try:
                                                self.beginUpload(
                                                    straw,
                                                    master_worker,
                                                    temp,
                                                    humid,
                                                    resistance,
                                                    test,
                                                    position,
                                                    CPAL,
                                                    "master",
                                                )
                                            except UploadFailedError:
                                                errors = open(
                                                    self.failed_path
                                                    + "\\"
                                                    + t
                                                    + "_masterupload_errors.txt",
                                                    "a+",
                                                )
                                                errors.write(
                                                    straw
                                                    + " "
                                                    + test
                                                    + " FAILED UPLOAD\n"
                                                )
                                                errors.write(original_message)
                                                errors.write("\n")
                                                errors.close()
                                        else:
                                            errors = open(
                                                self.failed_path
                                                + "\\"
                                                + t
                                                + "_masterupload_errors.txt",
                                                "a+",
                                            )
                                            errors.write(
                                                straw + " " + test + " FAILED UPLOAD\n"
                                            )
                                            errors.write(original_message)
                                            errors.write("\n")
                                            errors.close()

                                else:
                                    errors = open(
                                        self.failed_path
                                        + "\\"
                                        + t
                                        + "_masterupload_errors.txt",
                                        "a+",
                                    )
                                    errors.write(
                                        straw + " " + test + " FAILED UPLOAD\n"
                                    )
                                    errors.write(original_message)
                                    errors.write("\n")
                                    errors.close()


class CO2Upload:
    def __init__(self, mode):
        self.table = "straw_glueups"
        self.mode = mode
        self.failed_path = (
            "\\\\MU2E-CART1\\Database Backup\\Failure Data\\Upload Failure"
        )
        self.data_path = "\\\\MU2E-CART1\\Database Backup\\CO2 endpiece data"

        if self.mode == "dev":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2edev/loader"  # dev url
            self.password = "sdwjmvw"  # dev password
            self.workstation = "wsb0001"

        elif self.mode == "prod":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2e/loader"  # prod url
            self.password = "0cvkwic"  # prod password
            self.workstation = "ws-umn-CO2Ep0"

        self.queryUrl = "http://ifb-data.fnal.gov:9090/QE/hw/app/SQ/query"
        self.group = "Straw Tables"

    def createRow(self, data):
        return {
            "straw_barcode": str(data[0]),
            "glueup_type": data[1],
            "worker_barcode": data[2],
            "workstation_barcode": data[3],
            "glue_batch_number": data[4],
        }

    def beginUpload(self, straw, worker, epoxy_batch, cpal, source="gui"):
        if source == "gui":
            t = datetime.datetime.now().strftime("%Y-%m-%d")
            path = self.failed_path + "\\" + t + "_" + cpal + "_co2epoxy_errors.txt"
            errors = open(path, "a+")

        failed = False

        data = [straw, "CO2", worker, self.workstation, epoxy_batch]

        dataLoader = DataLoader(self.password, self.url, self.group, self.table)
        dataLoader.addRow(self.createRow(data))
        retVal, code, text = dataLoader.send()

        if not retVal:
            if source == "gui":
                errors.write(str(data[0]) + " FAILED upload\n")
                errors.write(code + "\n")
                errors.write(text.decode("unicode_escape") + "\n\n")

            failed = True

        dataLoader.clearRows()

        if source == "gui":
            errors.close()

            if os.stat(path).st_size == 0:
                os.remove(path)

        if failed:
            raise UploadFailedError(text.decode("unicode_escape"))

    def findDataAndUpload(self, failed_straws, CPAL, worker):
        for file in os.listdir(self.data_path):
            filename = os.fsdecode(file)
            if CPAL in filename:
                path = self.data_path + "\\" + filename
                with open(path, "r") as f:
                    data_file = csv.reader(f)
                    for index, row in enumerate(data_file):
                        if index == 1:
                            batch = row[2]
                            break

                try:
                    self.beginUpload(straw, worker, batch, CPAL, "master")
                except UploadFailedError as error:
                    t = datetime.datetime.now().strftime("%Y-%m-%d")
                    original_message = error.message

                    if error.message[125:-1] == workerIDError(worker):
                        try:
                            self.beginUpload(
                                straw, master_worker, batch, CPAL, "master"
                            )
                        except UploadFailedError:
                            errors = open(
                                self.failed_path
                                + "\\"
                                + t
                                + "_masterupload_errors.txt",
                                "a+",
                            )
                            errors.write(straw + " FAILED UPLOAD\n")
                            errors.write(original_message)
                            errors.write("\n")
                            errors.close()

                    elif error.message[125:-1] == strawIDError(straw):
                        try:
                            self.beginUpload(straw, worker, batch, CPAL, "master")
                        except UploadFailedError:
                            if error.message[125:-1] == workerIDError(worker):
                                try:
                                    self.beginUpload(
                                        straw, master_worker, batch, CPAL, "master"
                                    )
                                except UploadFailedError:
                                    errors = open(
                                        self.failed_path
                                        + "\\"
                                        + t
                                        + "_masterupload_errors.txt",
                                        "a+",
                                    )
                                    errors.write(straw + " FAILED UPLOAD\n")
                                    errors.write(original_message)
                                    errors.write("\n")
                                    errors.close()
                            else:
                                errors = open(
                                    self.failed_path
                                    + "\\"
                                    + t
                                    + "_masterupload_errors.txt",
                                    "a+",
                                )
                                errors.write(straw + " FAILED UPLOAD\n")
                                errors.write(original_message)
                                errors.write("\n")
                                errors.close()

                    else:
                        errors = open(
                            self.failed_path + "\\" + t + "_masterupload_errors.txt",
                            "a+",
                        )
                        errors.write(straw + " FAILED UPLOAD\n")
                        errors.write(original_message)
                        errors.write("\n")
                        errors.close()


class LeakUpload:
    def __init__(self, mode):
        self.table = "straw_leak_tests"
        self.mode = mode
        self.failed_path = (
            "\\\\MU2E-CART1\\Database Backup\\Failure Data\\Upload Failure"
        )
        self.data_path = "\\\\MU2E-CART1\\Database Backup\\Leak test data\\Leak Test Results\\Leak Test Results.csv"

        if self.mode == "dev":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2edev/loader"  # dev url
            self.password = "sdwjmvw"  # dev password

        elif self.mode == "prod":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2e/loader"  # prod url
            self.password = "0cvkwic"  # prod password

        self.queryUrl = "http://ifb-data.fnal.gov:9090/QE/hw/app/SQ/query"
        self.group = "Straw Tables"

    def createRow(self, data):
        # print str(data[0])
        return {
            "straw_barcode": str(data[0]),
            "test_type": str(data[1]),
            "worker_barcode": data[2],
            "workstation_barcode": str(data[3]),
            "leak_rate": round(data[4], 1),
            "comments": str(data[5]),
            "uncertainty": round(data[6], 1),
            "leak_test_timestamp": str(data[7]),
        }

    def beginUpload(
        self,
        straw,
        worker,
        leakrate,
        uncertainty,
        testtime,
        chamber,
        cpal,
        source="gui",
    ):
        if self.mode == "prod":
            self.workstation = "ws-umn-CH{0:02d}".format(chamber)
        elif self.mode == "dev":
            self.workstation = "wsb0001"

        if source == "gui":
            t = datetime.datetime.now().strftime("%Y-%m-%d")
            path = self.failed_path + "\\" + t + "_" + cpal + "_leak_errors.txt"
            errors = open(path, "a+")

        failed = False

        data = [
            straw,
            "co2",
            worker,
            self.workstation,
            leakrate,
            "",
            uncertainty,
            testtime,
        ]

        dataLoader = DataLoader(self.password, self.url, self.group, self.table)
        dataLoader.addRow(self.createRow(data))
        retVal, code, text = dataLoader.send()

        if not retVal:
            if source == "gui":
                errors.write(str(data[0]) + " FAILED upload\n")
                errors.write(code + "\n")
                errors.write(text.decode("unicode_escape") + "\n\n")

            failed = True

        dataLoader.clearRows()

        if source == "gui":
            errors.close()

            if os.stat(path).st_size == 0:
                os.remove(path)

        if failed:
            raise UploadFailedError(text.decode("unicode_escape"))

    def findDataAndUpload(self, failed_straws, CPAL, worker):
        with open(self.data_path, "r") as f:
            data_file = csvreader(f)

            for index, row in enumerate(data_file):
                straw = row[0]

                if straw in failed_straws:
                    test_time = row[1]
                    chamber = row[4]
                    leak_rate = row[5]
                    uncertainty = row[6]

                    try:
                        self.beginUpload(
                            straw,
                            worker,
                            leak_rate,
                            uncertainty,
                            test_time,
                            CPAL,
                            "master",
                        )
                    except UploadFailedError as error:
                        t = datetime.datetime.now().strftime("%Y-%m-%d")
                        original_message = error.message

                        if error.message[125:-1] == workerIDError(worker):
                            try:
                                self.beginUpload(
                                    straw,
                                    master_worker,
                                    leak_rate,
                                    uncertainty,
                                    test_time,
                                    CPAL,
                                    "master",
                                )
                            except UploadFailedError:
                                errors = open(
                                    self.failed_path
                                    + "\\"
                                    + t
                                    + "_masterupload_errors.txt",
                                    "a+",
                                )
                                errors.write(straw + " FAILED UPLOAD\n")
                                errors.write(original_message)
                                errors.write("\n")
                                errors.close()

                        elif error.message[125:-1] == strawIDError(straw):
                            try:
                                self.beginUpload(
                                    straw,
                                    worker,
                                    leak_rate,
                                    uncertainty,
                                    test_time,
                                    CPAL,
                                    "master",
                                )
                            except UploadFailedError:
                                if error.message[125:-1] == workerIDError(worker):
                                    try:
                                        self.beginUpload(
                                            straw,
                                            master_worker,
                                            leak_rate,
                                            uncertainty,
                                            test_time,
                                            CPAL,
                                            "master",
                                        )
                                    except UploadFailedError:
                                        errors = open(
                                            self.failed_path
                                            + "\\"
                                            + t
                                            + "_masterupload_errors.txt",
                                            "a+",
                                        )
                                        errors.write(straw + " FAILED UPLOAD\n")
                                        errors.write(original_message)
                                        errors.write("\n")
                                        errors.close()
                                else:
                                    errors = open(
                                        self.failed_path
                                        + "\\"
                                        + t
                                        + "_masterupload_errors.txt",
                                        "a+",
                                    )
                                    errors.write(straw + " FAILED UPLOAD\n")
                                    errors.write(original_message)
                                    errors.write("\n")
                                    errors.close()

                        else:
                            errors = open(
                                self.failed_path
                                + "\\"
                                + t
                                + "_masterupload_errors.txt",
                                "a+",
                            )
                            errors.write(straw + " FAILED UPLOAD\n")
                            errors.write(original_message)
                            errors.write("\n")
                            errors.close()


class MeasurementUpload:
    def __init__(self, mode):
        self.table = "straw_cut_lengths"
        self.mode = mode
        self.failed_path = (
            "\\\\MU2E-CART1\\Database Backup\\Failure Data\\Upload Failure"
        )
        self.data_path2 = "\\\\MU2E-CART1\\Database Backup\\Measurement Data"

        self.group = "Straw Tables"

        if self.mode == "dev":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2edev/loader"  # dev url
            self.password = "sdwjmvw"  # dev password
            self.workstation = "wsb0001"  # dev workstation

        elif self.mode == "prod":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2e/loader"  # prod url
            self.password = "0cvkwic"  # prod password
            self.workstation = "ws-umn-Lm1"  # prod workstation

    def createRow(self, data):
        return {
            "straw_barcode": str(data[0]),
            "worker_barcode": data[1],
            "workstation_barcode": data[2],
            "nominal_length": str(data[3]),
            "measured_length": data[4],
            "temperature": data[5],
            "humidity": data[6],
            "cut_length_timestamp": str(data[7]),
        }

    def beginUpload(
        self,
        straw,
        worker,
        testtime,
        temp,
        humidity,
        nom_length,
        measured_length,
        cpal,
        source="gui",
    ):
        if source == "gui":
            t = datetime.datetime.now().strftime("%Y-%m-%d")
            path = self.failed_path + "\\" + t + "_" + cpal + "_measurement_errors.txt"
            errors = open(path, "a+")

        failed = False

        data = [
            straw,
            worker,
            self.workstation,
            round(float(nom_length), 2),
            round(float(measured_length), 2),
            temp,
            humidity,
            testtime,
        ]

        dataLoader = DataLoader(self.password, self.url, self.group, self.table)
        dataLoader.addRow(self.createRow(data), "update")
        retVal, code, text = dataLoader.send()

        if not retVal:
            if source == "gui":
                errors.write(str(data[0]) + " FAILED upload\n")
                errors.write(code + "\n")
                errors.write(text.decode("unicode_escape") + "\n\n")

            failed = True

        dataLoader.clearRows()

        if source == "gui":
            errors.close()

            if os.stat(path).st_size == 0:
                os.remove(path)

        if failed:
            raise UploadFailedError(text.decode())

    def findDataAndUpload(self, failed_straws, CPAL, worker):
        for file in os.listdir(self.data_path1):
            filename = os.fsdecode(file)
            if CPAL in filename:
                path = self.data_path1 + "\\" + filename
                with open(path, "r") as f:
                    data_file = csv.reader(f)
                    for index, row in enumerate(data_file):
                        if index == 1:
                            time = row[0]
                            temp = round(float(row[3]), 1)
                            humid = row[4]
                        elif index == 2:
                            straws = row
                        elif index == 3:
                            nom_lengths = row

        for file in os.listdir(self.data_path2):
            filename = os.fsdecode(file)
            if CPAL in filename:
                path = self.data_path2 + "\\" + filename
                with open(path, "r") as f:
                    data_file = csv.reader(f)
                    for index, row in enumerate(data_file):
                        if index == 3:
                            diff = row

        for index, straw in enumerate(straws):
            if straw in failed_straws:
                meas_leng = float(nom_lengths[index]) + float(diff[index]) / 25.4

                try:
                    self.beginUpload(
                        straw,
                        worker,
                        (time + ":00").replace("_", " "),
                        temp,
                        humid,
                        nom_lengths[index],
                        meas_leng,
                        CPAL,
                        "master",
                    )
                except UploadFailedError as error:
                    t = datetime.datetime.now().strftime("%Y-%m-%d")
                    original_message = error.message

                    if error.message[125:-1] == workerIDError(worker):
                        try:
                            self.beginUpload(
                                straw,
                                master_worker,
                                (time + ":00").replace("_", " "),
                                temp,
                                humid,
                                nom_lengths[index],
                                meas_leng,
                                CPAL,
                                "master",
                            )
                        except UploadFailedError:
                            errors = open(
                                self.failed_path
                                + "\\"
                                + t
                                + "_masterupload_errors.txt",
                                "a+",
                            )
                            errors.write(straw + " FAILED UPLOAD\n")
                            errors.write(original_message)
                            errors.write("\n")
                            errors.close()

                    elif error.message[125:-1] == strawIDError(straw):
                        try:
                            self.beginUpload(
                                straw,
                                worker,
                                (time + ":00").replace("_", " "),
                                temp,
                                humid,
                                nom_lengths[index],
                                meas_leng,
                                CPAL,
                                "master",
                            )
                        except UploadFailedError:
                            if error.message[125:-1] == workerIDError(worker):
                                try:
                                    self.beginUpload(
                                        straw, master_worker, batch, CPAL, "master"
                                    )
                                except UploadFailedError:
                                    errors = open(
                                        self.failed_path
                                        + "\\"
                                        + t
                                        + "_masterupload_errors.txt",
                                        "a+",
                                    )
                                    errors.write(straw + " FAILED UPLOAD\n")
                                    errors.write(original_message)
                                    errors.write("\n")
                                    errors.close()
                            else:
                                errors = open(
                                    self.failed_path
                                    + "\\"
                                    + t
                                    + "_masterupload_errors.txt",
                                    "a+",
                                )
                                errors.write(straw + " FAILED UPLOAD\n")
                                errors.write(original_message)
                                errors.write("\n")
                                errors.close()

                    else:
                        errors = open(
                            self.failed_path + "\\" + t + "_masterupload_errors.txt",
                            "a+",
                        )
                        errors.write(straw + " FAILED UPLOAD\n")
                        errors.write(original_message)
                        errors.write("\n")
                        errors.close()
            else:
                continue


class SilverUpload:
    def __init__(self, mode):
        self.table = "straw_glueups"
        self.mode = mode
        self.failed_path = (
            "\\\\MU2E-CART1\\Database Backup\\Failure Data\\Upload Failure"
        )
        self.data_path = "\\\\MU2E-CART1\\Database Backup\\Silver epoxy data"

        if self.mode == "dev":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2edev/loader"  # dev url
            self.password = "sdwjmvw"  # dev password
            self.workstation = "wsb0001"

        elif self.mode == "prod":
            self.url = "https://dbweb6.fnal.gov:8443/hdb/mu2e/loader"  # prod url
            self.password = "0cvkwic"  # prod password
            self.workstation = "ws-umn-SilvEp0"

        self.queryUrl = "http://ifb-data.fnal.gov:9090/QE/hw/app/SQ/query"
        self.group = "Straw Tables"

    def createRow(self, data):
        return {
            "straw_barcode": str(data[0]),
            "glueup_type": data[1],
            "worker_barcode": data[2],
            "workstation_barcode": data[3],
            "glue_batch_number": data[4],
        }

    def beginUpload(self, straw, worker, epoxy_batch, cpal, source="gui"):
        if source == "gui":
            t = datetime.datetime.now().strftime("%Y-%m-%d")
            path = self.failed_path + "\\" + t + "_" + cpal + "_silverepoxy_errors.txt"
            errors = open(path, "a+")

        failed = False

        data = [straw, "termination", worker, workstation, epoxy_batch]

        dataLoader = DataLoader(password, url, group, table)
        dataLoader.addRow(self.createRow(data))
        retVal, code, text = dataLoader.send()

        if not retVal:
            if source == "gui":
                errors.write(str(data[0]) + " FAILED upload\n")
                errors.write(code + "\n")
                errors.write(text.decode("unicode_escape") + "\n\n")

            failed = True

        dataLoader.clearRows()

        if source == "gui":
            errors.close()

            if os.stat(path).st_size == 0:
                os.remove(path)

        if failed:
            raise UploadFailedError(text.decode())

    def findDataAndUpload(self, failed_straws, CPAL, worker):
        for file in os.listdir(self.data_path):
            filename = os.fsdecode(file)
            if CPAL in filename:
                path = self.data_path + "\\" + filename
                with open(path, "r") as f:
                    data_file = csv.reader(f)
                    for index, row in enumerate(data_file):
                        if index == 1:
                            batch = row[2]
                            break

                try:
                    self.beginUpload(straw, worker, batch, CPAL, "master")
                except UploadFailedError as error:
                    t = datetime.datetime.now().strftime("%Y-%m-%d")
                    original_message = error.message

                    if error.message[125:-1] == workerIDError(worker):
                        try:
                            self.beginUpload(
                                straw, master_worker, batch, CPAL, "master"
                            )
                        except UploadFailedError:
                            errors = open(
                                self.failed_path
                                + "\\"
                                + t
                                + "_masterupload_errors.txt",
                                "a+",
                            )
                            errors.write(straw + " FAILED UPLOAD\n")
                            errors.write(original_message)
                            errors.write("\n")
                            errors.close()

                    elif error.message[125:-1] == strawIDError(straw):
                        try:
                            self.beginUpload(straw, worker, batch, CPAL, "master")
                        except UploadFailedError:
                            if error.message[125:-1] == workerIDError(worker):
                                try:
                                    self.beginUpload(
                                        straw, master_worker, batch, CPAL, "master"
                                    )
                                except UploadFailedError:
                                    errors = open(
                                        self.failed_path
                                        + "\\"
                                        + t
                                        + "_masterupload_errors.txt",
                                        "a+",
                                    )
                                    errors.write(straw + " FAILED UPLOAD\n")
                                    errors.write(original_message)
                                    errors.write("\n")
                                    errors.close()
                            else:
                                errors = open(
                                    self.failed_path
                                    + "\\"
                                    + t
                                    + "_masterupload_errors.txt",
                                    "a+",
                                )
                                errors.write(straw + " FAILED UPLOAD\n")
                                errors.write(original_message)
                                errors.write("\n")
                                errors.close()

                    else:
                        errors = open(
                            self.failed_path + "\\" + t + "_masterupload_errors.txt",
                            "a+",
                        )
                        errors.write(straw + " FAILED UPLOAD\n")
                        errors.write(original_message)
                        errors.write("\n")
                        errors.close()


def uploadStep(worker, step, location="prod"):
    steps = {
        "makestraw": MakeUpload,
        "resistance": ResistanceUpload,
        "co2epoxy": CO2Upload,
        "leak": LeakUpload,
        "measurement": MeasurementUpload,
        "silverepoxy": SilverUpload,
    }

    upload = steps[step](location)
    directory = upload.failed_path

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if step in filename:
            CPAL = filename[11:19]
            failed_straws = []
            failed_tests = []

            with open(directory + "\\" + filename, "r") as read:
                line = read.readline()
                count = 0
                while line != "":
                    if count % 6 == 0:
                        straw = line[0:7]

                        if step == "resistance":
                            test = line[8:10]

                            l = [
                                i for i, v in enumerate(failed_straws) if v[0] == straw
                            ]
                            if l == []:
                                failed_straws.append((straw, [test]))
                            else:
                                failed_straws[l[0]][1].append(test)

                        else:
                            if straw not in failed_straws:
                                failed_straws.append(straw)

                    line = read.readline()
                    count += 1

            upload.findDataAndUpload(failed_straws, CPAL, worker)
            os.remove(directory + "\\" + file)
        else:
            continue


def uploadAll(worker, location="prod"):
    for step in all_steps:
        uploadStep(worker, step, location)


def uploadStepGivenStraws(worker, failed_straws, step, location="prod"):
    steps = {
        "makestraw": MakeUpload,
        "resistance": ResistanceUpload,
        "co2epoxy": CO2Upload,
        "leak": LeakUpload,
        "measurement": MeasurementUpload,
        "silverepoxy": SilverUpload,
    }

    CPAL = getCPALFromStraws(failed_straws)

    upload = steps[step](location)
    upload.findDataAndUpload(failed_straws, CPAL, worker)


def uploadAllGivenStraws(worker, straws, location="prod"):
    for step in all_steps:
        uploadStepGivenStraws(worker, straws, step, location)


def uploadStepGivenStrawsAndCPAL(worker, failed_straws, CPAL, step, location="prod"):
    steps = {
        "makestraw": MakeUpload,
        "resistance": ResistanceUpload,
        "co2epoxy": CO2Upload,
        "leak": LeakUpload,
        "measurement": MeasurementUpload,
        "silverepoxy": SilverUpload,
    }

    upload = steps[step](location)
    upload.findDataAndUpload(failed_straws, CPAL, worker)


def uploadAllGivenStrawsAndCPAL(worker, straws, CPAL, location="prod"):
    for step in all_steps:
        uploadStepGivenStrawsAndCPAL(worker, straws, CPAL, step, location)


def getCPALFromStraws(straws, mode="first"):
    path = "\\\\MU2E-CART1\\Database Backup\\Pallets"
    CPAL = dict(zip(straws, [""] * len(straws)))
    straw_copy = straws

    for cpalid in os.listdir(path):
        for cpal in os.listdir(os.path.join(path, cpalid)):
            with open(os.path.join(path, cpalid, cpal)) as file:
                reader = csv.reader(file)

                if mode == "first":
                    for row in reader:
                        for straw in straw_copy:
                            if straw in row:
                                CPAL[straw] = CPAL[:-4]
                                straw_copy.remove(straw)
                                continue
                elif mode == "last":
                    last = list(reader)[-1]

                    for straw in straw_copy:
                        if straw in row:
                            CPAL[straw] = CPAL[:-4]
                            straw_copy.remove(straw)
                            continue
                else:
                    return

    return list(CPAL.values())


def getStrawsFromCPAL(CPAL, mode="first"):
    valid = True

    if len(CPAL) != 8:
        valid = False

    if valid and CPAL[:4].upper() != "CPAL":
        valid = False

    if valid and not CPAL[4:].isdigit():
        valid = False

    if not valid:
        print("Invalid CPAL Number")
        return []
    else:
        path = "\\\\MU2E-CART1\\Database Backup\\Pallets"
        for cpalid in os.listdir(path):
            for cpal in os.listdir(path + "\\" + cpalid):
                if CPAL in cpal:
                    with open(path + "\\" + cpalid + "\\" + cpal, "r") as strawFile:
                        reader = csv.reader(strawFile)
                        row_list = list(reader)

                        if mode == "first":
                            first = row_list[1]
                            straws = list(
                                filter(
                                    lambda x: len(x) == 7
                                    and (x[0] == "s" or x[0] == "S")
                                    and (x[1] == "t" or x[1] == "T")
                                    and x[2:].isdigit(),
                                    first,
                                )
                            )
                        elif mode == "last":
                            last = row_list[-1]
                            straws = list(
                                filter(
                                    lambda x: len(x) == 7
                                    and (x[0] == "s" or x[0] == "S")
                                    and (x[1] == "t" or x[1] == "T")
                                    and x[2:].isdigit(),
                                    last,
                                )
                            )
                        else:
                            return []

                    return straws
        return []


def uploadStepGivenCPAL(worker, CPAL, step, location="prod"):
    steps = {
        "makestraw": MakeUpload,
        "resistance": ResistanceUpload,
        "co2epoxy": CO2Upload,
        "leak": LeakUpload,
        "measurement": MeasurementUpload,
        "silverepoxy": SilverUpload,
    }

    upload = steps[step](location)
    failed_straws = getStrawsFromCPAL(CPAL, "last")

    if failed_straws == []:
        print("Failed to get straws")
        return
    else:
        upload.findDataAndUpload(failed_straws, CPAL, worker)


def uploadAllGivenCPAL(worker, CPAL, location="prod"):
    straws = getStrawsFromCPAL(CPAL)

    if straws == []:
        print("Could not get straws")
        return
    else:
        uploadAllGivenStraws(worker, straws, location)


def getUploader(stationid):
    ids = {
        "make": MakeUpload,
        "ohms": ResistanceUpload,
        "C-O2": CO2Upload,
        "leak": LeakUpload,
        "leng": MeasurementUpload,
        "silv": SilverUpload,
    }

    try:
        uploader = ids[stationid]
        return uploader
    except KeyError:
        print("Invalid station ID, please try again")


# uploadStepGivenCPAL(master_worker, 'CPAL0056', 'measurement', 'prod')
# upload = MakeUpload('prod')
# upload.beginUpload('ST02870', '110717.B2', 'wk-bhiltbra01', 'CPAL0064')
