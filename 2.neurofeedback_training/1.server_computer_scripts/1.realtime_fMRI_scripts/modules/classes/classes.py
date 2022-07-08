############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
############################################################################

from modules.config import shared_instances
from modules.config.exp_config import Exp
from modules.pipelines.corregistration_pipeline import corregister_vol
from modules.pipelines.preproc_vol_to_timeseries_pipeline import preproc_to_baseline, preproc_to_timeseries, preproc_to_model_session
from modules.pipelines.decoding_pipeline import average_hrf_peak_vols_decoding, average_probs_decoding, dynamic_decoding
from modules.config import shared_instances
from colorama import init, Fore
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import sys
import threading
import time

#############################################################################################
# VOLUME CLASS
#############################################################################################

# Object containing all information relative to each volume (timings, indexes, type, file path, preprocessing status...)
# and calls for corregistration and preprocessing fuctions

class Vol(Exp):
    def __init__(self, 
                 vol_idx = None):

        self.vol_idx = vol_idx # Volume index
        self.trial = None # Corresponding trial
        self.vol_time = None # When the volume was detected in the MRI folder?
        self.vol_type = None # Is this a heatup, baseline or task volume?
        self.dicom_file = None # DICOM raw volume file
        self.vol_vs_trial_onset = None # Volume arrival time from last trial onset
        self.in_hrf_peak = False # Whether volume is within last trial HRF peak or not
        self.data = None # Volume already preprocessed data
        self.corregistration_times = None # Time to co-register this volume
        self.preproc_vol_to_timeseries_times = None # Time to preprocess this volume using timeseries information
        self.prepared_4_decoding = False # Is this volume totally preprocessed and prepared for decoding?
        self.decoding_prob = None # Decoding probability at volume level
        self.decoding_time = None # Time to decode this volume

    def preprocessing(self):
        preprocess_vol_thread = threading.Thread(name = 'vol_preprocessing',
                                                 target = self._start_preprocessing,
                                                ) # Preprocess volume in a new thread to avoid blocking main.py volumes filewatcher pipeline 
                                   
        preprocess_vol_thread.start()

    def _start_preprocessing(self):

        """ Volume co-registration (i.e., brain extraction, co-registration to reference volume, ROI masking and smoothing) and
            preprocessing using previous timeseries information """

        self.data, self.corregistration_times = corregister_vol(vol_file = self.dicom_file, # Co-registration of DICOM raw volume file
                                                                mask_file = self.mask_file, # R.O.I. mask file
                                                                ref_vol_file = self.ref_vol_file, # Reference volume from the decoder construction session
                                                                preprocessed_dir = self.preprocessed_dir # Preprocessed volumes output folder
                                                               )

        shared_instances.timeseries.preproc_vol_2_timeseries(self) # Use timeseries object instanced in main.py
                                                                   # Preprocess masked volume using whole timeseries data (i.e., detrending, zscoring, high-pass filtering...)

        self.prepared_4_decoding = True # This task volume is already prepared for decoding
        self._store_vol() # Store preprocessed task volume data as an independent file
       
    def _store_vol(self):
        np.save(Path(self.preprocessed_dir) / f'{Path(self.dicom_file).stem}.npy', self.data, allow_pickle = True) # Store this masked and preprocessed task volume data



#############################################################################################
# TIMESERIES CLASS
#############################################################################################

# Object containing all masked volumes and functions for preprocessing
# (i.e., detrending, zscoring, high-pass filtering) each task volume in relation to previous volumes 
# and baseline

class Timeseries(Exp):
    heatup_vols = np.array([]) # Array to store all masked and unpreprocessed heatup volumes
    baseline_vols = np.array([]) # Array to store all masked and unpreprocessed baseline volumes
    task_vols = np.array([]) # Array to store all masked and unpreprocessed task volumes
    whole_timeseries = np.array([]) # Array to store all masked and unpreprocessed baseline + task volumes

    def preproc_vol_2_timeseries(self, vol):
        self._append_vol(vol) # First, assign this volume to a specific timeseries array (i.e., baseline_vols, task_vols and/or whole_timeseries)
        
        if vol.vol_type == 'task': # Initialize task volumes preprocessing using whole timeseries once baseline ends
            
            if self.zscoring_procedure == 'to_baseline':
                vol.data, vol.preproc_vol_to_timeseries_time = preproc_to_baseline(whole_timeseries = self.whole_timeseries, # Unpreprocessed timeseries to last arrived volume
                                                                                   baseline_vols = self.baseline_vols, # Unpreprocessed baseline vols 
                                                                                   preprocessed_dir = self.preprocessed_dir, # Preprocessed volumes folder
                                                                                  )

            elif self.zscoring_procedure == 'to_timeseries':
                vol.data, vol.preproc_vol_to_timeseries_time = preproc_to_timeseries(whole_timeseries = self.whole_timeseries, # Unpreprocessed timeseries to last arrived volume
                                                                                    )
            
            elif self.zscoring_procedure == 'to_model_session':
                vol.data, vol.preproc_vol_to_timeseries_time = preproc_to_model_session(whole_timeseries = self.whole_timeseries, # Unpreprocessed timeseries to last arrived volume
                                                                                        zscoring_mean = self.zscoring_mean,  # Numpy array containing mean of model construction session data
                                                                                        zscoring_std = self.zscoring_std # Numpy array containing standard deviation of model construction session data
                                                                                       )

    def _append_vol(self, vol):

        """ Stack new masked volume onto baseline_vols, task_vols or whole_timeseries arrays """

        def vol_to_array(timeseries_array, vol):

            """ Append masked volume array to specific array """

            if timeseries_array.shape[0] == 0: # If timeseries array is empty, substitute it with the first masked volume array
                timeseries_array = vol
            else:
                timeseries_array = np.vstack([timeseries_array, vol]) # If timeseries array is not empty then stack new masked and unpreprocessed volume array on top
            return timeseries_array

        if vol.vol_type == 'heatup':
            pass

        elif vol.vol_type == 'baseline':
            self.baseline_vols = vol_to_array(self.baseline_vols, vol.data) # Append to unpreprocessed baseline timeseries array
            np.save(Path(self.preprocessed_dir) / 'unpreprocessed_baseline.npy', self.baseline_vols) # Store baseline timeseries

            self.whole_timeseries = vol_to_array(self.whole_timeseries, vol.data) # Append to baseline + task volumes timeseries array
            np.save(Path(self.preprocessed_dir) / 'unpreprocessed_whole_timeseries.npy', self.whole_timeseries) # Store baseline + task volumes timeseries

        elif vol.vol_type == 'task':
            self.task_vols = vol_to_array(self.task_vols, vol.data) # Append to unpreprocessed task timeseries array
            np.save(Path(self.preprocessed_dir) / 'unpreprocessed_task_vols.npy', self.task_vols) # Store task timeseries

            self.whole_timeseries = vol_to_array(self.whole_timeseries, vol.data) # Append to unpreprocessed baseline + task volumes timeseries array
            np.save(Path(self.preprocessed_dir) / 'unpreprocessed_whole_timeseries.npy', self.whole_timeseries) # Store baseline + task volumes timeseries

        else:
            print(Fore.RED + 'Volume type is not defined.')



#############################################################################################
# TRIAL CLASS
#############################################################################################

# Object containing all information (i.e., timings, indexes, ground truth, stimuli, decoding probability...) 
# relative to each experimental trial and fMRI volumes within them

class Trial(Exp):
    def __init__(self, 
                 trial_idx = None, 
                 trial_onset = None,
                 stimuli = None, 
                 ground_truth = None):

        self.trial_idx = trial_idx # Which index has this trial? (By default None)
        self.trial_onset = trial_onset # When new trial request was registered?
        self.stimuli = stimuli # This trial stimuli
        self.ground_truth = ground_truth # Ground truth label to select target decoding probability (ex., 0, 1, 2...)
        self.vols = [] # Volumes in this trial
        self.HRF_peak_vols = [] # Volumes within HRF peak
        self.n_HRF_peak_vols = 0 # Number of volumes in HRF peak
        self.HRF_peak_end = False # To track whether HRF peak ends with the last volume appended to this trial or should wait
        self.decoding_prob = None # Decoding probability at trial level
        self.decoding_time = None # Time to decode this trial HRF peak volumes
        self.decoding_done = False # It is decoding already completed?

    def assign(self, vol):

        if self.trial_idx != None: # If task volume
            vol.vol_vs_trial_onset = vol.vol_time - self.trial_onset # Calculate volume time difference from trial onset
            self.vols.append(vol) # Append volume to this trial list of vols
            vol.trial = self # Associate volume with this trial
            
            if self.HRF_peak_onset <= vol.vol_vs_trial_onset <= self.HRF_peak_offset: # If this volume is within HRF peak thresholds append also to a specific list for decoding
                vol.in_hrf_peak = True # This volume is within HRF peak
                self.HRF_peak_vols.append(vol) # Append to HRF peak vols list in this Trial instance
                self.n_HRF_peak_vols = len(self.HRF_peak_vols) # Refresh number of volumes within HRF peak

            if (vol.vol_vs_trial_onset + self.TR) > self.HRF_peak_offset: # Predict whether next volume will fall in HRF peak or not
                self.HRF_peak_end = True # If not, collection of HRF peak volumes ends
            
            self._store_trial() # With each new volume backup this trial instance onto a file
        
        else: # If not assigned trial_idx (i.e., heatup & baseline vols)
            self.vols.append(vol)
            vol.trial = self # Associate volume with this trial
            self._store_trial()

        shared_instances.logger.add_vol(vol)        


    def _decode(self):

        if self.decoding_procedure == 'average_probs':
            while (self.HRF_peak_end == False) or (self.HRF_peak_vols[-1].prepared_4_decoding == False): # If decoding signal is received before HRF peak ends or last HRF peak vol is prepared 
                                                                                                         # for decoding, just wait until these conditions happen to start decoding volumes
                time.sleep(0.1) # Just wait until while loop condition is False refreshing var status each 100 ms to avoid cannibalization of system processing resources

            preproc_vols_data = [vol.data for vol in self.HRF_peak_vols] # Get data arrays from every volume within HRF peak
            trial_decoding_prob, vols_decoding_probs, trial_decoding_time = average_probs_decoding(preproc_vols_data = preproc_vols_data, # Masked and preprocessed volumes in HRF peak (list of numpy arrays. Each array has following dimensions: 1, n_voxels)
                                                                                                   model_file = self.model_file, # Pre-trained decoder
                                                                                                   ground_truth = self.ground_truth, # Ground truth label to select target decoding probability (ex., 0, 1, 2...)
                                                                                                  )
            
            shared_instances.server.send(trial_decoding_prob) # Send back decoding probability to client side with server object from main.py
            time.sleep(0.05) # Wait some miliseconds after sending decoding_prob. In that way, different signals will not be sent in the same package of data

            self.decoding_prob = trial_decoding_prob # Assign trial_decoding_prob to this trial
            self.decoding_time = trial_decoding_time  # Assign trial_decoding_time to this trial

            for vol, vol_decoding_prob in zip(self.HRF_peak_vols, vols_decoding_probs): # Update HRF peak volumes objects with decoding information
                vol.decoding_prob = vol_decoding_prob
                shared_instances.logger.update_vol(vol)

            self.decoding_done = True # Update trial status to trigger feedback finalization


        elif self.decoding_procedure == 'average_hrf_peak_vols':
            while (self.HRF_peak_end == False) or (self.HRF_peak_vols[-1].prepared_4_decoding == False): # If decoding signal is received before HRF peak ends or last HRF peak vol is prepared 
                                                                                                         # for decoding, just wait until these conditions happen to start decoding volumes
                time.sleep(0.1) # Just wait until while loop condition is False refreshing var status each 100 ms to avoid cannibalization of system processing resources

            preproc_vols_data = [vol.data for vol in self.HRF_peak_vols] # Get data arrays from every volume within HRF peak
            trial_decoding_prob, trial_decoding_time = average_hrf_peak_vols_decoding(preproc_vols_data = preproc_vols_data, # Masked and preprocessed volumes in HRF peak (list of numpy arrays. Each array has following dimensions: 1, n_voxels)
                                                                                      model_file = self.model_file, # Pre-trained decoder
                                                                                      ground_truth = self.ground_truth, # Ground truth label to select target decoding probability (ex., 0, 1, 2...)
                                                                                     )

            shared_instances.server.send(trial_decoding_prob) # Send back decoding probability to client side with server object from main.py
            time.sleep(0.05) # Wait some miliseconds after sending decoding_prob. In that way, different signals will not be sent in the same package of data

            self.decoding_prob = trial_decoding_prob # Assign trial_decoding_prob to this trial
            self.decoding_time = trial_decoding_time  # Assign trial_decoding_time to this trial

            self.decoding_done = True # Update trial status to trigger feedback finalization


        elif self.decoding_procedure == 'dynamic':
            last_decoded_vol = None # Keep track of last decoded volume instance

            while self.HRF_peak_end == False: # While HRF peak has not ended
                if (len(self.HRF_peak_vols) >= 1) and (self.HRF_peak_vols[-1].prepared_4_decoding == True): # If some volume is already processed and prepared_4_decoding
                    if id(last_decoded_vol) != id(self.HRF_peak_vols[-1]): # If a new preprocessed and non decoded vol is detected within 
                                                                           # HRF_peak_vols (i.e., different id from last decoded volume)

                        last_vol = self.HRF_peak_vols[-1] # Get data array from last volume within HRF peak

                        vol_decoding_prob, vol_decoding_time = dynamic_decoding(last_vol.data, # Last preprocessed volume within HRF peak array data
                                                                                self.model_file, # Pre-trained decoder
                                                                                self.ground_truth # Ground truth label to select target decoding probability (ex., 0, 1, 2...)
                                                                               )
                        
                        shared_instances.server.send(vol_decoding_prob) # Send back decoding probability to client side with server object from main.py
                        time.sleep(0.05) # Wait some miliseconds after sending decoding_prob. In that way, different signals will not be sent in the same package of data

                        last_vol.decoding_prob = vol_decoding_prob # Assign decoding probability to last decoded volume
                        last_vol.decoding_time = vol_decoding_time # Assign decoding time to last decoded volume
                        
                        shared_instances.logger.update_vol(last_vol) # Tell logger to update last volume information
                        
                        last_decoded_vol = last_vol # Set this new detected volume as last_decoded_vol to know whether it was already decoded

                    elif id(last_decoded_vol) == id(self.HRF_peak_vols[-1]): # If last_decoded_vol is not a new preprocessed and non decoded volume in this while loop iteration (i.e., has the same id of last decoded volume)
                        time.sleep(0.1) # Just wait until while loop condition is False, refreshing var status each 100 ms and avoid cannibalization of system processing resources
                else:
                    time.sleep(0.1) # Just wait until condition is True, refreshing var status each 100 ms and avoid cannibalization of system processing resources

            self.decoding_done = True # Update trial status to trigger feedback finalization
    

    def _store_trial(self):
        trial_file = open(Path(self.trials_dir) / f'trial_{self.trial_idx}.pkl', 'wb') # Store this trial object containing all preprocessed volumes and information relative to them in a pkl file
        pickle.dump(self, trial_file)
        trial_file.close()



#############################################################################################
# WATCHER CLASS
#############################################################################################

# To process volumes as soon as they are created, a file watcher 
# continuously polls for new files. 

class Watcher(Exp):
    
    def empty_fMRI_folder(self):
        """ Empty fMRI raw volumes output folder """
        folder_exist = self._check_folder() # Check if MRI folder exist
        if folder_exist:
            print(Fore.CYAN  + '\n[WAIT] Removing all volumes from MRI folder...')
            raw_volumes_folder = Path(self.raw_volumes_folder)
            for file in raw_volumes_folder.glob('*.*'): # Get all volumes in this folder
                file.unlink() # Remove each volume
            print(Fore.GREEN  + f'[OK] Volumes removed.')

    def vol_watcher(self, new_vol):
        """ Watch for new files """
        next_vol = format(new_vol.vol_idx, self.index_format) # Next expected volume name
        print(Fore.CYAN + '\n[WAIT] Waiting for volume:', next_vol)
        while True:
            new_vol.vol_time = time.time()
            dicom_file = next(Path(self.raw_volumes_folder).glob(f'*{next_vol}.dcm'), False) # Look up for a file with following name
            if dicom_file != False: # If file exists
                dicom_file = str(dicom_file) # Convert raw volumes route from Path type to string
                print(Fore.GREEN + f'[OK] Vol {new_vol.vol_idx} received.') # When the file exists notify
                break
        return dicom_file

    def _check_folder(self):
        """ Look up for the MRI folder corresponding to this participant, session and run """
        print(Fore.CYAN  + '\n[WAIT] Checking MRI folder to watch...')
        if Path(self.raw_volumes_folder).is_dir():
            print(Fore.GREEN  + f'[OK] Folder OK.')
            return True
        else:
            print(Fore.RED + f'[ERROR] MRI folder "{self.raw_volumes_folder}" does not exist. Please ensure that MRI folder is created before running main.py')
            return False



#############################################################################################
# LOGGER CLASS
#############################################################################################

# Save data relative to timings, trials, volumes and decoding results into a CSV file

class Logger(Exp):

    def __init__(self):
        self.this_run_vols = [] # This fMRI run volumes objects
        self.list_rows = [] # List to store log rows (i.e., data dictionaries corresponding to each volume)

    def add_vol(self, vol):
        self.this_run_vols.append(vol) # Append new_vol object to self.this_run_vols
        variables_to_log = self._log_variables(vol) # Get information corresponding to this volume timepoint
        self.list_rows.append(variables_to_log) # Append that volume information as a dictionary as a row in log file
        df = pd.DataFrame(self.list_rows) # Create a dataframe using list of rows
        df.to_csv(Path(self.logs_dir) / f'logs.csv') # Update CSV file into logs_dir

    def update_vol(self, vol):
        vol_idx = self.this_run_vols.index(vol) # Find volume index in list of vols
        variables_to_log = self._log_variables(vol) # Get information corresponding to this volume timepoint
        self.list_rows[vol_idx] = variables_to_log # Update row corresponding to a volume in rows list
        df = pd.DataFrame(self.list_rows) # Create a dataframe using list of rows
        df.to_csv(Path(self.logs_dir) / f'logs.csv') # Update CSV file into logs_dir

    def _log_variables(self, vol):
        # Variables to log in logs.csv file
        variables_to_log = {
                            'subject': Exp.subject,
                            'session': Exp.session,
                            'run': Exp.run,
                            'n_heatup_vols': Exp.n_heatup_vols,
                            'HRF_peak_onset': Exp.HRF_peak_onset,
                            'HRF_peak_offset': Exp.HRF_peak_offset,
                            'vol_type': vol.vol_type,
                            'trial_idx': vol.trial.trial_idx,
                            'trial_onset': vol.trial.trial_onset,
                            'vol_idx': vol.vol_idx,
                            'vol_time': vol.vol_time,
                            'vol_time_vs_trial_onset': vol.vol_vs_trial_onset,
                            'in_hrf_peak': vol.in_hrf_peak,
                            'decoding_procedure': Exp.decoding_procedure,
                            'vol_decoding_prob': vol.decoding_prob,
                            'trial_decoding_prob': vol.trial.decoding_prob,
                            'stimuli': vol.trial.stimuli,
                            'ground_truth': vol.trial.ground_truth
                            }
        return variables_to_log