import os
import time
import threading
from classes.trial import Trial

def client_request(message, new_trial, server):
    
    # If message informs about a trial onset
    if message['request_type'] == 'trial_onset':
        trial = Trial()
        trial.trial_idx = message['trial_idx']
        trial.ground_truth = message['ground_truth']
        trial.stimuli = message['word']
        trial.trial_onset = time.time() # Set onset time when we receive onset signal. 
                                        # There is some delay with respect to when the onset actually occurred in the stimuli presentation computer. 
                                        # However, by doing this we avoid clock synchronization problems between experimental computer and server computer.

        server.send('ok') # Send an OK to the client when information is received
        return trial

    # If message is a request from experimental software to decode HRF peak volumes within this trial 
    if message['request_type'] == 'feedback_start':
        feedback_thread = threading.Thread(target = new_trial.decode(), # Call new_trial.decode function and pass server object as argument to send back 
                                                                        # a message when decoding is finished
                                           args = (server, )) # Decode volumes in a new thread to not interrupt volumes filewatcher
        feedback_thread.start() # Open the thread

    # If message is a request to finish this experimental run
    if message['request_type'] == 'exp_run_end':
        print('Experimental run is over.')
        os._exit(1) # End server execution