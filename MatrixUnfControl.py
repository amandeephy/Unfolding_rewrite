
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
