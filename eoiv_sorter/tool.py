import pandas as pd
import json
import numpy as np

from scipy.interpolate import interp1d
from scipy.stats import norm, gamma

#########################################################################
# Utility functions 
#########################################################################

from .utility import utility_model_json_to_model_dict, utility_model_list_to_model_dict, utility_model_dict_flatten_single_values, utility_model_dict_to_model_json

#########################################################################
# RW Equity functions 
#########################################################################

def skt_smoothing(factor_loadings):
    """ Creates a copy of the factor_loadings Table with the Skew, Kurtosis and TermStructureBeta columns that have been smoothed for minor strike ticks e.g. 0.65, 0.75, ... 1.25, 1.35.

    Args: 
        factor_loadings: A pandas table representing the Factor Loadings table in the model. This must include the 'SkewBeta','KurtosisBeta' & 'TermStructureBeta' columns. 

    Returns:

        A pandas table representing the Factor Loadings table, where the values of 'SkewBeta','KurtosisBeta' & 'TermStructureBeta' have been smoothed at minor strike ticks using linear interpolation between the major ticks. 
               
    """      
    skt = factor_loadings[['SkewBeta','KurtosisBeta','TermStructureBeta']].apply(pd.to_numeric)
    skt_actual = skt[skt.index.isin([i/10 for i in range(6,15)], level='Strike')]
    
    out_strikes = [i/100 for i in range(60,145,5)]
    
    
    SKT_Smoothed = skt_actual.reset_index()
    SKT_Smoothed = SKT_Smoothed.groupby('Maturity').apply(
        lambda x:pd.DataFrame.from_dict({
            'Strike':out_strikes,
            'SmooSkewBeta':interp1d(x['Strike'],x['SkewBeta'])(out_strikes),
            'SmooKurtosisBeta':interp1d(x['Strike'],x['KurtosisBeta'])(out_strikes),
            'SmooTermStructureBeta':interp1d(x['Strike'],x['TermStructureBeta'])(out_strikes),
        }))

    SKT_Smoothed = SKT_Smoothed.reset_index()
    SKT_Smoothed = SKT_Smoothed.drop('level_1',axis=1)
    SKT_Smoothed = SKT_Smoothed.set_index(['Maturity','Strike'])
    
    return SKT_Smoothed

def probability_of_negative_IV(c_L, mpd, factor_loadings, iv_column='IVInf', step_size = 1/100):
    """ Calculation of the probablities of negative IVs being produced by the model. See https://erswiki.analytics.moodys.net/display/EI/Standard+calibration+of+the+real-world+equity+implied+volatility+model for the definition of the analytic derivation of the negative rate probablilities.  

    Args: 
        c_L: float. The scaling factor of the model.
        mpd: dictonary. The *model-parameter* dictionary containing all parameters required from the input models.
        factor_loadings: pandas table. Representing the Factor Loadings table of the model. This is derived during the tool run, and may be smoothed first using *skt_smoothing*.
        iv_column: string, defaults to 'IVInf'. The column in 'factor_loadings' that will be used as the volatility surface in the calculation. This should be 'IVInf' or 'InitialIV'.
        step_size: float, default 1/100. The granularity of the percentages where we will evaluate the negative rate probablities. At the default level this will calculate probablilites at [0.01, 0.02, ..., 0.98, 0.99]

    Returns:

        An unnamed tuple containing the results:
        [0], float: The maximum negative rate probablilty. This is the maximum value of the observed cumulative probablilty across all terms and strikes in the IV surface.
        [1], dictionary: A table of  the *used derived constants* calcluated in the process of calculating negative IV probablities. This can be used to check calculated values.  
        
        udc = {
            'gamma_k':gamma_k,
            'gamma_theta':gamma_theta,        
            'sigma_J2':sigma_J2,
            'sys_vol': sys_vol,
            'variance_mean': variance_mean,
            'variance_var': variance_var,
            'nu_infty':nu_infty,
            'parameter_a': parameter_a,
            'parameter_b': parameter_b        
        }
               
    """    
    # 1. Extract parameters from mpd dictionary
    
    F1_Var_RevLevel = float(mpd['F1.SVJD']['BE_SVJD_E_Var_RevLevel_F1'])
    F1_Var_Vol = float(mpd['F1.SVJD']['BE_SVJD_E_Var_Vol_F1'])
    F1_Var_RevRate = float(mpd['F1.SVJD']['BE_SVJD_E_Var_RevRate_F1'])
    #F1_Var_StartVal = float(mpd['F1.SVJD']['BE_SVJD_E_Var_StartVal_F1'])
    #F1_Var_Correl = float(mpd['F1.SVJD']['BE_SVJD_E_Var_Correl_F1'])

    F1_Jump_ArrivalRate = float(mpd['F1.SVJD']['BE_SVJD_E_Jump_Lambda_F1'])
    F1_Jump_Mean = float(mpd['F1.SVJD']['BE_SVJD_E_Jump_Mean_F1'])
    F1_Jump_Vol = float(mpd['F1.SVJD']['BE_SVJD_E_Jump_Vol_F1'])

    Asset_Beta_1 = float(mpd['Asset.Betas']['BE_E_Beta_f1'])
    Asset_Beta_2 = float(mpd['Asset.Betas']['BE_E_Beta_f2'])
    Asset_Beta_3 = float(mpd['Asset.Betas']['BE_E_Beta_f3'])
    Asset_Beta_4 = float(mpd['Asset.Betas']['BE_E_Beta_f4'])
    Asset_Beta_5 = float(mpd['Asset.Betas']['BE_E_Beta_f5'])
    Asset_Beta_6 = float(mpd['Asset.Betas']['BE_E_Beta_f6'])

    Asset_Var_RevLevel = float(mpd['Asset.SVJD']['BE_SVJD_E_Var_RevLevel'])
    Asset_Var_Vol = float(mpd['Asset.SVJD']['BE_SVJD_E_Var_Vol'])
    Asset_Var_RevRate = float(mpd['Asset.SVJD']['BE_SVJD_E_Var_RevRate'])

    Asset_Jump_ArrivalRate = float(mpd['Asset.SVJD']['BE_SVJD_E_Jump_Lambda'])
    Asset_Jump_Mean = float(mpd['Asset.SVJD']['BE_SVJD_E_Jump_Mean'])
    Asset_Jump_Vol = float(mpd['Asset.SVJD']['BE_SVJD_E_Jump_Vol'])

    # Factor Var = Vol**2
    F2_Var = float(mpd['Factors.Const']['BE_E_Fix_f2_s1']) ** 2
    F3_Var = float(mpd['Factors.Const']['BE_E_Fix_f3_s1']) ** 2
    F4_Var = float(mpd['Factors.Const']['BE_E_Fix_f4_s1']) ** 2
    F5_Var = float(mpd['Factors.Const']['BE_E_Fix_f5_s1']) ** 2
    F6_Var = float(mpd['Factors.Const']['BE_E_Fix_f6_s1']) ** 2
    
    # Create matrix arrays for Factors 2-6 and calculate systematic volatility component
    asset_beta_2to5 = np.array([Asset_Beta_2,Asset_Beta_3,Asset_Beta_4,Asset_Beta_5,Asset_Beta_6])
    factor_vars_2to5  = np.array([F2_Var,F3_Var,F4_Var,F5_Var,F6_Var])
    sys_vol = (asset_beta_2to5**2).dot(factor_vars_2to5)  
    
    # Take SKT (Skew-Kurtosis-TermStructure) from the factor loadings
    
    SKT = factor_loadings[['SkewBeta','KurtosisBeta','TermStructureBeta']].apply(pd.to_numeric)
    
    # 2. Calculate constant parameters

    gamma_k = ( 
      (Asset_Beta_1**2 *  F1_Var_RevLevel +  Asset_Var_RevLevel)**2 / 
      (Asset_Beta_1**4 *  F1_Var_RevLevel *  F1_Var_Vol**2 / (2*F1_Var_RevRate) +  Asset_Var_RevLevel *  Asset_Var_Vol**2 / (2*Asset_Var_RevRate))
    )

    gamma_theta = (
        ( Asset_Beta_1**4 * F1_Var_RevLevel * F1_Var_Vol**2 / (2*F1_Var_RevRate) + Asset_Var_RevLevel * Asset_Var_Vol**2/(2*Asset_Var_RevRate))
        / (Asset_Beta_1**2 * F1_Var_RevLevel + Asset_Var_RevLevel))

    beta_2 = SKT.apply(lambda i:i**2).sum(axis=1).apply(lambda i: i**0.5)

    sigma_J2 = (
            0.25*F1_Jump_ArrivalRate*
            (Asset_Beta_1**2)*
            (F1_Jump_Mean**2 +
            F1_Jump_Vol**2) +
            0.25*Asset_Jump_ArrivalRate*
            (Asset_Jump_Mean**2 +
            Asset_Jump_Vol**2)
    )

    asset_beta_2to5 = np.array([Asset_Beta_2,Asset_Beta_3,Asset_Beta_4,Asset_Beta_5,Asset_Beta_6])
    factor_vars_2to5  = np.array([F2_Var,F3_Var,F4_Var,F5_Var,F6_Var])
    sys_vol = (asset_beta_2to5**2).dot(factor_vars_2to5)

    variance_mean = (
        Asset_Beta_1**2*
        F1_Var_RevLevel +
        sys_vol +
        Asset_Var_RevLevel 
    )

    variance_var = (
        Asset_Beta_1**4*
        F1_Var_RevLevel*
        F1_Var_Vol**2/
        (2*F1_Var_RevRate) +
        Asset_Var_RevLevel*
        Asset_Var_Vol**2/
        (2*Asset_Var_RevRate)
    )

    nu_infty=(
        ((sigma_J2 +
        variance_mean)**0.5 -
        (1/8)*(sigma_J2 +
        variance_mean)**(-3/2)*
        variance_var)**2 -
        sigma_J2
    )

    # calculating parameter a of Section 5.8 of Wiki page
    parameter_a = sigma_J2+sys_vol

    # calculating parameter b of Section 5.8 of Wiki page
    parameter_b =-(sigma_J2+nu_infty)**0.5
    
    # 3. calculate negative IV
    
    IV = factor_loadings[iv_column].astype(float)
    Lv = factor_loadings['LevelBeta'].astype(float)

    def thresholdFcn(y):
        return (IV.add(c_L*Lv*((parameter_a + y)**0.5 + parameter_b))*-1)/beta_2

    pct_range = [i * step_size for i in range(1,100)]
    actual_pd = pd.DataFrame()
    for p in pct_range:
        actual_pd[p] = step_size * thresholdFcn(gamma.ppf(p, a=gamma_k, scale=gamma_theta)).apply(norm.cdf)

    cumulative_pd = actual_pd.sum(axis=1)

    probability_of_negative_IV = cumulative_pd.max()
    
    # Return the used derived constants
    udc = {
        'gamma_k':gamma_k,
        'gamma_theta':gamma_theta,        
        'sigma_J2':sigma_J2,
        'sys_vol': sys_vol,
        'variance_mean': variance_mean,
        'variance_var': variance_var,
        'nu_infty':nu_infty,
        'parameter_a': parameter_a,
        'parameter_b': parameter_b        
    }
    
    return probability_of_negative_IV, udc
    
def eoiv_tool(model_dict):
    """ A "sorter" style tool that produces a valid 'Assets.EQ.PEA.RWOIV' model as its sole output model. This is compiled from the input Models passed in a 'model_dict' of compiled models. In addition to the 'Assets.EQ.PEA.RWOIV' model parameters, we also calculate the expected maximum negative rate probablities based on the current and unconditional IV surfaces.  

    Args: 
        model_dict: dictionary. A dictionary representation of "input" models to a tool. The "anchored" model names are the keys in the dictionary, and the returned values are string representations of the Model JSON for each model. 

    Returns:

        An output dictionary of "anchored" model names and Model JSON values. The dictionary contains a single key 'Output'. This can be pushed as a valid 'Assets.EQ.PEA.RWOIV' model.
               
    """      
    # Extract model dictionary to a model-parameter dictionary
    model_params = {k:utility_model_json_to_model_dict(model_dict[k]) for k in model_dict}
    
    # Get settings values
    c_L = float(model_params['Settings']['ScalingFactor'])
    apply_smoothing = bool(model_params['Settings']['ApplySmoothing'])
    
    # The parameters can then be read from the dictionary, and converted to data types for use in python (tables or single values)
    raw_data = pd.DataFrame.from_dict(model_params['InitialIV']["Equity.ImpliedVol"])
    # Data cleaning
    raw_data = raw_data[['term','strike','value']]
    raw_data.columns = ['Maturity','Strike','InitialIV']
    raw_data[['Maturity','Strike']] = raw_data[['Maturity','Strike']].apply(pd.to_numeric)
    raw_data = raw_data.dropna() # As we have gaps here, from the XLS way we compile the final IV
    raw_data = raw_data.set_index(['Maturity','Strike'])

    RWOIV_Betas = pd.DataFrame.from_dict(model_params['RWOIV.Betas']["FactorLoadings"])
    # Data cleaning
    RWOIV_Betas = RWOIV_Betas[['maturity','strike','ivInf','levelBeta','skewBeta','kurtosisBeta','termStructureBeta']]
    RWOIV_Betas.columns = ['Maturity','Strike','IVInf','LevelBeta','SkewBeta','KurtosisBeta','TermStructureBeta']
    RWOIV_Betas[['Maturity','Strike']] = RWOIV_Betas[['Maturity','Strike']].apply(pd.to_numeric)
    RWOIV_Betas = RWOIV_Betas.dropna() # no missing values expected
    RWOIV_Betas = RWOIV_Betas.set_index(['Maturity','Strike'])

    factor_loadings = pd.concat([raw_data,RWOIV_Betas], axis=1)
    
    # If smoothing is used, then replace in the factor loadings 
    if apply_smoothing:
        skt_smoothed = skt_smoothing(factor_loadings)        
        factor_loadings['SkewBeta'] = skt_smoothed['SmooSkewBeta']
        factor_loadings['KurtosisBeta'] = skt_smoothed['SmooKurtosisBeta']
        factor_loadings['TermStructureBeta'] = skt_smoothed['SmooTermStructureBeta']

    # Convert to a suitable table for parameter export
    factor_loadings_parameter = factor_loadings.reset_index().sort_values(['Maturity','Strike'])
    factor_loadings_parameter['_index'] = factor_loadings_parameter.index + 1
    factor_loadings_parameter
    
    # Calculate default probability at given scaling factor       
    
    PONIV_IVInf, constants = probability_of_negative_IV(c_L, model_params, factor_loadings, iv_column='IVInf', step_size = 1/100)
    PONIV_IV_InitialIV, _ = probability_of_negative_IV(c_L, model_params, factor_loadings, iv_column='InitialIV', step_size = 1/100)
    
    constants_parameter = pd.Series(constants, name='Value').rename_axis('Name').reset_index().to_dict('records')
    
    output_model = {
        "FactorLoadings": factor_loadings_parameter,
        'SigmaInf': model_params['RWOIV.Static']['SigmaInf'],
        'Skew.Alpha': model_params['RWOIV.Static']['Skew.Alpha'],
        'Skew.Sigma': model_params['RWOIV.Static']['Skew.Sigma'],
        'Skew.Mu': model_params['RWOIV.Static']['Skew.Mu'],
        'Skew.StartVal': model_params['RWOIV.Static']['Skew.StartVal'],
        'Kurtosis.Alpha': model_params['RWOIV.Static']['Kurtosis.Alpha'],
        'Kurtosis.Sigma': model_params['RWOIV.Static']['Kurtosis.Sigma'],
        'Kurtosis.Mu': model_params['RWOIV.Static']['Kurtosis.Mu'],
        'Kurtosis.StartVal': model_params['RWOIV.Static']['Kurtosis.StartVal'],
        'TermStructure.Alpha': model_params['RWOIV.Static']['TermStructure.Alpha'],
        'TermStructure.Sigma': model_params['RWOIV.Static']['TermStructure.Sigma'],
        'TermStructure.Mu': model_params['RWOIV.Static']['TermStructure.Mu'],
        'TermStructure.StartVal': model_params['RWOIV.Static']['TermStructure.StartVal'],
        'Level.JumpVol':0,
        'Level.LevelScaling':c_L,
        'Level.LevelDisplacement':0,
        'Level.Alpha': model_params['F1.SVJD']['BE_SVJD_E_Var_RevRate_F1'],
        'Prob.NegativeIV.DerivedConstants': constants_parameter,
        'Prob.NegativeIV.IVInf':PONIV_IVInf,
        'Prob.NegativeIV.InitialIV':PONIV_IV_InitialIV
    }

    # Return Models Dictionary
    outputs_dict = {
        'Output': utility_model_dict_to_model_json(output_model)
        }

    outputs_json = json.dumps(outputs_dict)

    return outputs_json