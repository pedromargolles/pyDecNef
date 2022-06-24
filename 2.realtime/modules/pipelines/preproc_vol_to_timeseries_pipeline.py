############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021, Python fMRI-Neurofeedback
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: 
############################################################################

#############################################################################################
# IMPORT DEPENDENCIES
#############################################################################################

from modules.config.exp_config import Exp
from collections import OrderedDict
from nilearn.signal import clean, _detrend
import numpy as np
from pathlib import Path
import time
from typing import Tuple

#############################################################################################
# DESCRIPTION
#############################################################################################

# Preprocess each volume in real-time before decoding by using timeseries data to that moment 

#############################################################################################
# FUNCTIONS
#############################################################################################

def preproc_vol_to_timeseries(whole_timeseries: np.array, baseline_vols: np.array, preprocessed_dir: str) -> Tuple[np.array, list]:

    """
    Preprocess last corregistered volume before decoding by using timeseries data to that moment 

    Steps:

        1 - Detrend baseline
        2 - Detrend volume using timeseries data to that volume
        3 - Zscore detrended volume using detrended baseline data

    Inputs:

        whole_timeseries: all corregistered fMRI volumes in a Region Of Interest so far, including last corregistered volume as last volume (Stacked Numpy Array: n_vols, n_voxels)
        baseline_vols: all corregistered baseline volumes in a Region Of Interest (Stacked Numpy Array: n_vols, n_voxels)
        preprocessed_dir: Path where 'preprocessed' folder for this participant will be created

    Returns:

        preprocessed_vol: Already detrended and zscored volume (Numpy Array)
        preproc_time: Processing time of each preprocessing pipeline step (List)
    """

    # Preprocessing start time
    preproc_time = OrderedDict()
    start_preproc = time.time()

    # Ensure preprocessed_dir path is string type
    #preprocessed_dir = str(preprocessed_dir)

    # Detrend baseline if is not already detrended
    start_baseline_detrending = time.time()
    if Path(preprocessed_dir / 'detrended_baseline.npy').is_file():
        detrended_baseline = np.load(preprocessed_dir / 'detrended_baseline.npy') # Load detrended baseline
    else:
        detrended_baseline = _detrend(baseline_vols, # Independently detrend baseline vols to then perform vols of interest zscoring normalization 
                                      inplace = False, 
                                      type = 'linear', # Linear detrending
                                      n_batches = 10)
        np.save(preprocessed_dir / 'detrended_baseline.npy', detrended_baseline) # Save detrended baseline
    preproc_time['baseline_detrending'] = time.time() - start_baseline_detrending

    # Detrend timeseries to last arrived vol of interest
    def detrend_timeseries(whole_timeseries):
        timeseries_to_volofinterest = whole_timeseries.copy()
        detrended_timeseries = _detrend(timeseries_to_volofinterest, # Detrend timeseries to last arrived vol of interest
                                        inplace = False, 
                                        type = 'linear', # Linear detrending
                                        n_batches = 10)
        detrended_vol_of_interest = detrended_timeseries[-1].reshape(1, -1) # Extract just detrended vol of interest
        return detrended_vol_of_interest

    start_detrending = time.time()
    detrended_vol_of_interest = detrend_timeseries(whole_timeseries)
    preproc_time['detrending_time'] = time.time() - start_detrending

    # Normalize vol of interest with respect to detrended baseline
    def zscore_func(detrended_vol_of_interest, detrended_baseline):
        zscored_vols = np.vstack([detrended_baseline, detrended_vol_of_interest]) # Append vol of interest to baseline_vols 
        zscored_vols = clean(signals = zscored_vols, # Normalize detrended baseline + vol of interest
                             standardize = 'zscore', # Zscoring normalization
                             detrend = False,
                             ensure_finite = True,
                            )
        zscored_vol_of_interest = zscored_vols[-1].reshape(1, -1) # Extract just z-zscored vol of interest
        return zscored_vol_of_interest

    start_zscoring = time.time()
    zscored_vol_of_interest = zscore_func(detrended_vol_of_interest, detrended_baseline)
    preproc_time['zscoring_time'] = time.time() - start_zscoring

    # Preprocessing end time
    preproc_time['total_preproc_decoding_time'] = time.time() - start_preproc
    preproc_time = [preproc_time]

    # Preprocessed vol
    preprocessed_vol = zscored_vol_of_interest

    return preprocessed_vol, preproc_time