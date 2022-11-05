import os

def main() :
    with open("TUnfoldSystList.txt", "r") as systfile :
        systnames = systfile.readlines()
    
    with open("TUnfoldVariablesList.txt", "r") as varfile :
        varnames = varfile.readlines()

    if not os.path.exists("StandbySlurmJobs") :
        os.mkdir("StandbySlurmJobs")
    
    eras = ["2016ULpreVFP", "2016ULpostVFP", "2017UL", "2018UL"]

    SUBMIT_SCRIPT = open("SLURM_submit.sh", "w")

    for era in eras :
        for var in varnames :
            var = var.strip("\n")
            for syst in systnames :
                syst = syst.strip("\n")

                JOB_FILE_PATH = "StandbySlurmJobs/Unfold_paralllel_" + era + "_" + var + "_" + syst + ".sh"
                SUBMIT_SCRIPT.write("sbatch " + JOB_FILE_PATH + "\n")
                
                print("Currently working with file :: " + JOB_FILE_PATH)
                
                with open(JOB_FILE_PATH, "w") as cfg :
                    cfg.write("#!/bin/sh")
                    cfg.write("\n")
                    cfg.write("#SBATCH  -A standby")
                    cfg.write("\n")
                    cfg.write("#SBATCH --nodes=1")
                    cfg.write("\n")
                    cfg.write("#SBATCH --time=00:05:00")
                    cfg.write("\n")
                    cfg.write("cd /depot/cms/top/bakshi3/TopSpinCorr_Run2_alt_version/CMSSW_10_6_29/src/TopAnalysis/Configuration/analysis/diLeptonic")
                    cfg.write("\n")
                    cfg.write("source /cvmfs/cms.cern.ch/cmsset_default.sh")
                    cfg.write("\n")
                    cfg.write("export SCRAM_ARCH=slc6_amd64_gcc530")
                    cfg.write("\n")
                    cfg.write("eval `scramv1 runtime -sh`")
                    cfg.write("\n")
                    cfg.write("./install/bin/MatrixUnfControl " + era + " Nominal " + syst + " " + var + " combined 0 1 1 0 0 2 1 0")
                    cfg.write("\n")
    SUBMIT_SCRIPT.close()

if __name__ == "__main__":
    main()
