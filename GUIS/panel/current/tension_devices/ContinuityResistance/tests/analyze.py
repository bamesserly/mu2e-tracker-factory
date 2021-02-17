import MyROOT

ROOT = MyROOT.ROOT
import numpy

data = numpy.loadtxt(
    "practice_panel_data_Feb232018.csv", delimiter=",", usecols=range(103)
)

wires = {}
straws = {}

resistance_ref = 149.83978481001057
delta_resistance_refs = 0.34182766715695534

for i, line in enumerate(data):
    index = int(line[0])
    wire = bool(line[1])
    adc_values = line[2:102]
    resistance = line[102]

    # Discard the 10th and 90th percentiles
    n = len(adc_values)
    adc_values = sorted(adc_values)[int(round(0.1 * n)) : int(round(0.9 * n))]
    # resistance_values = [resistance_ref*(adc/float(1023-adc)) for adc in adc_values]
    # resistance_values = [resistance_ref/(1023/float(adc) - 1) for adc in adc_values]
    resistance_values = [
        resistance_ref * (1023 / (1.0 * adc) - 1) for adc in adc_values
    ]
    resistance_mean = numpy.mean(resistance_values, dtype=numpy.float64)
    resistance_stdv = numpy.std(resistance_values, dtype=numpy.float64)

    print i, index, wire
    print "Resistance mean from Arduino:", resistance
    print "Resistance mean from Python: ", resistance_mean

    if wire:
        target = wires
    else:
        target = straws

    target[index] = (resistance_mean, resistance_stdv)

straws = {
    k: v for k, v in straws.iteritems() if not (numpy.isnan(v[0]) or numpy.isnan(v[1]))
}
npoints = len(straws)  # data.shape[1]
g_straws = ROOT.TGraphErrors(npoints)
g_straws.SetLineColor(ROOT.kBlue)
g_straws.SetMarkerColor(ROOT.kBlue)
for i, kv in enumerate(straws.iteritems()):
    index = kv[0]
    mean = kv[1][0]
    stdv = kv[1][1]
    if numpy.isnan(mean) or numpy.isnan(stdv):
        continue
    g_straws.SetPoint(i, index, mean)
    g_straws.SetPointError(i, 0, stdv)

wires = {
    k: v for k, v in wires.iteritems() if not (numpy.isnan(v[0]) or numpy.isnan(v[1]))
}
npoints = len(wires)
g_wires = ROOT.TGraphErrors(npoints)
for i, kv in enumerate(wires.iteritems()):
    index = kv[0]
    mean = kv[1][0]
    stdv = kv[1][1]
    if numpy.isnan(mean) or numpy.isnan(stdv):
        continue
    g_wires.SetPoint(i, index, mean)
    g_wires.SetPointError(i, 0, stdv)

c1 = ROOT.TCanvas("c1", "c1")
c1.cd()
mg = ROOT.TMultiGraph("mg", "mg")
mg.Add(g_wires)
mg.Add(g_straws)
mg.Draw("ALP")
MyROOT.SetTitles(
    mg, "Practice Panel", "Position Index (0 = longest straw)", "Resistance (#Omega)"
)
mg.SetMinimum(0)

g_straws.SetFillColor(ROOT.kBlue)
g_wires.SetFillColor(ROOT.kBlack)
tl = ROOT.TLegend(0.1, 0.7, 0.3, 0.9)
tl.AddEntry(g_wires, "Wires")
tl.AddEntry(g_straws, "Straws")
tl.Draw()

ROOT.gPad.Modified()
ROOT.gPad.Update()

c1.SaveAs("practice_panel_test.pdf")
