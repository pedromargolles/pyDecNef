############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, Python fMRI-Neurofeedback
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: 
############################################################################

import shutil
import time
from pathlib import Path
import shutil
from colorama import init, Fore # For colouring outputs in the terminal
init()

#############################################################################################
# DESCRIPTION
#############################################################################################

# Using real and raw functional MRI data from a subject's session (i.e., DICOM files),
# simulate a MRI scanner to test a experimental paradigm running in paralel 
# neurofeedback scripts as it was a real fMRI session

#############################################################################################
# fMRI SIMULATION VARIABLES
#############################################################################################

TR = 2

#############################################################################################
# DIRECTORIES & DATA
#############################################################################################

# Get script directory
script_dir = Path(__file__).absolute().parent 

# Define an outputs directory to copy DICOM files from real_data directory as it was a real fMRI scanner
outputs_dir = script_dir / 'outputs'

# Remove files in outputs_dir (if there are)
if outputs_dir.exists(): 
    for file in outputs_dir.glob('*.*'): # Get all volumes in outputs folder
        file.unlink() # Remove each volume one by one

# Folder with fMRI real_data
real_data = script_dir / 'real_data'

#############################################################################################
# DATA TRANSFER FROM REAL_DATA TO OUTPUTS FOLDER
#############################################################################################

for volume in sorted(list(real_data.glob('*'))):
    print(Fore.YELLOW + f'\n[PROCESSING] Generating vol {volume.stem}...')
    time.sleep(TR) # Wait for a TR before generating the next volume
    shutil.copy(str(volume), str(outputs_dir))
    print(Fore.GREEN + '[OK]')
    

    