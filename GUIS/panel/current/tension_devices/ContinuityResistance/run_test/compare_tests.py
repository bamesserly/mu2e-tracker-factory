import make_graph

# import MyROOT
import sys, re, time, math
import ROOT

# ROOT = MyROOT.ROOT

f1 = sys.argv[1]
f2 = sys.argv[2]

mg1, g_wires1, g_straws1 = make_graph.make_graph(f1)
mg2, g_wires2, g_straws2 = make_graph.make_graph(f2)

g_wires2.SetLineColor(ROOT.kGreen)
g_wires2.SetMarkerColor(ROOT.kGreen)
g_wires2.SetMarkerSize(0.5)
g_wires2.SetMarkerStyle(20)
g_straws2.SetLineColor(ROOT.kMagenta)
g_straws2.SetMarkerColor(ROOT.kMagenta)
g_straws2.SetMarkerSize(0.5)
g_straws2.SetMarkerStyle(21)

c1 = ROOT.TCanvas()
mg = ROOT.TMultiGraph("mg", "Resistance Test panel_2.5.4 2 months apart")
mg.Add(g_wires1)
mg.Add(g_straws1)
mg.Add(g_wires2)
mg.Add(g_straws2)
mg.SetMaximum(250)
mg.Draw("AP")

l = ROOT.TLegend(0.85, 0.85, 1, 1)
l.AddEntry(g_wires1, "Wires 1")
l.AddEntry(g_straws1, "Straws 1")
l.AddEntry(g_wires2, "Wires 2")
l.AddEntry(g_straws2, "Straws 2")
l.Draw()

c1.SaveAs("log/compare.pdf")


def graph_op(g1, g2, binop):
    sigma = 2
    outliers = []
    N = g1.GetN()
    assert N == g2.GetN()
    g = ROOT.TGraph(N)
    x1, y1 = ROOT.Double(), ROOT.Double()
    x2, y2 = ROOT.Double(), ROOT.Double()
    for i in xrange(N):
        g1.GetPoint(i, x1, y1)
        g2.GetPoint(i, x2, y2)
        assert x1 == x2
        diff = binop(y1, y2)
        g.SetPoint(i, x1, diff)
        if abs(diff) > sigma:
            outliers.append(str(int(x1)))
    g.GetXaxis().SetTitle(g1.GetXaxis().GetTitle())
    g.GetYaxis().SetTitle(g1.GetYaxis().GetTitle())
    return g, outliers


c2 = ROOT.TCanvas()

gdiff, outliers = graph_op(g_wires1, g_wires2, lambda x, y: x - y)
gdiff.GetXaxis().SetRangeUser(-5, 100)
gdiff.SetMarkerStyle(26)
gdiff.SetMarkerSize(0.5)
gdiff.SetMaximum(20)
gdiff.SetMinimum(-10)
# MyROOT.SetTitles(gdiff,"Difference Between Resistance Tests Sept 7 and Nov 30",
#                 "Wire Index","Difference in Resistance (#Omega)")
gdiff.Draw("AP")

tp = ROOT.TPaveText(0.1, 0.8, 0.899, 0.89, "NBNDC")
tp.SetTextAlign(10 + 2)
tp.SetTextSize(0.045)
tp.SetFillColorAlpha(ROOT.kWhite, 0)
s = "Outliers: " + ",".join(outliers)
tp.AddText(s)
tp.Draw()

c2.SaveAs("log/diff.pdf")
