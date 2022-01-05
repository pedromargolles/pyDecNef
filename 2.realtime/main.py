############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021, Python fMRI-Neurofeedback
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: 
############################################################################

import os
import threading
import time
from colorama import init, Fore # For colouring outputs in the terminal
init(autoreset=True) # Autoreset line color style

#############################################################################################
# SET EXPERIMENTAL PARAMETERS
#############################################################################################

from modules.config.exp_config import Exp
Exp._new_participant() # Generate directory routes with participant, session and run data

#############################################################################################
# CLEAR SCREEN
#############################################################################################

clear = lambda: os.system('clear')
clear() # Clear the console before continuing

#############################################################################################
# INITIALIZE A SERVER TO SEND/RECEIVE PICKLED DATA FROM/TO THE EXPERIMENTAL SOFTWARE
#############################################################################################

from modules.config.connection_config import Connection
server = Connection.start_server()

#############################################################################################
# INSTATIATE FIRST TRIAL OBJECT
#############################################################################################

from modules.classes.trial import Trial
new_trial = Trial() # new_trial will be replaced on each experimental trial

#############################################################################################
# START RECEIVING CONTROL FLOW INSTRUCTIONS FROM THE EXPERIMENTAL SOFTWARE
#############################################################################################

from modules.config.client_requests import client_request

def listening():
    while True:
        client_message = server.listen()
        request = client_request(client_message, new_trial, server) # Execute a specific command when a message is received 
                                                                    # from client side. Potential Message - Commands are specified
                                                                    # within config.client_requests.py file.
        
        if isinstance(request, Trial): # If returned message is a Trial object
            new_trial = request # Assign to new_trial the new trial object received from the client side

onset_thread = threading.Thread(target = listening)
onset_thread.start() # Continously keep listening to client requests in a new thread

#############################################################################################
# INITIALIZE VOLUMES WATCHER ON FMRI FOLDER
#############################################################################################

from modules.classes.vols_watcher import Watcher
watcher = Watcher()
watcher.empty_fMRI_folder() # Remove previous volumes within EXP.files_dir (dont worry, previous runs/sessions 
                            # functional volumes have also been recorded in EXP.preprocessed_dir as backup)

#############################################################################################
# INITIALIZE VOLS LOGGER
#############################################################################################

from modules.classes.vols_logger import Logger
logger = Logger()

#############################################################################################
# CREATE A TIMESERIES OBJECT TO STORE AND PREPROCESS NEW VOLS WITH WHOLE fMRI TIMESERIES
#############################################################################################

from modules.classes.timeseries import Timeseries
timeseries = Timeseries()

#############################################################################################
# MAIN THREAD
#############################################################################################

print(Fore.YELLOW + '[START] Listening for new volumes...')

from modules.classes.vol import Vol
vol_idx = Exp.first_vol_idx # Start with the first vol idx

while True:

    new_vol = Vol(vol_idx = vol_idx) # Create a new vol instance

    # Separator
    print('.....................................................................')

    # Whatch for that file
    new_vol.dicom_file = watcher.vol_watcher(new_vol.vol_idx) # Wait for the next volume

    # Wait for 100ms to ensure file copying from MRI scanner is completely finished
    time.sleep(0.1)

    #############################################################################################
    # MRI scanner HEATUP
    #############################################################################################
    
    in_heatup = vol_idx + Exp.n_heatup_vols # Number of vols after first vol_idx to consider as heatup 
                                            # (i.e., vol index where heatup should finish)

    # While heating up print a warning
    if new_vol.vol_idx <= in_heatup:
        new_vol.vol_type = 'heatup' # Label as heatup_vol for logs_file
        print(Fore.RED + '[HEATING UP] MRI machine is heating up.')

    # After heating up, send a signal to the experimental software to resume
    if new_vol.vol_idx == in_heatup + 1:
        server.send('fMRIheatedup')

    #############################################################################################
    # fMRI RUN BASELINE ACTIVITY
    #############################################################################################

    in_baseline = vol_idx + Exp.n_baseline_vols # Number of vols after first vol_index to consider as baseline 
                                                # (i.e., vol index where baseline should finish)

     # While measuring baseline print a warning
    if in_heatup < new_vol.vol_idx <= in_baseline:
        new_vol.vol_type = 'baseline'
        print(Fore.RED + '[BASELINE] Measuring this fMRI run baseline activity.')
    
    # After baseline is acquired, send a signal to the experimental software to start with the experimental task
    if new_vol.vol_idx == in_baseline + 1:
        server.send('baselineok')

    #############################################################################################
    # TASK STARTS
    #############################################################################################

    # If it is not a baseline vol, then label it as experimental task volume
    if new_vol.vol_idx > in_baseline:
        new_vol.vol_type = 'task'

    #############################################################################################
    # VOL PREPROCESSING
    #############################################################################################

    # After labeling fMRI vol, then preprocess it in an independent thread (i.e., brain extraction, 
    # corregistration to reference volume, ROI masking, smoothing...)
    new_vol.corregistration()

    # Preprocess new vol using whole timeseries data (i.e., detrending, zscoring, high-pass filtering...).
    new_vol.data, new_vol.preproc_vol_to_timeseries_times = timeseries.preproc_vol_2_timeseries(new_vol)

    # Assign preprocessed vol to this trial
    new_trial.assign(new_vol)

    #############################################################################################
    # CONSOLE REPORT
    #############################################################################################

    if new_trial.trial_idx != None:
        # Print subject info
        print(Fore.YELLOW + '\nSubject:', Exp.subject, 'Session:', Exp.session, 'Run:', Exp.run)
        # Print actual trial data
        print(Fore.YELLOW + 'Trial:', new_trial.trial_idx)
        print(Fore.YELLOW + 'Trial onset time:', new_trial.trial_onset)
        # Print volume info
        print(Fore.YELLOW + 'Volume index:', new_vol.vol_idx)
        print(Fore.YELLOW + 'Volume time:', new_vol.vol_time)
        print(Fore.YELLOW + 'Volume type:', new_vol.vol_type)
        print(Fore.YELLOW + 'Time after trial onset:', new_vol.vol_vs_trial_onset)
        print(Fore.YELLOW + f'Is this volume within HRF Peak ({Exp.low_HRF_peak}-{Exp.high_HRF_peak} seconds):', new_vol.in_hrf_peak)
        # Print decoding info
        print(Fore.YELLOW + f'Has HRF peak already ended for this trial?:', new_trial.hrf_peak_end)
        print(Fore.YELLOW + f'Number of vols within HRF peak interval in this trial:', new_trial.n_hrf_peak_vols)
        print(Fore.YELLOW + 'Decoding prob:', new_trial.decoding_prob)

    else:
        print(Fore.YELLOW + 'Waiting for the first trial...') # If new_trial idx is None (i.e., the experimental task did not start yet)

    #End volume separator
    print('.....................................................................')

    #############################################################################################
    # DATA LOGGING
    #############################################################################################
    
    # With each vol record in a csv file the next variables values. Use this format: 
    # [('column_name', variable_to_register), 'column_name', variable_to_register)]
    logger.append_data([
                        ('subject', Exp.subject),
                        ('session', Exp.session),
                        ('run', Exp.run),
                        ('n_heatup_vols', Exp.n_heatup_vols),
                        ('low_HRF_peak', Exp.low_HRF_peak),
                        ('high_HRF_peak', Exp.high_HRF_peak),
                        ('vol_type', new_vol.vol_type),
                        ('trial_idx', new_trial.trial_idx),
                        ('trial_onset', new_trial.trial_onset),
                        ('vol_idx', new_vol.vol_idx),
                        ('vol_time', new_vol.vol_time),
                        ('vol_time_vs_trial_onset', new_vol.vol_vs_trial_onset),
                       ])

    #############################################################################################
    # PREPARE FOR NEXT VOL
    #############################################################################################
    
    vol_idx += 1