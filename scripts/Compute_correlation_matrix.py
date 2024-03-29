import tqdm
import math
import uproot
import numpy  as np

def main() :
    # 2016 variable list
    # var_list = ['b1k', 'b2k','b1r','b2r','b1n','b2n','b1j','b2j','b1q','b2q',
    #             'c_kk','c_rr','c_nn','c_Prk','c_Mrk','c_Pnr','c_Mnr','c_Pnk','c_Mnk',
    #             'll_cHel','ll_cLab','llbar_delta_phi']
    
    # Updated 1D variable list
    var_list  = ['b1k', 'b2k','b1r','b2r','b1n','b2n','b1j','b2j','b1q','b2q',
                 'c_kk','c_rr','c_nn','c_Prk','c_Mrk','c_Pnr','c_Mnr','c_Pnk','c_Mnk',
                 'c_kj','c_rq' ,'c_han','c_tra','c_sca','c_Prj','c_Mrj','c_kjL','c_rqL',
                 'c_rkP', 'c_rkM', 'c_nrP', 'c_nrM', 'c_nkP', 'c_nkM',
                 'll_cHel','ll_cLab','llbar_delta_phi', 'llbar_delta_eta']
    
    # Updated 2D variable list
    # var_list  = ['b1k_mttbar', 'b2k_mttbar','b1r_mttbar','b2r_mttbar','b1n_mttbar','b2n_mttbar','b1j_mttbar','b2j_mttbar','b1q_mttbar','b2q_mttbar',
    #              'c_kk_mttbar','c_rr_mttbar','c_nn_mttbar','c_Prk_mttbar','c_Mrk_mttbar','c_Pnr_mttbar','c_Mnr_mttbar','c_Pnk_mttbar','c_Mnk_mttbar',
    #              'c_kj_mttbar','c_rq_mttbar' ,'c_han_mttbar','c_tra_mttbar','c_sca_mttbar','c_Prj_mttbar','c_Mrj_mttbar','c_kjL_mttbar','c_rqL_mttbar',
    #              'c_rkP_mttbar', 'c_rkM_mttbar', 'c_nrP_mttbar', 'c_nrM_mttbar', 'c_nkP_mttbar', 'c_nkM_mttbar',
    #              'll_cHel_mttbar','ll_cLab_mttbar','llbar_delta_phi_mttbar', 'llbar_delta_eta_mttbar']
    
    BASEDIR = "/depot/cms/top/bakshi3/TopSpinCorr_Run2_generalized_ND/CMSSW_10_6_30/src/TopAnalysis/Configuration/analysis/diLeptonic/TUnfoldResults_2016/Nominal/combined/"

    fileptr_dict = {}
    for var in var_list :
        fileptr_dict[var] = uproot.open(BASEDIR + str(var) + ".root")

    nPE      = 1000
    nbinsvar = 6
    nbinstot = nbinsvar * len(var_list)
    r        = np.zeros((nbinstot,nbinstot))
    cov      = np.zeros((nbinstot,nbinstot))

    print('Begin processing matrices with nPE :: ' + str(nPE))

    # Create an array with varname repeated nbinsvar times and flatten it
    # Some fun list comprehension stuff
    n_times_over   = [[var] * nbinsvar for var in var_list]
    flattened_vars = [item for sublist in n_times_over for item in sublist]

    from tqdm import tqdm

    for xbin in tqdm(range(nbinstot)) :
        for ybin in range(nbinstot) :
            
            mu_x = 0
            mu_y = 0
            
            # Returns a string corresponding to varname
            xvar = flattened_vars[xbin]
            yvar = flattened_vars[ybin]
            
            # ##################
            # Computing the mean
            # ##################
            
            for i in range(nPE) :
                X = fileptr_dict[xvar][xvar + '_pseudo' + str(i) + 'TUnfResult_rebinnedA'].values()
                Y = fileptr_dict[yvar][yvar + '_pseudo' + str(i) + 'TUnfResult_rebinnedA'].values()   
                
                # modulo nbinsvar for the var
                mu_x += X[xbin%nbinsvar]
                mu_y += Y[ybin%nbinsvar]
                
            mu_x /= nPE
            mu_y /= nPE

            sum_xy  = 0
            diff_x2 = 0
            diff_y2 = 0
            
            for i in range(nPE) :
                X = fileptr_dict[xvar][xvar +'_pseudo' + str(i) + 'TUnfResult_rebinnedA'].values()
                Y = fileptr_dict[yvar][yvar +'_pseudo' + str(i) + 'TUnfResult_rebinnedA'].values()   
                
                diff_x2 += (X[xbin%nbinsvar] - mu_x)**2
                diff_y2 += (Y[ybin%nbinsvar] - mu_y)**2
                
                sum_xy  += (X[xbin%nbinsvar] - mu_x) * (Y[ybin%nbinsvar] - mu_y)
                
            cov[xbin][ybin] = sum_xy / nPE
            
            # Correlation is covariance normalized by the 2 variances
            r[xbin][ybin]   = sum_xy / math.sqrt(diff_x2 * diff_y2)

    np.savetxt('Correlation_matrix_1D_38x38_1000PE_updated.txt',   r, fmt='%1.6f')
    np.savetxt('Covariance_matrix_1D_38x38_1000PE_updated.txt' , cov, fmt='%1.6f')

if __name__ == '__main__' :
    main()
