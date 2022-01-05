from modules.config.exp_config import Exp
from modules.pipelines.corregistration_pipeline import corregister_vol
import threading
from colorama import init, Fore
# Autoreset line color style
init(autoreset=True)

class Vol(Exp):
    def __init__(self, 
                 vol_idx = None, 
                 vol_time = None, 
                 vol_type = None, 
                 dicom_file = None):

        self.vol_idx = vol_idx
        self.vol_time = vol_time
        self.vol_type = vol_type
        self.dicom_file = dicom_file
        self.vol_vs_trial_onset = None
        self.in_hrf_peak = False
        self.data = None
        self.corregistration_times = None
        self.preproc_vol_to_timeseries_times = None

    def corregistration(self):
        preprocess_vol_thread = threading.Thread(target = self._start_corregistration, args = (self, )) # Specify a thread to preprocess this vol
        preprocess_vol_thread.start() # Start vol corregistration

    def _start_corregistration(self):
        print(Fore.YELLOW + f'Corregistering vol {self.vol_idx}...')
        self.data, self.corregistration_times = corregister_vol(vol_file = self.dicom_file,
                                                                mask_file = self.mask_file,
                                                                ref_vol_file = self.ref_vol_file,
                                                                preprocessed_dir = self.preprocessed_dir
                                                               )
        print(Fore.YELLOW + f'Vol {self.vol_idx} corregistered.')