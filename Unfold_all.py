import os
import ROOT
import argparse
import numpy as np

class MatrixUnfControl() :
  def __init__(self, era, lumi) :
    self.fEra  = era
    self.fLumi = lumi

    # Empty arrays, similar to the TObjArrays in the cpp version
    self.fMCFiles   = []
    self.fBgFiles   = []
    self.fDataFiles = []
    self.fSysFiles  = []
    self.fDataArray = []
    self.fRecArray  = []
    self.fGenArray  = []
    
    self.fVisGenArray = []
    self.fMigMatArray = []
    self.fBgArray     = []

    self.fBgSamplesArray = []
    self.fMigMatSysArray = []
    self.fTrueDataArray  = []

  def SetTauOptions(self, constrainTau, taumin, taumax, tausys, minRhoAVG) :
    # Tau options and Regularization 
    self.fConstrainTau = constrainTau
    self.fTauMin       = taumin
    self.fTauMax       = taumax
    self.fTauSys       = tausys
    self.fMinRhoAVG    = minRhoAVG

  def SetOptions(self, args, closuretest, combinedsumptt, subtbgmcfromdata, dosubtrbg, useareaconstrain, regmode) :
    # Other options
    self.fClosureTest       = closuretest     
    self.fSelfConsistency   = args.selfconsistency
    self.fEnsembleTest      = args.ensembletest
    self.fLinearityTest     = args.linearitytest
    self.fAllowRebinOption  = args.allowrebin  
    self.fCombinedSumptt    = combinedsumptt
    self.fSubtrBgMCFromData = subtbgmcfromdata 
    self.fDoSubtrBg         = dosubtrbg        
    self.fUseAreaConstrain  = useareaconstrain
    self.fUseBiasInUnfold   = args.usebiasintunfold
    self.fsetSyst           = args.setsyst
    self.fRegMode           = regmode          

  def FillHistoArrays(self, channel, variablename) :

    # Make sure the MC files exist
    try :
      assert (self.fMCFiles)
    except AssertionError:
      print("No MC files provided/found")

    nbgfiles   = len(self.fBgFiles)
    ndatafiles = len(self.fDataFiles)
    nMCfiles   = len(self.fMCFiles)
    nsysfiles  = len(self.fSysFiles)

    # Make sure equal number of systs in each channel
    try :
      assert (nsysfiles %  nMCfiles) == 0
    except AssertionError :
      print("Didn't find the same number of systematic files in each channel")

    ##########
    # ADD DATA
    ##########

    data_yields_by_channel = {"ee" :  0, "emu" : 0, "mumu" : 0, "combined" : 0}

    if(self.fDataFiles) :
      # Get a sample histogram from the 0th element and then use it as the final histogram
      temp_data_file      = ROOT.TFile.Open(self.fDataFiles[0], "READ")
      temp_data_histogram = temp_data_file.Get("hreco_" + variablename).Clone(variablename + "_data")
      temp_data_histogram.Reset()

      histograms_by_channel  = {}

      # Similarily for the one across channels
      # Assign a dummy empty histogram
      for channel in data_yields_by_channel.keys() :
        temp_data_histogram_channel    = temp_data_file.Get("hreco_" + variablename).Clone(variablename + "_databgsub_" + channel)
        temp_data_histogram_channel.Reset()
        histograms_by_channel[channel] = temp_data_histogram_channel

      # Now loop over all files add 
      for datafile in self.fDataFiles :
        ipfile = ROOT.TFile.Open(datafile, "READ")
        iphist = ipfile.Get("hreco_" + variablename)

        # Add yields from all channels
        if   ("histosTUnfold_ee_" in datafile) :
          data_yields_by_channel["ee"]     += iphist.Integral()
          histograms_by_channel["ee"].Add(iphist)

        elif ("histosTUnfold_emu_" in datafile) :
          data_yields_by_channel["emu"]    += iphist.Integral()
          histograms_by_channel["emu"].Add(iphist)

        elif ("histosTUnfold_mumu_" in datafile) :
          data_yields_by_channel["mumu"]   += iphist.Integral()
          histograms_by_channel["mumu"].Add(iphist)

        # And finally then for combined 
        data_yields_by_channel["combined"] += iphist.Integral()
        temp_data_histogram.Add(iphist)
        
        # Safely close the file and delete temp variables
        del iphist
        ipfile.Close()

    print("")
    print("Data yields from counting ::")
    print("data yields ee emu mumu combined: " + str(data_yields_by_channel["ee"]) + " " + str(data_yields_by_channel["emu"]) + " " + str(data_yields_by_channel["mumu"]) + " " + str(data_yields_by_channel["combined"]))
    self.fDataArray.append(temp_data_histogram)

    print("Data yields from histogram integrals :: ")
    print("data yields ee emu mumu combined: " + str(histograms_by_channel["ee"].Integral()) + " " + str(histograms_by_channel["emu"].Integral()) + " " + str(histograms_by_channel["mumu"].Integral()) + " " + str(temp_data_histogram.Integral()))
    
    #####################
    # ADD MC/SIGNAL FILES
    #####################


    # Safely close the file and delete temp variables
    del temp_data_histogram_channel
    del temp_data_histogram
    temp_data_file.Close()
      
def main() :

    # Define the arguments 
    # Revisit the help sections here
    parser = argparse.ArgumentParser(description='Arguments to unfolding')
    parser.add_argument('--era'     , type=str, help='Dataset era options : 2016ULpreVFP, 2016ULpostVFP, 2016UL, 2017UL, 2018UL')
    parser.add_argument('--syst'    , type=str, help='Systematic over which we want to run')
    parser.add_argument('--channel' , type=str, help='ee, emu, mumu or combined')
    parser.add_argument('--selfconsistency' , type=bool)
    parser.add_argument('--usebiasintunfold', type=bool)
    parser.add_argument('--allowrebin'      , type=bool)
    parser.add_argument('--ensembletest'    , type=bool)
    parser.add_argument('--linearitytest'   , type=bool)
    parser.add_argument('--setsyst'         , type=bool, help='if on it will use TUnfoldSys class AddSysError()')
    parser.add_argument('--bkgsuboption'    , type=int , help='0 for no backgrounds, 2 for background subtraction')

    # Obtain arguments from arg parser
    args = parser.parse_args()

    ERA     = args.era
    SYST    = args.syst
    CHANNEL = args.channel

    print(ERA + " " + SYST +  " " + CHANNEL)

    # Grab lumi information for each specific ERA
    if   (ERA == "2016UL") : LUMI = 36310.0
    elif (ERA == "2017UL") : LUMI = 41480.0
    elif (ERA == "2018UL") : LUMI = 41480.0
    elif (ERA == "2016ULpreVFP")  : LUMI = 41480.0
    elif (ERA == "2016ULpostVFP") : LUMI = 41480.0
    else : print("ERA :: " + ERA + "not currently supported")

    # Create object of type MatrixUnfControl
    # This declares the arrays needed for filelists and hists

    mcontrol = MatrixUnfControl(ERA, LUMI)

    print("Setting tau options")
    mcontrol.SetTauOptions(
      constrainTau = False,
      tausys      = 0, 
      taumin      = 1e-6,
      taumax      = 1e-3,  
      minRhoAVG   = True)

    print("Setting other unfolding options")
    mcontrol.SetOptions(args, 
      closuretest      = False,  # if self consistency is on, this doesn't matter
      combinedsumptt   = False, 
      subtbgmcfromdata = (True if args.bkgsuboption == 2 else False),  # Manual background subtraction  | this subtracts bg mc from data before using TUnfold
      dosubtrbg        = (True if args.bkgsuboption == 1 else False),  # TUnfold background subtraction | turn this on to provide bg distribution to be subtracted by TUnfold
      useareaconstrain = True,
      regmode          = 3      # (1=size,2=derivative,3=curvature,4=mixed,5=densityCurvature) 
    )


    # Needs to be done
    # std::cout<<"adding unfold variables"<<std::endl
    # mcontrol.AddUnfoldVariables("TUnfoldVariablesList.txt")

    # PreunfoldedFile = os.path.join("Preunfolded_"    + ERA.replace("UL", ""), SYST, CHANNEL)
    # UnfoldedFile    = os.path.join("TUnfoldResults_" + ERA.replace("UL", ""), SYST, CHANNEL)

    ##########
    # MC FILES 
    ##########

    # Cross-sections borrowed from : https:# gitlab.cern.ch/jthieman/TopAnalysis/-/blob/SpinCorr-Run2-UL/Configuration/analysis/diLeptonic/src/PlotterConfigurationHelper.cc#L1209  
    
    MC_filepath     = os.path.join("TUnfoldHistoFileLists_" + ERA.replace("UL", ""), "TUnfoldHistoFileList_" + SYST + "_" + CHANNEL + ".txt")
        
    with open(MC_filepath) as filepath :
      samplenames = filepath.readlines()

    # Instead of feeding it the xsection and lumi, we can look it up later when scaling the histos
    for samplename in samplenames :
        samplename = samplename.replace("\n", "")
        if   (samplename == "")    : continue
        elif ("run" in samplename) : mcontrol.fDataFiles.append(samplename)
        elif ("ttbarsignalplustau" in samplename or "ttbarsignalviatau" in samplename) : mcontrol.fMCFiles.append(samplename)
        else : mcontrol.fBgFiles.append(samplename)

    del samplenames

    #############
    # SYSTEMATICS
    #############

    with open("TUnfoldSystList.txt", "r") as sysfile :
      systs = sysfile.readlines()

    VectorOfInputSystematics = [] # The names in the Systfile list
    VectorOfValidSystematics = [] # The actual directory names

    for syst in systs :
      syst = syst.replace("\n", "")
      VectorOfInputSystematics.append(syst)

      if (syst == "TOP_PT" or "PDF" in syst) : 
        VectorOfValidSystematics.append(syst)

      elif (syst == "SCALE") :
        VectorOfValidSystematics.append("MESCALE_UP")
        VectorOfValidSystematics.append("MESCALE_DOWN")
        VectorOfValidSystematics.append("MEFACSCALE_UP")
        VectorOfValidSystematics.append("MEFACSCALE_DOWN")
        VectorOfValidSystematics.append("MERENSCALE_UP")
        VectorOfValidSystematics.append("MERENSCALE_DOWN")

      elif (syst == "BFRAG") :
        VectorOfValidSystematics.append(syst + "_UP")
        VectorOfValidSystematics.append(syst + "_DOWN")
        VectorOfValidSystematics.append(syst + "_PETERSON")

      elif (syst == "COLORREC") :
        VectorOfValidSystematics.append("ERDON")
        VectorOfValidSystematics.append("ERDONRETUNE")
        VectorOfValidSystematics.append("GLUONMOVETUNE")

      else :
        VectorOfValidSystematics.append(syst + "_UP")
        VectorOfValidSystematics.append(syst + "_DOWN")

    del systs

    print(mcontrol.fDataFiles)
    print('')
    print(mcontrol.fMCFiles)
    print('')
    print(mcontrol.fBgFiles)

    mcontrol.FillHistoArrays(CHANNEL, "b1k")

if __name__ == '__main__' :
  main()