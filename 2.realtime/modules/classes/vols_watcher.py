from modules.config.exp_config import Exp
import time
from pathlib import Path
from colorama import init, Fore
# Autoreset line color style
init(autoreset=True)

class Watcher(Exp):
    def __init__(self):
        self._check_folder()

    # Empty fMRI raw vols output folder
    def empty_fMRI_folder(self):
        files_dir = Path(self.files_dir)
        for file in files_dir.glob('*.*'):
            file.unlink()
        return

    # To process volumes as soon as they are finished being created,
    # a file watcher function continuously polls for new files. 
    def vol_watcher(self, new_vol):
        # What file name are you going to load next
        next_vol = format(new_vol.vol_idx, '04d')
        print(Fore.CYAN + '\n[WAIT] Waiting for volume:', next_vol)
        while True:
            new_vol.vol_onset = time.time()
            dicom_file = next(Path(self.files_dir).glob(f'*{next_vol}.dcm'), False) # Check for a file with next_volume included in its name
            if dicom_file != False:
                dicom_file = str(dicom_file) # Next_filename to string
                print(Fore.GREEN + f'[OK] Vol {new_vol.vol_idx} received.') # When the file exists notify
                break
        return dicom_file
    
    def _check_folder(self):
        # Look for the fMRI folder for this subject, session and run
        print(Fore.CYAN  + '\n[WAIT] Checking fMRI folder to watch...')
        if Path(self.files_dir).is_dir():
            print(Fore.GREEN  + f'[OK] Folder OK.')
        else:
            print(Fore.RED + f'[ERROR] fMRI folder "{self.files_dir}" does not exist. Please ensure that this folder is created before running main.py')