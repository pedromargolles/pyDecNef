#############################################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
#############################################################################################

from pathlib import Path
import time
from colorama import init, Fore
import sys
init(autoreset=True)

#############################################################################################
# EXP CLASS
#############################################################################################

# Main configuration file 
# Here you can set experimental, MRI scanner parameters and directory routes

class Exp:

    #############################################################################################
    # EXPERIMENTAL PARAMETERS
    #############################################################################################

    # Volumes processing information
    n_heatup_vols = 5 # Number of volumes needed for heating up MRI scanner (heatup duration = TR * n_heatup_vols)

    n_baseline_vols = 20 # Number of baseline volumes after heatup to sample before beggining with the experimental task (baseline duration = TR * n_baseline_vols)

    TR = 2 # MRI Repetition time. Volumes sampling rate (in seconds)

    HRF_peak_onset = 5 # H.R.F. peak threshold onset (seconds from trial onset). Default HRF_peak_onset = 5 for decoding procedure = 'average_HRF_peak_vols' or 'average_probs'. 
                       # Set to 0 if do you want to decode volumes from trial onset in dynamic neurofeedback experiments

    HRF_peak_offset = 11 # H.R.F. peak threshold offset (seconds from trial onset). Default HRF_peak_offset = 11 for decoding procedure = 'average_HRF_peak_vols' or 'average_probs'. 
                         # Set to float("inf") if using an undetermined number of H.R.F. peak volumes within each trial of dynamic neurofeedback experiments


    # Volumes tracking
    first_vol_idx = 1 # First volume index to track in EXP.raw_volumes_folder
    index_format = '04d' # How volumes indexes are left-zero padded in fMRI cls.raw_volumes_folder folder? (ex., IM-0001.dcm)
    
    # Z-scoring procedure
    zscoring_procedure = 'to_model_session' # 'to_model_session' (default) (each task volume will be z-scored relative to model construction session data in specific R.O.I. using its mean and standard deviation).
                                            # 'to_baseline' (each task volume will be z-scored relative to data from that run baseline in specific R.O.I. For example, volumes 51 will be z-scored to n_baseline_vols data)
                                            # 'to_timeseries' (each task volume will be z-scored relative to that run previous volumes in specific R.O.I.. For example, volume 51 will be z-scored using data from volume 0 to that volume)
    
    # Decoding settings
    decoding_procedure = 'average_probs' # 'average_HRF_peak_vols' (average volumes within a trial H.R.F. peak before decoding a single averaged volume to increase signal-to-noise ratio)
                                         # 'average_probs' (default) (average decoding probabilities of volumes within a trial H.R.F. peak to increase feedbacks variability)
                                         # 'dynamic' (all volumes within a trial H.R.F. peak, will be decoded independently and sent individually to experimental software as feedback)


    @classmethod # This method ensures participants data and directory routes can be inherited by all other classes
    def _new_participant(cls):

        """ Request new participant data (participant, session, run) each time main.py runs to set directories routes """

        def check_file(file):

            """ Check if a essential file exists or not. If not then cancel script execution. """

            if not file.exists():
                sys.exit(Fore.RED + f'[ERROR] File/Directory "{file}" does not exist. Check that you are pointing to a correct path. Breaking main.py execution.')

        #############################################################################################
        # DIRECTORIES & DATA
        #############################################################################################

        # First, ask for participant info to find/generate its corresponding folders
        print(Fore.YELLOW + 'Specify participants data before initialization:')
        cls.subject = input(Fore.YELLOW + '\nParticipant number: ')
        cls.session = input(Fore.YELLOW + 'Session number: ')
        cls.run = input(Fore.YELLOW + 'Run number: ')
        print('\n')

        # Package directory
        cls.moduledir = Path(__file__).absolute().parent.parent.parent

        # fMRI raw volumes output folder
        cls.raw_volumes_folder = cls.moduledir.parent / 'mri_simulator/outputs' # To use with fMRI simulator stored in ../../1.fakefmri_realdata
        print(cls.raw_volumes_folder)
        #cls.raw_volumes_folder = '/firmm/20211028.pm21oct.pm21oct' # To use in a real experiment setting
        check_file(cls.raw_volumes_folder)
 
        # Required resources directory 
        # Contains pretrained model, region of interest mask, reference functional volume & z-scoring information
        cls.resources_dir = cls.moduledir.parent.parent / f'data/sub-{cls.subject}'
        print(cls.resources_dir)
        check_file(cls.resources_dir)

        # Pretrained model path
        cls.model_file = cls.resources_dir / 'models/bilateral_occipital_model.joblib'
        check_file(cls.model_file)

        # Region of interest mask path (as .nii to maximize load speed)
        cls.mask_file = cls.resources_dir / 'coregistration/masks/bilateral_occipital.nii'
        check_file(cls.mask_file)

        # Reference functional volume path (from model construction session. As .nii to maximize load speed)
        cls.ref_vol_file = cls.resources_dir / 'coregistration/ref_vol/example_func_deoblique_brain.nii'
        check_file(cls.ref_vol_file)

        # Brain extraction configuration file path
        #cls.bet_config_file = cls.resources_dir / 'coregistration/brain_extraction/bet_config.txt'
        #check_file(cls.bet_config_file)
        
        # ROI reference data for z-scoring (if zscoring_procedure is 'to_model_session')
        if cls.zscoring_procedure == 'to_model_session':
            cls.zscoring_mean =  cls.resources_dir / 'zscoring/mean_bilateral_occipital.npy' # Numpy array containing mean of model construction session data
            cls.zscoring_std = cls.resources_dir / 'zscoring/std_bilateral_occipital.npy'  # Numpy array containing standard deviation of model construction session data

        # Create an outputs directory to store participant session log files and preprocessed volumes
        cls.outputs_dir = cls.moduledir / f'outputs/sub-{cls.subject}_session-{cls.session}'
        Path(cls.outputs_dir).mkdir(parents=True, exist_ok=True)
        
        # main.py script run time
        script_run_time = time.strftime('%Y-%m-%d_%H-%M-%S') # Get main.py script run time, to create an unique run folder 
                                                             # and avoid folder replacement problems when wrongly typing runs number

        # Make a run directory inside outputs dir to store all participant log files and preprocessed volumes
        cls.run_dir = cls.outputs_dir / f'run-{cls.run}_{script_run_time}'
        Path(cls.run_dir).mkdir(parents=True, exist_ok=True)

        # Make a trials directory inside run directory to store all masked volumes and information classified by trial
        cls.trials_dir = cls.run_dir / 'trials'
        Path(cls.trials_dir).mkdir(parents=True, exist_ok=True)

        # Make a logs directory inside run directory to store run logs data
        cls.logs_dir = cls.run_dir / 'logs_dir'
        Path(cls.logs_dir).mkdir(parents=True, exist_ok=True)

        # Make a preprocessed volumes directory inside run directory to store all outputs corresponding to preprocessed volumes in that run
        cls.preprocessed_dir = cls.run_dir / 'preprocessed'
        Path(cls.preprocessed_dir).mkdir(parents=True, exist_ok=True)

        

        # CHECKS