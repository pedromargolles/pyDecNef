#############################################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
#############################################################################################

#############################################################################################
# IMPORT DEPENDENCIES
#############################################################################################

from pathlib import Path
from nilearn.image import concat_imgs

#############################################################################################
# DESCRIPTION
#############################################################################################

# Stack together all volumes of each fMRI run in a NIfTI file

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
preprocessed_dir = exp_dir / 'preprocessed/'
preprocessed_func_dir = preprocessed_dir / 'preprocessed_func'

#############################################################################################
# STACK IN A NIFTI FILE ALL PREPROCESSED FUNCTIONAL VOLUMES BY RUN
#############################################################################################

for folder in preprocessed_func_dir.iterdir():
    if folder.is_dir(): # Iterate over all preprocessed functional runs folders

        vols = [vol_file for vol_file in folder.glob('*.nii')] # List all preprocessed functional volumes of this run
        sorted_vols = sorted(vols, key = lambda vol_file: int(vol_file.name.split('_')[2])) # Ensure volumes are correctly sorted by their index
        sorted_vols_str = [str(vol_file) for vol_file in sorted_vols] # Convert Pathlib format routes to str to avoid Nilearn errors

        print(f'\n{folder.name} sorted functional volumes:')
        print(sorted_vols_str)
        print('\n')

        stacked_run = concat_imgs(sorted_vols_str) # Concatenate all volumes in one 4D array

        stacked_file = folder / (folder.name + '.nii.gz')
        stacked_run.to_filename(stacked_file) # Save stacked data as a single compressed NIfTI file
        for vol_file in sorted_vols:
            vol_file.unlink() # Delete individual NIfTI files of each run folder to free space
        