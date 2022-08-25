#############################################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
#############################################################################################

import shutil
import time
from pathlib import Path
import shutil
from colorama import init, Fore # For colouring outputs in the terminal
init()

#############################################################################################
# DESCRIPTION
#############################################################################################

# Using as example raw functional MRI data from a subject's session (i.e., DICOM files), simulate 
# a MRI scanner to test the experimental paradigm running in paralel 
# neurofeedback scripts as it was a real session

#############################################################################################
# fMRI SIMULATION VARIABLES
#############################################################################################

TR = 2 # Repetition time
subject_idx = 1 # Subject index to obtain example volumes from

#############################################################################################
# DIRECTORIES & DATA
#############################################################################################

# Get generate.py script directory
script_dir = Path(__file__).absolute().parent 

# Define an outputs directory to copy DICOM files from real_data directory as it was a real scanner
outputs_dir = script_dir / 'outputs'

# Remove all files in outputs_dir (if there are)
if outputs_dir.exists(): 
    for file in outputs_dir.glob('*.*'): # Get all volumes in outputs folder
        file.unlink() # Remove each volume one by one

# Folder with fMRI DICOM files
real_data = script_dir.parent.parent / f'data/sub-{subject_idx}/example_volumes'
print(real_data)

#############################################################################################
# DATA TRANSFER FROM REAL_DATA FOLDER TO OUTPUTS FOLDER
#############################################################################################

for volume in sorted(list(real_data.glob('*'))):
    print(Fore.YELLOW + f'\n[PROCESSING] Generating volume {volume.stem}...')
    time.sleep(TR) # Wait for a TR before generating the next volume
    shutil.copy(str(volume), str(outputs_dir))
    print(Fore.GREEN + '[OK]')
    

    