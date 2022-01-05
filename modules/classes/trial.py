from modules.config.exp_config import Exp
import time
from modules.pipelines.trial_decoding_pipeline import decode_trial_vols
import sys

class Trial(Exp):
    def __init__(self, 
                 trial_idx = None, 
                 trial_onset = None, 
                 stimuli = None, 
                 ground_truth = None):

        self.trial_idx = trial_idx
        self.trial_onset = trial_onset
        self.stimuli = stimuli
        self.ground_truth = ground_truth
        self.vols = []
        self.HRF_peak_vols = []
        self.HRF_peak_end = False # To track whether HRF peak ends with the last volume assigned to this trial
        self.decoding_prob = None
        self.decoding_time = None

    def assign(self, vol):
        vol.vol_vs_trial_onset = vol.vol_time - self.trial_onset # Calculate vol time difference from trial onset
        self.vols.append(vol) # Append vol to this trial list of vols
        
        if self.HRF_peak_onset <= vol.vol_vs_trial_onset <= self.HRF_peak_offset: # If vol within HRF peak append to specific list for decoding
            vol.in_hrf_peak = True
            self.HRF_peak_vols.append(vol)
            self.n_hrf_peak_vols = len(self.HRF_peak_vols)

        elif (vol.vol_vs_trial_onset + self.TR) >= self.HRF_peak_offset: # If next vol will not be within HRF peak
            self.HRF_peak_end = True

    def decode(self, server):
        while self.hrf_peak_end == False: # If decoding signal is received before HRF peak finish, just wait until it happens to start decoding volumes
            time.sleep(0.1) # Just wait until condition is True refreshing var status each 100 ms to avoid cannibalization of system processing resources

        self.decoding_prob, self.decoding_time = decode_trial_vols(preproc_vols = self.HRF_peak_vols,
                                                                   model_file = self.model_file,
                                                                   ground_truth = self.ground_truth,
                                                                   decoding_procedure = self.decoding_procedure
                                                                   )

        server.send(f'{self.decoding_prob}') # Send back decoding likelihood to client side
        time.sleep(0.05) # Wait some miliseconds to end decoding so end signal is not sent in the same package of data
        server.send('ok') # End of decoding procedure. Continue with next experimental phase
        sys.exit() # Kill this processing thread
