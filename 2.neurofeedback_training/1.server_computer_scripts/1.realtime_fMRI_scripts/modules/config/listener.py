############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
############################################################################

import os
import time
import threading
import pickle
from colorama import init, Fore
from modules.classes.classes import Trial
from modules.config import shared_instances

#############################################################################################
# LISTENER CLASS
#############################################################################################

# Listener class match specific client requests (i.e., experimental software requests) with specific server actions
# This class can be customized to create new requests-actions pairings

class Listener:
    def __init__(self):
        pass

    def listen(self):
        listener_thread = threading.Thread(name = 'listener', 
                                           target = self._start_listen)
        listener_thread.start() # Keep listening to client requests in a new thread

    def _start_listen(self):
        while True:
            self.client_request = shared_instances.server.listen() # Start listening to potential client requests as a dictionary
            self._process_client_requests() # Execute a specific action when a request is received 
    
    #############################################################################################
    # CLIENT REQUESTS - SERVER ACTIONS PAIRINGS
    #############################################################################################

    def _process_client_requests(self):

        # If client request signals a trial onset
        if self.client_request['request_type'] == 'trial_onset':
            shared_instances.new_trial = Trial()
            shared_instances.new_trial.trial_idx = self.client_request['trial_idx']
            shared_instances.new_trial.ground_truth = self.client_request['ground_truth']
            shared_instances.new_trial.stimuli = self.client_request['stimuli']
            shared_instances.new_trial.trial_onset = time.time() # Set an onset time when we receive trial onset signal
                                                                 # There might be some delay (miliseconds) with respect to when the onset actually occurred in the experimental software computer 
                                                                 # However, by doing this we avoid clock synchronization problems between experimental computer and server computer

            shared_instances.server.send('ok') # Send an OK to the client when request is processed

        # If client request from experimental software signals to start with decoding of HRF peak volumes in this trial
        elif self.client_request['request_type'] == 'feedback_start':
            feedback_thread = threading.Thread(
                                               name = 'decoding_trial',
                                               target = shared_instances.new_trial._decode
                                              ) # Call new_trial.decode function and pass server object as an argument, to send back 
                                                # resulting information to experimental software when decoding is finished
                                                # Decode trial volumes in a new thread for not interrupting volumes' filewatcher
            
            feedback_thread.start() # Start a new thread
            feedback_thread.join() # Wait until decoding is finished, then continue

            if shared_instances.new_trial.decoding_done == True:
                shared_instances.server.send('ok') # End of feedback procedure. Continue with the next experimental phase
        
        # If client request is a request to finish this experimental run
        elif self.client_request['request_type'] == 'end_run':
            print(Fore.GREEN + '[FINISHING] Experimental run is over.')
            shared_instances.server.send('ok') # End experimental software script and exit.
            os._exit(1) # End server execution

        else:
            print(Fore.RED + f'[ERROR] Request {self.client_request} not recognized.')