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

from nilearn.signal import clean
from sklearn.linear_model import LogisticRegression
from collections import OrderedDict
from joblib import load
import numpy as np
import time

#############################################################################################
# FUNCTIONS
#############################################################################################

def decode_trial_vols(preproc_vols, 
                      model_file,
                      ground_truth, 
                      decoding_procedure):

    """
    Inputs:
    preproc_vol: preprocessed fMRI volume
    model_file: pretrained model path for preprocessed ROI
    scaler_file: scaler fitted on training data
    ground_truth: As integer. Decoding target

    Returns:
    decoding_prob: Probability of decoding ground_truth target
    """

    # Decoding start time
    decoding_time = OrderedDict()
    start_decoding = time.time()
    model_file = str(model_file)
    clf_fit = load(model_file) # Load pretrained logistic regression with 'l2' regularization

    if decoding_procedure == 'average_hrf_peak_vols':

        # Average vols of interest
        start_average_vols = time.time()
        average_zscored = np.average(preproc_vols, axis = 0) # Average HRF peak vols
        average_zscored = average_zscored.reshape(1, -1) # Reshape so averaged array has (1, n_voxels) dimensions
        decoding_time['average_vols_time'] = time.time() - start_average_vols
     
        # Predict class
        start_prediction = time.time()
        class_probabilities = clf_fit.predict_proba(average_zscored) # Predict class probabilities over this trial averaged vols
        decoding_prob = class_probabilities[0][ground_truth] # Select probability corresponding to this trial ground truth
        decoding_time['prediction_time'] = time.time() - start_prediction

        # Decoding end time
        decoding_time['total_decoding_time'] = time.time() - start_decoding
        decoding_time = [decoding_time] # Convert dict to list to store all times in a pandas dataframe

        return decoding_prob, decoding_time

    if decoding_procedure == 'average_probs':

        start_decoding_vols = time.time()
        decoding_probs = [] # Each HRF peak vol ground truth decoding probability
        
        # Iterate over preprocessed vols
        for zscored_vol in preproc_vols:
            # Predict vol class
            class_probabilities = clf_fit.predict_proba(zscored_vol) # Predict class probabilities over this vol
            decoding_prob = class_probabilities[0][ground_truth] # Select probability corresponding to this trial ground truth
            decoding_probs.append(decoding_prob) # Append decoding probability to list of decoding probabilities of vols within a trial
        
        averaged_decoding_prob = np.average(decoding_probs)
        decoding_time['decoding_vols_time'] = time.time() - start_decoding_vols

        # Decoding end time
        decoding_time['total_decoding_time'] = time.time() - start_decoding
        decoding_time = [decoding_time] # Convert dict to list to store all times in a pandas dataframe

        return averaged_decoding_prob, decoding_time, decoding_probs