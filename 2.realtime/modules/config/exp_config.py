from colorama import init, Fore
from pathlib import Path
import time
init(autoreset=True) # Autoreset line color style

#############################################################################################
# DESCRIPTION
#############################################################################################

# Main configuration file. 
# Here you can set experimental, MRI scanner parameters and directory routes.

class Exp:

    #############################################################################################
    # EXPERIMENTAL PARAMETERS
    #############################################################################################

    # Volumes processing information
    n_heatup_vols = 5 # Number of volumes for heating up MRI scanner (heatup duration = TR * n_heatup_vols)
    n_baseline_vols = 30 # Number of baseline volumes to sample before beggining with the experimental task (baseline duration = TR * n_baseline_vols)
    low_HRF_peak = 5 # Bottom HRF peak threshold (seconds from trial onset)
    high_HRF_peak = 11 # Top HRF peak threshold (seconds from trial onset)
    TR = 2 # Volumes sampling rate (in seconds)

    # Volumes tracking
    first_vol_idx = 1 # First volume index to track
    
    # Decoding procedure
    decoding_procedure = 'average_probs' # Average vols within HRF peak probabilities of decoding ground truth 'average_probs' or 
                                         # 'average_hrf_peak_vols' to average vols within HRF peak before decoding a single 
                                         # averaged vol to increase signal-to-noise ratio

    @classmethod # This method helps participants data and routes can be easely inherited by all other package classes without instantiating Exp class and repeatedly passing that as a class function argument
    def _new_participant(cls):

        """ Register new participant data each time main.py starts to set directories routes """

        #############################################################################################
        # DIRECTORIES & DATA
        #############################################################################################

        # First ask for participant info to find its corresponding folders
        print(Fore.YELLOW + 'Specify participants data before initialization:')
        cls.subject = input(Fore.YELLOW + '\nParticipant number: ')
        cls.session = input(Fore.YELLOW + 'Session number: ')
        cls.run = input(Fore.YELLOW + 'Run number: ')
        print('\n')

        # Package directory
        cls.moduledir = Path(__file__).absolute().parent.parent.parent

        # fMRI raw vols output folder
        #files_dir = moduleDir / '1.fakefmri_realdata/output' # To use with fake fMRI simulator in 1.fakefmri_realdata
        cls.files_dir = '/firmm/20211028.pm21oct.pm21oct' # To use in a real experiment setting

        # Required resources directory (i.e., pretrained model, region of interest mask & reference functional volume to corregister this session volumes)
        cls.resources_dir = cls.moduledir / f'required_resources/sub-{cls.subject}'

        # Pretrained model path
        cls.model_file = cls.resources_dir / 'models/bilateral_occipital_model.joblib'

        # Region of interest mask path (as .nii to maximize load speed)
        cls.mask_file = cls.resources_dir / 'masks/bilateral_occipital.nii'

        # Model construction session reference volume path
        cls.ref_vol_file = cls.resources_dir / 'training_session_ref_image/example_func_deoblique_brain.nii'

        # Make an output dir to store participants session results and preprocessed vols
        cls.outputs_dir = cls.moduledir / f'outputs/sub-{cls.subject}_session-{cls.session}'
        Path(cls.outputs_dir).mkdir(parents=True, exist_ok=True)
        
        # main.py script run time
        script_run_time = time.strftime('%Y-%m-%d_%H-%M-%S') # Get main.py script run time, to create an unique run folder 
                                                             # and avoid folder replacement problems when wrongly typing run number

        # Make a run dir inside outputs_dir to store all participant session results
        cls.run_dir = cls.outputs_dir / f'run-{cls.run}_{script_run_time}'
        Path(cls.run_dir).mkdir(parents=True, exist_ok=True)

        # Make a logs dir inside run_dir to store all participant session data
        cls.logs_dir = cls.run_dir / 'logs_dir'
        Path(cls.logs_dir).mkdir(parents=True, exist_ok=True)

        # Make a preprocessed volumes dir inside run_dir to store all outputs corresponding to preprocessed vols
        cls.preprocessed_dir = cls.run_dir / 'preprocessed'
        Path(cls.preprocessed_dir).mkdir(parents=True, exist_ok=True)