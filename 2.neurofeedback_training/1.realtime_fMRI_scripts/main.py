############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021, Python fMRI-Neurofeedback
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: 
############################################################################

import os
import time
from colorama import init, Fore
import threading
from modules.config import shared_instances
init(autoreset=True)

#############################################################################################
# SET EXPERIMENTAL PARAMETERS
#############################################################################################

from modules.config.exp_config import Exp
Exp._new_participant() # Generate directory routes with specified participant, session and run

#############################################################################################
# CLEAR SCREEN
#############################################################################################

clear = lambda: os.system('clear')
clear() # Clear the console before continuing

#############################################################################################
# INITIALIZE A SERVER TO SEND/RECEIVE PICKLED DATA FROM/TO THE EXPERIMENTAL SOFTWARE
#############################################################################################

from modules.config.connection_config import Connection
shared_instances.server = Connection()
shared_instances.server.start_server()

#############################################################################################
# INSTATIATE TIMESERIES OBJECT
#############################################################################################

from modules.classes.classes import Timeseries
shared_instances.timeseries = Timeseries() # timeseries object will contain all corregistered run volumes
                                           # for pre-processing (ex., for detrending or z-scoring)

#############################################################################################
# INSTATIATE FIRST TRIAL OBJECT
#############################################################################################

from modules.classes.classes import Trial
shared_instances.new_trial = Trial() # Empty trial object
                                     # new_trial will be replaced with each experimental trial

#############################################################################################
# INITIALIZE VOLUMES WATCHER IN MRI FIRMM FOLDER
#############################################################################################

from modules.classes.classes import Watcher
watcher = Watcher()
watcher.empty_fMRI_folder() # Remove all volumes within EXP.raw_volumes_folder (dont worry, previous 
                            # runs/sessions functional volumes will be backed up in 
                            # EXP.preprocessed_dir)

#############################################################################################
# START RECEIVING FLOW CONTROL REQUESTS FROM THE EXPERIMENTAL SOFTWARE
#############################################################################################

from modules.config.listener import Listener
listener = Listener()
listener.listen() # Continously listen to experimental software requests in a new thread

#############################################################################################
# INITIALIZE VOLUMES LOGGER
#############################################################################################

from modules.classes.classes import Logger
shared_instances.logger = Logger() # Keep track of volumes information and store it in a logs file

#############################################################################################
# MAIN THREAD
#############################################################################################

print(Fore.YELLOW + '\n[START] Listening for new volumes...')

from modules.classes.classes import Vol
vol_idx = Exp.first_vol_idx # Start with the first vol idx

while True:

    new_vol = Vol(vol_idx = vol_idx) # Create a new volume instance

    print('.....................................................................')

    new_vol.dicom_file = watcher.vol_watcher(new_vol) # Wait for volume including that vol_idx in EXP.raw_volumes_folder

    time.sleep(0.1) # Wait for 100ms to ensure file copying from MRI scanner is completely finished

    #############################################################################################
    # MRI SCANNER HEATUP
    #############################################################################################
    
    in_heatup = Exp.first_vol_idx + Exp.n_heatup_vols # Number of volumes after first vol_idx to consider as heatup 
                                                      # (i.e., volume index where heatup will finish)

    if new_vol.vol_idx <= in_heatup: # While heating up print a warning
        new_vol.vol_type = 'heatup' # Label volume as heatup_vol for logs_file
        print(Fore.RED + '[HEATING UP] MRI scanner is heating up.')

    if new_vol.vol_idx == in_heatup + 1: # After heating up, send a signal to the experimental software to resume
        shared_instances.server.send('fmriheatedup')

    #############################################################################################
    # fMRI BASELINE
    #############################################################################################

    in_baseline = Exp.first_vol_idx + Exp.n_baseline_vols # Number of volumes after first vol_index to consider as baseline 
                                                          # (i.e., vol index where baseline will finish)

    if in_heatup < new_vol.vol_idx <= in_baseline: # While measuring baseline print a warning
        new_vol.vol_type = 'baseline'
        print(Fore.RED + '[BASELINE] Measuring this fMRI run baseline activity.')

    if new_vol.vol_idx == in_baseline + 1: # After baseline is acquired, send a signal to 
                                           # the experimental software to start with the experimental task
        shared_instances.server.send('baselineok')

    #############################################################################################
    # TASK STARTS
    #############################################################################################

    if new_vol.vol_idx > in_baseline: # If it is not a baseline volume, then label as an experimental task volume
        new_vol.vol_type = 'task'

    #############################################################################################
    # VOLUME PREPROCESSING
    #############################################################################################

    new_vol.preprocessing() # After labeling fMRI volume, then preprocess it in an independent thread (this avoids sampling
                                      # delays due to preprocessing overlappings between volumes if preprocessing times > TR)

    shared_instances.new_trial.assign(new_vol) # Assign preprocessed vol to new_trial object

    #############################################################################################
    # VOLUMES DECODING
    #############################################################################################

    # When decoding request is received from client side, Trial class will automatically perform
    # decoding of those volumes within HRF peak. Check Trial class in modules.classes.classes for
    # more details.

    #############################################################################################
    # CONSOLE REPORT
    #############################################################################################

    if shared_instances.new_trial.trial_idx != None: # With the first indexed trial, start showing experimental info in console
        print(Fore.YELLOW + '\nSubject:', Exp.subject, Fore.YELLOW + 'Session:', Exp.session, Fore.YELLOW + 'Run:', Exp.run)
        print(Fore.YELLOW + 'Trial:', shared_instances.new_trial.trial_idx)
        print(Fore.YELLOW + 'Trial onset time:', shared_instances.new_trial.trial_onset)
        print(Fore.YELLOW + 'Volume index:', new_vol.vol_idx)
        print(Fore.YELLOW + 'Volume time:', new_vol.vol_time)
        print(Fore.YELLOW + 'Volume type:', new_vol.vol_type)
        print(Fore.YELLOW + 'Time after trial onset:', new_vol.vol_vs_trial_onset)
        print(Fore.YELLOW + f'Is this volume within HRF Peak ({Exp.HRF_peak_onset}-{Exp.HRF_peak_offset} seconds from trial onset):', new_vol.in_hrf_peak)
        print(Fore.YELLOW + f'Has HRF peak already ended for this trial?:', shared_instances.new_trial.HRF_peak_end)
        print(Fore.YELLOW + f'Number of volumes within HRF peak interval in this trial:', shared_instances.new_trial.n_HRF_peak_vols)
        print(Fore.YELLOW + f'Trial decoding prob:', shared_instances.new_trial.decoding_prob)
        print(Fore.YELLOW + f'Has decoding process already finished?:', shared_instances.new_trial.decoding_done)
        print(Fore.YELLOW + f'Number of current threads:', threading.active_count())
    else:
        print(Fore.YELLOW + 'Waiting for the first trial...') # If new_trial index is None (i.e., the experimental task did not start yet)
    
    print('.....................................................................')

    #############################################################################################
    # PREPARE FOR NEXT VOL
    #############################################################################################
    
    vol_idx += 1