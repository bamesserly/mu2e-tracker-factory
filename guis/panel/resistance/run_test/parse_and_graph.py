from guis.panel.resistance.run_test.parse_log import parse_log
from guis.panel.resistance.run_test.make_graph import make_graph

def parse_and_graph():
    print("Enter path to raw resistance data file")
    print("E.g. C:\\Users\\mu2e\\Desktop\\Production\\Data\\Panel data\\FinalQC\\Resistance\\RawData\\resistancetest_20210405161931.log")
    raw_data = input().strip('\"')

    print("Enter panel number. Just the number, not the MN. E.g. 93 or 093.")
    panelid = input()
    panelid = panelid.zfill(3)

    logfilename = raw_data.split("\\")[-1]
    print("logfile name is", logfilename)

    #raw_data = "C:\\Users\\mu2e\\Desktop\\Production\\Data\\Panel data\\FinalQC\\Resistance\\RawData\\resistancetest_20210312131828.log"
    #panelid = "093"
    #logfilename = "resistancetest_20210312131828.log"

    datafilename = parse_log(raw_data)
    print("Data file and plots are at", datafilename)
    make_graph(datafilename, panelid, logfilename)

if __name__ == "__main__":
    parse_and_graph()
