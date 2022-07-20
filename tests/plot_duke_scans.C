#include <cassert>
#include <string.h>
#include "TStyle.h"
#include "TChain.h"
#include "TFile.h"
#include "TH1.h"
#include "TTree.h"
#include "TKey.h"
#include "Riostream.h"
#include "TCanvas.h"
#include "TF1.h"
#include "TPaveLabel.h"

void PlotTH1(TH1* h1, std::string tag, double ymax = -1, bool do_log_scale = false, bool do_fit = false) {
  gStyle->SetOptStat(0);
  gStyle->SetOptFit(1);
  //TH1::SetDefaultSumw2();

  TCanvas cF ("c4","c4"); 

  h1->SetTitle(tag.c_str());
  h1->Draw("HIST");

  if(do_log_scale)
    cF.SetLogy();

  cF.Update();

  if (ymax > 0)
    h1->GetYaxis()->SetRangeUser(0,ymax);

  if(do_fit){
    // gaussian fit
    h1->Fit("gaus","0");
    h1->Draw("");
    cF.Update();
    TF1 *fit1 = (TF1*)h1->GetFunction("gaus");
    fit1->SetLineColor(kRed);
    fit1->Draw("SAME");
  }

  /* 
  // draw a line
  TLine *line = new TLine(0,0,0,cF.GetUymax());
  line->SetLineColor(kBlue);
  line->Draw();
  */

  cF.Print(Form("%s.png", tag.c_str()));
  //cF.Print(Form("%s.eps", tag.c_str()));
}

/*
run from the command line like:

for i in `cat dukes_scans_preproduction_list.txt`; do echo $i; root -l -b -q plot_duke_scans.C+\(\"$i\"\); done

root files downloaded from http://mu2e.phy.duke.edu/scan/VI/data/Panel/panel_2.5
*/
int plot_duke_scans(std::string f) {
  TList* sourcelist = new TList();
  std::string filename = "rootfiles/" + f + ".root";
  sourcelist->Add(TFile::Open(filename.c_str()));
  TFile *first_source = (TFile*)sourcelist->First();
  first_source->cd();
  Bool_t status = TH1::AddDirectoryStatus();
  TH1::AddDirectory(kFALSE);

  std::cout << "Starting loop over file objects\n";
  // loop over all keys in this directory
  TChain *globChain = 0;
  TIter nextkey( gDirectory->GetListOfKeys() );
  TKey *key, *oldkey=0;
  int i = 0;
  while ( (key = (TKey*)nextkey())) {
    ++i;
    //keep only the highest cycle number for each key
    if (oldkey && !strcmp(oldkey->GetName(),key->GetName())) continue;

    // read object from first source file
    TObject *obj = key->ReadObj();
    std::string name = obj->GetName();
    std::cout << i << "  " << name << "\n";

    TH1F* curv = dynamic_cast<TH1F*>(obj);
    TCanvas* canv= dynamic_cast<TCanvas*>(obj);
    if(canv)
      canv->SetName("c");
    assert(!(curv && canv));
    if (curv){
      //PlotTH1(curv, name);
    }   
    else if (canv){
      // Add title to canvases that don't already have one
      if (name.find("WIRE") != std::string::npos ||
          name.find("final") != std::string::npos ||
          //name.find("\ ") != std::string::npos ||
          name.find(" ") != std::string::npos ||
          name.find("plots") != std::string::npos) {
        canv->Draw();
        gStyle->SetOptTitle(0);
        TPaveLabel *title = new TPaveLabel(.0,.92,.35,.99,name.c_str(),"brndc");
        title->Draw(); 
      }
      // remove spaces and slashes, which Print doesn't like
      //std::string slash("\/");
      std::string slash("/");
      std::size_t pos = name.find(slash);
      if (pos != std::string::npos) {
        name.replace(pos, slash.length(), "_");
        std::cout << "new name " << name << "\n";
      }
      
      canv->Print(Form("plots/%s/%s.png", f.c_str(), name.c_str()));
      //if(i > 5) return 0;
    }
    else std::cout << "NEITHER\n";


  } // while ( ( TKey *key = (TKey*)nextkey() ) )

  return 0;
}
