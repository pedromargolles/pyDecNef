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

from collections import OrderedDict
from joblib import load
import numpy as np
from sklearn.linear_model import LogisticRegression
import time
from typing import Tuple

#############################################################################################
# DESCRIPTION
#############################################################################################

# Decoding pipeline to be applied in real-time on each trial data

#############################################################################################
# FUNCTIONS
#############################################################################################

def average_hrf_peak_vols_decoding(preproc_vols_data: list, model_file: str, ground_truth: int) -> Tuple[np.array, list]:

    """ 
    Average volumes within a trial HRF peak before decoding a single averaged volume to increase signal-to-noise ratio

    Steps:

        1 - Load model
        2 - Average volumes of interest (i.e., volumes within HRF peak) onto a single volume
        3 - Predict class probabilities over this trial averaged volume
        4 - Get probability of decoding ground truth class

    Inputs:

        preproc_vols: masked and preprocessed volumes (List of Numpy arrays. Each array has following dimensions: 1, n_voxels)
        model_file: pretrained model (ex., a classifier) in a Region Of Interest (Have to match with mask_file)
        ground_truth: as integer. Target class position in model probabilities predictions tuple.
        
    Returns:

        decoding_prob: probability of decoding ground truth of averaged HRF volume (Float)
        decoding_time: processing time for each decoding pipeline step (List)
    """

    # Decoding start time
    decoding_time = OrderedDict()

    # Load pretrained model
    model_file = str(model_file)
    clf_fit = load(model_file)
    start_decoding = time.time()

    # First, average vols within HRF peak
    start_average_vols = time.time()
    average_preproc = np.average(preproc_vols_data, axis = 0) # Average HRF peak vols
    average_preproc = average_preproc.reshape(1, -1) # Reshape so averaged array has (1, n_voxels) dimensions
    decoding_time['average_vols_time'] = time.time() - start_average_vols
     
    # Predict class probability
    start_prediction = time.time()
    class_probabilities = clf_fit.predict_proba(average_preproc) # Predict class probabilities over this trial averaged vol
    decoding_prob = class_probabilities[0][ground_truth] # Select the probability corresponding to the ground truth
    decoding_time['prediction_time'] = time.time() - start_prediction

    # Decoding end time
    decoding_time['total_decoding_time'] = time.time() - start_decoding
    decoding_time = [decoding_time] # Convert dict to a list to store all times in a pandas dataframe

    return decoding_prob, decoding_time



def average_probs_decoding(preproc_vols_data: list, model_file: str, ground_truth: int) -> Tuple[np.array, list]:

    """
    Average decoding probabilities of volumes within a trial HRF peak

    Steps:

        1 - Load model
        2 - Predict class probabilities for each HRF peak volume
        3 - Get probability of decoding ground truth class for each HRF peak volume
        4 - Average probabilities of decoding ground truth across volumes

    Inputs:

        preproc_vols: masked and preprocessed volumes (List of Numpy arrays. Each array has following dimensions: 1, n_voxels)
        model_file: pretrained model (ex., a classifier) in a Region Of Interest (Have to match with mask_file)
        ground_truth: as integer. Target class position in model probabilities predictions tuple.
        
    Returns:

        averaged_decoding_prob: averaged decoding probability across HRF volumes (Float)
        vols_decoding_probs: decoding probability for each independent volume within HRF peak (Float)
        decoding_time: processing time for each decoding pipeline step (List)
    """

    # Decoding start time
    decoding_time = OrderedDict()

    # Load pretrained model
    model_file = str(model_file)
    clf_fit = load(model_file)

    start_decoding = time.time()
    start_decoding_vols = time.time()
    vols_decoding_probs = [] # To store each HRF peak vol ground truth decoding probability
        
    # Iterate over all preprocessed volumes within HRF peak
    for vol in preproc_vols_data:
        # Predict class probability
        class_probabilities = clf_fit.predict_proba(vol) # Predict class probabilities for each vol
        decoding_prob = class_probabilities[0][ground_truth] # Select the probability corresponding to the ground truth
        vols_decoding_probs.append(decoding_prob) # Append decoding probability to list of decoding probabilities for each vol
        
    averaged_decoding_prob = np.average(vols_decoding_probs) # Average probabilities of decoding ground truth across volumes
    decoding_time['decoding_vols_time'] = time.time() - start_decoding_vols

    # Decoding end time
    decoding_time['total_decoding_time'] = time.time() - start_decoding
    decoding_time = [decoding_time] # Convert dict to a list to store all times in a pandas dataframe

    return averaged_decoding_prob, vols_decoding_probs, decoding_time



def dynamic_decoding(preproc_vol: np.array, model_file: str, ground_truth: int)  -> Tuple[np.array, list]:

    """
    Decode a single volume. In dynamic decoding, all volumes within a trial HRF peak, will be decoded independently and 
    sent individually to experimental software as feedback.

    Steps:

        1 - Load model
        2 - Predict class probabilities of a preprocessed volume
        3 - Get probability of decoding ground truth class for a preprocessed volume

    Inputs:

        preproc_vol: a single masked and preprocessed fMRI volume data (Array with following dimensions: 1, n_voxels)
        model_file: pretrained model (ex., a classifier) in a Region Of Interest (Have to match with mask_file)
        ground_truth: as integer. Target class position in model probabilities predictions tuple.
   
    Returns:

        decoding_prob: probability of decoding ground truth in preproc_vol
        decoding_time: processing time for each decoding pipeline step (List)
    """

    # Decoding start time
    decoding_time = OrderedDict()

    # Load pretrained model
    model_file = str(model_file)
    clf_fit = load(model_file)

    start_decoding = time.time()

    # Predict class probability
    start_prediction = time.time()
    class_probabilities = clf_fit.predict_proba(preproc_vol) # Predict class probabilities of last HRF peak volume
    decoding_prob = class_probabilities[0][ground_truth] # Select the probability corresponding to the ground truth
    decoding_time['prediction_time'] = time.time() - start_prediction

    # Decoding end time
    decoding_time['total_decoding_time'] = time.time() - start_decoding
    decoding_time = [decoding_time] # Convert dict to a list to store all times in a pandas dataframe

    return decoding_prob, decoding_time



def decode_trial(this_trial, model_file: str, ground_truth: int, decoding_procedure: str) -> Tuple[np.array, list, list]:

    """ 
    Apply a decoding pipeline as a function of decoding procedure and assign results to respective vols/trials 
    
    Inputs:

        this_trial: new_trial object containing all volumes within HRF peak and trial related information
        model_file: pretrained model (ex., a classifier) in a Region Of Interest (Have to match with mask_file)
        ground_truth: as integer. Target class position in model probabilities predictions tuple.
        decoding_procedure: decoding procedure which will be applied at trial level

    Returns:

        decoding_probability: decoded probability across last trial/vol
    """

    if decoding_procedure == 'average_hrf_peak_vols':

        preproc_vols_data = [vol.data for vol in this_trial.HRF_peak_vols] # Get data arrays from every volume within HRF peak
        trial_decoding_prob, trial_decoding_time = average_hrf_peak_vols_decoding(preproc_vols_data, model_file, ground_truth) # Average HRF peak volumes arrays onto a single volume and decode it
        return trial_decoding_prob, None , trial_decoding_time

    elif decoding_procedure == 'average_probs':

        preproc_vols_data = [vol.data for vol in this_trial.HRF_peak_vols] # Get data arrays from every volume within HRF peak
        trial_decoding_prob, vols_decoding_probs, trial_decoding_time = average_probs_decoding(preproc_vols_data, model_file, ground_truth) # Decode each HRF peak volume and then average decoding probabilities
        return trial_decoding_prob, vols_decoding_probs, trial_decoding_time

    elif decoding_procedure == 'dynamic':
        
        preproc_vol = this_trial.HRF_peak_vols[-1].data # Get data array from last volume within HRF peak
        vol_decoding_prob, vol_decoding_time = dynamic_decoding(preproc_vol, model_file, ground_truth)
        return vol_decoding_prob, vol_decoding_time
        