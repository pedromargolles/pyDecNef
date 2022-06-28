############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021, Python fMRI-Neurofeedback
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
# FMRI SIMULATION VARIABLES
#############################################################################################

TR = 2

#############################################################################################
# DIRECTORIES & DATA
#############################################################################################

# Get script dir
script_dir = Path(__file__).absolute().parent 

# Create an output dir to copy DICOM files from real_data dir as it was an fMRI machine
output_dir = script_dir / 'output'

# Remove output dir if it exists
if output_dir.exists(): 
    shutil.rmtree(output_dir)

# Folder with fMRI real_data
real_data = script_dir / 'real_data'

#############################################################################################
# TRANSFER DATA
#############################################################################################

for i in sorted(list(real_data.glob('*'))):
    print(Fore.YELLOW + f'\n[PROCESSING] Generating vol {i.stem}...')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    time.sleep(TR) # Wait for a TR before generating the next volume
    shutil.copy(str(i), str(output_dir))
    print(Fore.RED + '[OK]')
    

    