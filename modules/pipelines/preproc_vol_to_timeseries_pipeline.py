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
import numpy as np
from nilearn.signal import clean
import time
from collections import OrderedDict
from nilearn.signal import _detrend
from pathlib import Path

#############################################################################################
# FUNCTIONS
#############################################################################################

def preproc_vol_to_timeseries(whole_timeseries, baseline_vols):

    # Preprocessing decoding start time
    preproc_decoding_time = OrderedDict()
    start_preproc_decoding = time.time()

    # Detrend baseline if is not already detrended
    if Path(Exp.preprocessed_dir / 'detrended_baseline.npy').is_file():
        pass
    else:
        detrended_baseline = _detrend(baseline_vols, 
                                      inplace = False, 
                                      type = 'linear', 
                                      n_batches = 10)
        np.save(str(Exp.preprocessed_dir) / 'detrended_baseline.npy', detrended_baseline)

    # Detrending timeseries to last arrived vol of interest
    def detrend_timeseries(whole_timeseries):
        timeseries_to_volofinterest = whole_timeseries.copy()
        detrended_timeseries = _detrend(timeseries_to_volofinterest, inplace = False, type = 'linear', n_batches = 10)
        detrended_vol_of_interest = detrended_timeseries[-1].reshape(1, -1)
        return detrended_vol_of_interest

    start_detrending = time.time()
    detrended_vol_of_interest = detrend_timeseries(whole_timeseries)
    preproc_decoding_time['detrending_time'] = time.time() - start_detrending

    # Normalize vol of interest with respect to detrended baseline
    def zscore_func(detrended_vol_of_interest, baseline_detrended):
        zscored_vols = np.vstack([baseline_detrended, detrended_vol_of_interest]) # Append vol to baseline_vols 
        zscored_vols = clean(signals = zscored_vols, # Time-series normalization
                             standardize = 'zscore',
                             detrend = False,
                             ensure_finite = True,
                            )
        zscored_vol_of_interest = zscored_vols[-1].reshape(1, -1) # Extract z-zscored vol of interest
        return zscored_vol_of_interest

    start_zscoring = time.time()
    zscored_vol_of_interest = zscore_func(detrended_vol_of_interest, baseline_detrended)
    preproc_decoding_time['zscoring_time'] = time.time() - start_zscoring

    # Preprocessing decoding end time
    preproc_decoding_time['total_preproc_decoding_time'] = time.time() - start_preproc_decoding

    return zscored_vol_of_interest, preproc_decoding_time