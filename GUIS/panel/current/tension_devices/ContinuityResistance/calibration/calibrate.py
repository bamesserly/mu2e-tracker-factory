from sig_digs_error_bars import sig_digs_error_bars
import ROOT

t = ROOT.TTree("t", "t")
t.ReadFile("calibration_data.csv", "R/D:dR/D:Arduino_R/D:ADC/D:ADC_std/D:dADC/D")

# resistance_ref*(1023/(1.0*adc_avg) - 1);
# R = R_ref*(1023/ADC - 1)
# x = 1/ADC
# R = R_Ref*(1023*x - 1)
# R = (R_Ref*1023)*x - R_Ref

c1 = ROOT.TCanvas("c1", "c1")
N_entries = t.GetEntries()
g = ROOT.TGraphErrors(N_entries)
for i in range(N_entries):
    t.GetEntry(i)
    x = 1.0 / t.ADC
    y = t.R
    dx = t.dADC / (t.ADC ** 2)
    dy = t.dR
    g.SetPoint(i, x, y)
    g.SetPointError(i, dx, dy)

# t.Draw("R:1/ADC")
# g = ROOT.gROOT.FindObject("Graph").Clone("g")
g.Sort()
g.Draw("AP")

f1 = ROOT.TF1("f1", "[0]*(1023*x - 1)", 0, 0.005)
f1.SetLineWidth(1)

fit_result = g.Fit(f1, "S")

R_ref = f1.GetParameter(0)
dR_ref = f1.GetParError(0)

f2 = ROOT.TF1("f2", "[0]+[1]*(1023*x-1)", 0, 0.005)
f2.SetParameters(0, R_ref)
f2.SetLineWidth(1)
f2.SetLineColor(ROOT.kRed)
fit_result = g.Fit(f2, "S+")

const_ref = f2.GetParameter(0)
dconst_ref = f2.GetParError(0)
R2_ref = f2.GetParameter(1)
dR2_ref = f2.GetParError(1)

R_ref_string, dR_ref_string = sig_digs_error_bars(R_ref, dR_ref)
R2_ref_string, dR2_ref_string = sig_digs_error_bars(R2_ref, dR2_ref)
const_ref_string, dconst_ref_string = sig_digs_error_bars(const_ref, dconst_ref)


def makelabel(x, y, lbl):
    label = ROOT.TLatex()
    label.SetNDC()
    label.SetText(x, y, lbl)
    label.Draw()
    return label


l0 = makelabel(0.12, 0.85, "Proportional fit:")
l1 = makelabel(0.12, 0.8, "R_{ref} = %s #pm %s" % (R_ref_string, dR_ref_string))
l2 = makelabel(0.12, 0.74, "Affine fit:")
l3 = makelabel(
    0.12,
    0.69,
    "R_{ref} = %s #pm %s, const = %s #pm %s"
    % (R2_ref_string, dR2_ref_string, const_ref_string, dconst_ref_string),
)


g.GetXaxis().SetTitle("1/ADC Value")
g.GetYaxis().SetTitle("Measured Resistance (#Omega)")
g.SetTitle("Panel QC Resistance Tester Calibration")

ROOT.gPad.Modified()
ROOT.gPad.Update()

c1.SaveAs("calibration.pdf")

# Do resolution vs resistance plot.
c2 = ROOT.TCanvas("c2", "c2")


def adc_to_res(adc):
    return R_ref * (1023 / (1.0 * adc) - 1)


def adc_to_dres(adc):
    return dR_ref * (1023 / (1.0 * adc) - 1)


adc_values = range(1, 1022)
r0 = adc_to_res(adc_values[0])

g_res = ROOT.TGraph(len(adc_values) - 1)
g_res.SetMarkerStyle(2)
g_res.SetMarkerSize(0.3)
g_res.SetFillColor(ROOT.kBlack)

g_unc = ROOT.TGraph(len(adc_values) - 1)
g_unc.SetMarkerStyle(2)
g_unc.SetMarkerSize(0.3)
g_unc.SetMarkerColor(ROOT.kBlue)
g_unc.SetFillColor(ROOT.kBlue)

for i in adc_values[1:-1]:
    r1 = adc_to_res(i)
    diff = abs(r1 - r0)
    g_res.SetPoint(i, r1, diff)
    g_unc.SetPoint(i, r1, adc_to_dres(i))
    r0 = r1

mg = ROOT.TMultiGraph("mg", "Resistance Measurement Quality")
mg.Add(g_res)
mg.Add(g_unc)
mg.Draw("AP")
mg.GetXaxis().SetRangeUser(0, 300)
mg.SetMaximum(2)
mg.SetMinimum(0)

tl = ROOT.TLegend(0.1, 0.5, 0.5, 0.9)
tl.AddEntry(g_res, "ADC Resolution")
tl.AddEntry(g_unc, "Measurement Uncertainty")
tl.Draw()

mg.GetXaxis().SetTitle("Resistance (#Omega)")
mg.GetYaxis().SetTitle("#Omega")

ROOT.gPad.Modified()
ROOT.gPad.Update()
c2.SaveAs("measurement_quality.pdf")
