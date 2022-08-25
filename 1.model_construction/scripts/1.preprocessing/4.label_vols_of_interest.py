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

import pandas as pd
from pathlib import Path
from nilearn.image import load_img, index_img

#############################################################################################
# DESCRIPTION
#############################################################################################

# Label volumes of interest from model construction session by using logs files generated
# by your experimental software. This script requires customization to match your experimental
# needs and conditions.

#############################################################################################
# SETUP VARIABLES
#############################################################################################

# Relevant variables to extract volumes of interest in the model construction session
n_heatup_vols = 5 # Number of fumctional volumes to consider as heatup volumes used for image
                  # stabilization of MRI scanner
TR = 2000 # MRI Repetition time. Volumes sampling rate (in miliseconds)
HRF_peak_onset = 5000 # H.R.F. peak threshold onset (miliseconds from trial onset).
HRF_peak_offset = 18000 #  H.R.F. peak threshold offset (miliseconds from trial onset).

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
raw_dir = exp_dir / 'data'
func_logs_dir = raw_dir / 'logs'
preprocessed_dir = exp_dir / 'preprocessed/'
preprocessed_func_dir = preprocessed_dir / 'preprocessed_func'
labeled_dir = preprocessed_dir / 'labeled_vols_of_interest'

# Create dirs
labeled_dir.mkdir(exist_ok = True, parents = True)

#############################################################################################
# MATCH FUNCTIONAL DATA TO EXPERIMENTAL LOG
#############################################################################################

# List preprocessed functional data for each fMRI run
func_files = sorted([file for file in preprocessed_func_dir.glob('**/*.nii.gz')])
# List functional data log files for each fMRI run
logs_files = sorted([csv for csv in func_logs_dir.glob('*.csv')])
# Match functional data and logs
runs_data = zip(func_files, logs_files)

#############################################################################################
# LOCATE AND LABEL VOLUMES OF INTEREST IN FUNCTIONAL DATA TIMESERIES FOR EACH RUN
#############################################################################################

for func_file, log_file in runs_data: # For each run
    
    # Get run name
    func_parent = func_file.parent
    func_name = func_parent.name # Get this run name
    
    # Set Pathlib paths as strings to avoid NiLearn errors
    func_file = str(func_file)
    log_file = str(log_file)
    print(func_file, log_file)
    
    # Remove heatup vols from MRI data
    nii_data = load_img(func_file)
    nii_data = index_img(nii_data, slice(n_heatup_vols, None))

    # Remove heatup vols times from log file
    run_log = pd.read_csv(log_file, usecols=['trial_onset', 'concept'])
    run_log['trial_onset'] -= (TR * n_heatup_vols) # Remove heatup duration from trials onset times
    run_log['trial_idx'] = run_log.index # Create trial index column
    run_log.drop(run_log.tail(1).index, inplace = True) # Remove last row as it was only inserted
                                                        # into logs files to track run's total 
                                                        # duration

    # Set next volume after heatup as the new run start time (i.e., time 0)
    # Then, create new functional data timestamps increasing at TR increments by each volume
    onset_time = 0
    new_timestamps = []
    for i in range(nii_data.shape[-1]):
        new_timestamps.append(onset_time)
        onset_time += TR

    # Encode labels for model construction 
    category = []
    for value in run_log['concept'].values: # For each stimuli category in 'concept' column
        try:
            if ('non_living' in value): # If trial belongs to 'non_living' category, then label = 0
                category.append(0)
            elif ('living' in value): # If trial belongs to 'living' category, then label = 1
                category.append(1)
            else:
                category.append(2) # If trial doesn't belong neither 'non_living' nor 'living' categories then label = 2
        except:
            category.append('nan') 
    run_log['trial_category'] = category
    
    # Stablish trials intervals of interest (normally H.R.F. peaks) by using trials onsets and set thresholds
    run_log['HRF_peak_onset'] = run_log['trial_onset'] + HRF_peak_onset
    run_log['HRF_peak_offset'] = run_log['trial_onset'] + HRF_peak_offset
    
    # Label functional volumes of interest using specified trials intervals of interest
    vol_of_interest_idx = []
    vol_of_interest_time = []
    trial_idx = []
    trial_category = []
    trial_onset = []
    trial_HRF_peak_onset = []
    trial_HRF_peak_offset = []
    for vol_idx, timestamp in enumerate(new_timestamps): # For each timestamp
        for row in run_log.iterrows(): # For each trial specified in log file
            row = row[1] # Get row values (and not row index)
            if row['HRF_peak_onset'] <= timestamp <= row['HRF_peak_offset']: # If this volume timestamp is within interval of interest

                vol_of_interest_idx.append(vol_idx) # Append volume index to a list. This index will be then used to extract volume of interest from timeseries 
                                                     # while preprocessing data for model construction
                vol_of_interest_time.append(timestamp)  # Append volume timestamp to a list

                trial_idx.append(row['trial_idx']) # Append the trial this volume belongs to in a list
                trial_category.append(row['trial_category']) # Append stimuli category for model construction to a list
                trial_onset.append(row['trial_onset']) # Append trial onset time to a list
                trial_HRF_peak_onset.append(row['HRF_peak_onset']) # Trial H.R.F. peak onset
                trial_HRF_peak_offset.append(row['HRF_peak_offset']) # Trial H.R.F. peak offset    

    # Create a new dataframe containing information relative to volumes of interest in this run
    df_vols_of_interest = {'vol_idx': vol_of_interest_idx,
                           'vol_time': vol_of_interest_time,
                           'trial_idx': trial_idx,
                           'trial_category': trial_category,
                           'trial_onset': trial_onset,
                           'hrf_peak_onset': trial_HRF_peak_onset,
                           'hrf_peak_offset': trial_HRF_peak_offset,
                           'run': func_name,
                          }
    
    df_vols_of_interest = pd.DataFrame(df_vols_of_interest)
    
    # Save whole co-registered functional volumes timeseries (without heatup volumes)
    nii_data.to_filename(str(labeled_dir / (func_name + '.nii.gz')))
    
    # Extract labeled volumes of interest information
    df_vols_of_interest.to_csv(str(labeled_dir / (func_name + '_vols_of_interest.csv')))