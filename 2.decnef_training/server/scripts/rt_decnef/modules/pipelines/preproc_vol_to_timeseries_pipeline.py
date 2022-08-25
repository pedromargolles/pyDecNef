#############################################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
#############################################################################################

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

def preproc_to_baseline(whole_timeseries: np.array, baseline_vols: np.array, preprocessed_dir: str) -> Tuple[np.array, list]:

    """
    Preprocess last corregistered volume before decoding by using unpreprocessed timeseries data to that moment and baselines volumes

    Steps:

        1 - Independently detrend unpreprocessed baseline
        2 - Detrend volume using unpreprocessed timeseries data to that volume
        3 - Zscore detrended volume using detrended baseline data

    Inputs:

        whole_timeseries: All unpreprocessed and corregistered fMRI volumes in a Region Of Interest so far, including last corregistered volume (Stacked Numpy Array: n_vols, n_voxels)
        baseline_vols: All unpreprocessed and corregistered baseline volumes in a Region Of Interest (Stacked Numpy Array: n_vols, n_voxels)
        preprocessed_dir: Preprocessed volumes folder

    Returns:

        last_zscored_vol: Already detrended and zscored volume (Numpy Array)
        preproc_time: Processing time of each preprocessing pipeline step (List)
    """

    # Preprocessing start time
    preproc_time = OrderedDict()
    start_preproc = time.time()

    # Detrend baseline if is not already detrended
    start_baseline_detrending = time.time()
    if Path(preprocessed_dir / 'detrended_baseline.npy').is_file():
        detrended_baseline = np.load(preprocessed_dir / 'detrended_baseline.npy') # Load detrended baseline
    else:
        detrended_baseline = _detrend(baseline_vols, # Independently detrend baseline vols to then perform zscoring normalization 
                                      inplace = False, 
                                      type = 'linear', # Linear detrending
                                      n_batches = 10)
        np.save(preprocessed_dir / 'detrended_baseline.npy', detrended_baseline) # Save detrended baseline
    preproc_time['baseline_detrending'] = time.time() - start_baseline_detrending

    # Detrend timeseries to last arrived vol
    def detrend_timeseries(whole_timeseries):
        timeseries_to_last_vol = whole_timeseries.copy()
        detrended_timeseries = _detrend(timeseries_to_last_vol, # Detrend timeseries to last arrived volume
                                        inplace = False, 
                                        type = 'linear', # Linear detrending
                                        n_batches = 10)
        last_detrended_vol = detrended_timeseries[-1].reshape(1, -1) # Extract just last detrended volume
        return last_detrended_vol

    start_detrending = time.time()
    last_detrended_vol = detrend_timeseries(whole_timeseries)
    preproc_time['detrending_time'] = time.time() - start_detrending

    # Normalize last_detrended_vol with respect to independently detrended baseline
    def zscore_func(last_detrended_vol, detrended_baseline):
        zscored_vols = np.vstack([detrended_baseline, last_detrended_vol]) # Append last_detrended_vol to detrended baseline_vols 
        zscored_vols = clean(signals = zscored_vols, # Normalize detrended baseline + last detrended volume
                             standardize = 'zscore', # Zscoring normalization
                             detrend = False, # Volumes are already detrended, just zscoring
                             ensure_finite = True,
                            )
        last_zscored_vol = zscored_vols[-1].reshape(1, -1) # Extract just last zscored volume
        return last_zscored_vol

    start_zscoring = time.time()
    last_zscored_vol = zscore_func(last_detrended_vol, detrended_baseline)
    preproc_time['zscoring_time'] = time.time() - start_zscoring

    # Preprocessing end time
    preproc_time['total_preproc_decoding_time'] = time.time() - start_preproc
    preproc_time = [preproc_time]

    return last_zscored_vol, preproc_time



def preproc_to_timeseries(whole_timeseries: np.array) -> Tuple[np.array, list]:

    """
    Preprocess last corregistered volume before decoding by using unpreprocessed timeseries data to that moment 

    Steps:

        1 - Detrend and zscore volume using unpreprocessed timeseries data to that volume

    Inputs:

        whole_timeseries: All unpreprocessed and corregistered fMRI volumes in a Region Of Interest so far, including last corregistered volume (Stacked Numpy Array: n_vols, n_voxels)

    Returns:

        last_zscored_vol: Already detrended and zscored volume (Numpy Array)
        preproc_time: Processing time of each preprocessing pipeline step (List)
    """

    # Preprocessing start time
    preproc_time = OrderedDict()
    start_preproc = time.time()

    # Detrend and zscore last volume using timeseries to that volume
    start_zscoring = time.time()

    zscored_vols = clean(signals = whole_timeseries, # Unpreprocessed timeseries to last arrived volume
                         standardize = 'zscore', # Zscoring normalization
                         detrend = True, # Linear detrending 
                         ensure_finite = True,
                        )

    last_zscored_vol = zscored_vols[-1].reshape(1, -1) # Extract last zscored volume
    preproc_time['zscoring_time'] = time.time() - start_zscoring

    # Preprocessing end time
    preproc_time['total_preproc_decoding_time'] = time.time() - start_preproc
    preproc_time = [preproc_time]

    return last_zscored_vol, preproc_time



def preproc_to_model_session(whole_timeseries: np.array, zscoring_mean: str, zscoring_std: str) -> Tuple[np.array, list]:
   
    """
    Preprocess last corregistered volume before decoding by using timeseries data to that moment and model construction data mean and std

    Steps:

        1 - Detrend volume using unpreprocessed timeseries data to that volume
        2 - Zscore detrended volume using mean and std from model construction session

    Inputs:

        whole_timeseries: All unpreprocessed and corregistered fMRI volumes in a Region Of Interest so far, including last corregistered volume (Stacked Numpy Array: n_vols, n_voxels)
        zscoring_mean: Numpy array containing mean of model construction session data (Numpy array: n_voxels, )
        zscoring_std: Numpy array containing standard deviation of model construction session data (Numpy array: n_voxels, )

    Returns:

        last_zscored_vol: Already detrended and zscored volume (Numpy Array)
        preproc_time: Processing time of each preprocessing pipeline step (List)
    """

    # Preprocessing start time
    preproc_time = OrderedDict()
    start_preproc = time.time()

    # Load zscoring data
    zscoring_mean = np.load(zscoring_mean)
    zscoring_std = np.load(zscoring_std)

    # Detrending timeseries to last volume
    def detrend_func(whole_timeseries):
        timeseries_including_last_vol = whole_timeseries.copy()
        detrended_timeseries = _detrend(timeseries_including_last_vol, # Linear detrending
                                        inplace = False, 
                                        type = 'linear', 
                                        n_batches = 10)
        detrended_last_vol = detrended_timeseries[-1].reshape(1, -1)
        return detrended_last_vol

    start_detrending = time.time()
    detrended_last_vol = detrend_func(whole_timeseries)
    preproc_time['detrending_time'] = time.time() - start_detrending

    # Normalize last detrended volume using previous session data mean and std
    def zscore_func(detrended_last_vol, zscoring_mean, zscoring_std):
        last_zscored_vol = (detrended_last_vol - zscoring_mean) / zscoring_std
        return last_zscored_vol
    
    start_zscoring = time.time()
    last_zscored_vol = zscore_func(detrended_last_vol, zscoring_mean, zscoring_std)
    preproc_time['zscoring_time'] = time.time() - start_zscoring
    
    # Total detrending and zscoring time
    preproc_time['total_preproc_time'] = time.time() - start_preproc

    return last_zscored_vol, preproc_time

