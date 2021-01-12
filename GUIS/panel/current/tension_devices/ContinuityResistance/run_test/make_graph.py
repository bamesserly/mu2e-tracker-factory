# This script takes a data file produced by parse_log and makes
# a graph for visually summarizing the continuity test results.
# Note: this script (and other QC scripts) use python 2.7.
# This script also uses ROOT, and was tested with ROOT5.

import ROOT
import sys, re, time, math, os


def make_graph(datafilename):
    # First get header information that we care about.
    with open(datafilename, "r") as infile:
        for line in infile:
            if not line.startswith("#"):
                continue
            tokens = re.split("[:,]", line)
            if "workerids" in line:
                workers = [s.strip() for s in tokens[1:]]
            elif "panelid" in line:
                panelid = tokens[1].strip()
            elif "datetime" in line:
                timestamp = tokens[1].strip()

    timelabel = time.asctime(time.strptime(timestamp, "%Y%m%d%H%M%S"))
    # Now read the data
    t = ROOT.TTree("t", "t")
    t.ReadFile(datafilename, "idx/I:wire/I:R/D:dR/D:nvalid/D", ",")

    # Create two blank graphs.
    g_wires = ROOT.TGraphErrors(96)
    g_wires.SetMarkerColor(ROOT.kRed)
    g_wires.SetMarkerStyle(24)
    g_wires.SetMarkerSize(1)
    g_wires.SetFillColor(0)
    g_straws = ROOT.TGraphErrors(96)
    g_straws.SetMarkerColor(ROOT.kBlue)
    g_straws.SetMarkerStyle(25)
    g_straws.SetMarkerSize(1)
    g_straws.SetFillColor(0)

    # Lists for keeping track of which wires and straws had "OK" measurements.
    ok_wires = [False] * 96
    ok_straws = [False] * 96

    # Loop over the TTree we just filled from the file.
    # This loop automatically overwrites older measurements
    # for the same straw/wire, so only the latest measurement is in the graph.
    for i in xrange(t.GetEntries()):
        t.GetEntry(i)

        # Select the right graph and "ok" list for wire or straw.
        if t.wire:
            g = g_wires
            ok_list = ok_wires
        else:
            g = g_straws
            ok_list = ok_straws
        if not (math.isinf(t.R) or math.isnan(t.R) or t.R == 0):
            ok_list[t.idx] = True
        else:
            ok_list[t.idx] = False
        g.SetPoint(t.idx, t.idx, t.R)
        g.SetPointError(t.idx, 0, t.dR)

    # Now set up the MultiGraph, axes, labels, etc.
    mg = ROOT.TMultiGraph("mg", "Resistance Test %s %s" % (panelid, timelabel))
    mg.Add(g_wires)
    mg.Add(g_straws)

    c1 = ROOT.TCanvas()

    mg.SetMaximum(min(t.GetMaximum("R") + t.GetMaximum("dR"), 250))
    mg.SetMinimum(max(t.GetMinimum("R") - t.GetMaximum("dR"), 0))
    mg.Draw("AP")
    mg.GetXaxis().SetTitle("Index (0-95)")
    mg.GetYaxis().SetTitle("Resistance (#Omega)")
    mg.GetYaxis().SetTitleOffset(1.25)

    l = ROOT.TLegend(0.85, 0.85, 1, 1)
    l.AddEntry(g_wires, "Wires")
    l.AddEntry(g_straws, "Straws")
    l.Draw()

    # Label for workers who did the test.
    tp = ROOT.TPaveText(0.7, 0.7, 0.899, 0.89, "NBNDC")
    tp.SetTextAlign(10 + 2)
    tp.SetTextSize(0.045)
    tp.SetFillColorAlpha(ROOT.kWhite, 0)
    tp.AddText("Workers:")
    for w in workers:
        tp.AddText(w)
    tp.Draw()

    # Label for wires/straws that are not in the ok_list.
    tp2 = ROOT.TPaveText(0.1, 0.1, 0.6, 0.25, "NBNDC")
    tp2.SetTextAlign(10 + 2)
    tp2.SetTextSize(0.03)
    tp2.SetFillColorAlpha(ROOT.kWhite, 0)
    inf_wires = []
    inf_straws = []
    for i in range(96):
        if not ok_wires[i]:
            inf_wires.append(str(i))
        if not ok_straws[i]:
            inf_straws.append(str(i))
    tp2.AddText("Inf/NaN/0 Wires: " + ",".join(inf_wires))
    tp2.AddText("Inf/NaN/0 Straws:" + ",".join(inf_straws))
    tp2.Draw()

    ROOT.gPad.Modified()
    ROOT.gPad.Update()

    pdfname = datafilename.replace(".csv", ".pdf")
    c1.SaveAs(pdfname)
    os.system("evince %s" % pdfname)
    c1.SaveAs(datafilename.replace(".csv", ".png"))
    return mg, g_wires, g_straws


if __name__ == "__main__":
    datafilename = sys.argv[1]
    make_graph(datafilename)
