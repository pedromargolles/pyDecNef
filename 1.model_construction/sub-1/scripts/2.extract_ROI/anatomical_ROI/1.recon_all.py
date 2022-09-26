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

import pandas as pd
from pathlib import Path
import shutil
import subprocess

#############################################################################################
# DESCRIPTION
#############################################################################################

# Reconstruct cortical surface using Freesurfer recon-all from anatomical data

#############################################################################################
# SETUP VARIABLES
#############################################################################################

neck_extraction_size = 140
bet_fractional_intensity = 0.25 # Fractional intensity threshold (0 - 1); default = 0.5; smaller values
                                # give larger brain outline estimates
bet_vertical_gradient = 0 # Vertical gradient in fractional intensity threshold (-1 - 1); default = 0; positive values
                          # give larger brain outline at bottom and smaller at top

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent.parent
data_dir = exp_dir / 'data'
raw_dir = data_dir / 'raw'
anat_dir = raw_dir / 'anat'
preprocessed_dir = data_dir / 'preprocessed/'
preprocessed_anat_dir = preprocessed_dir / 'anat'
recon_all_dir = preprocessed_dir / 'recon_all'
subject_id = exp_dir.name.split('-')[1]
subject_dir = recon_all_dir / subject_id
orig_dir = subject_dir / 'mri/orig'

# Create dirs
preprocessed_anat_dir.mkdir(exist_ok = True)
recon_all_dir.mkdir(exist_ok = True, parents = True)
subject_dir.mkdir(exist_ok = True, parents = True)
orig_dir.mkdir(exist_ok = True, parents = True)

#############################################################################################
# CONVERT ANATOMICAL DICOM TO NIFTI
#############################################################################################

# Stack all anatomical DICOM files into a NIFTI file
subprocess.run([f'dcm2niix -f anat -o {preprocessed_anat_dir} {anat_dir}'], shell = True)

#############################################################################################
# DEOBLIQUE ANATOMICAL NIFTI
#############################################################################################

anat_file = next(preprocessed_anat_dir.glob('anat.nii'))
# Deoblique anatomical file as functional files
deobliqued_anat_file = str(preprocessed_anat_dir / (anat_file.name.split('.nii')[0] + '_deobliqued.nii.gz'))
subprocess.run([f'3dWarp -prefix {deobliqued_anat_file} -deoblique {anat_file}'], shell = True)

#############################################################################################
# REMOVE NECK FROM ANATOMICAL IMAGE
#############################################################################################

anat_noneck_file = str(preprocessed_anat_dir / 'anat_deobliqued_noneck.nii.gz')
# Neck extraction from anatomical image to improve brain extraction
subprocess.run([f'robustfov -i {deobliqued_anat_file} -b {neck_extraction_size} -r {anat_noneck_file}'], shell = True)

#############################################################################################
# PERFORM BRAIN EXTRACTION FROM ANATOMICAL IMAGE
#############################################################################################

anat_noneck_file = str(preprocessed_anat_dir / 'anat_deobliqued_noneck.nii.gz')
brain_anat_noneck_file = str(preprocessed_anat_dir / 'anat_deobliqued_noneck_brain.nii.gz')
# Perform brain extraction on the anatomical image
subprocess.run([f'bet {anat_noneck_file} {brain_anat_noneck_file} -R -f {bet_fractional_intensity} -g {bet_vertical_gradient} -m'], shell = True)

#############################################################################################
# CONVERT ANATOMICAL NIFTI TO MGZ FORMAT
#############################################################################################

new_anat_file = str(orig_dir / f'{subject_id.zfill(3)}.mgz')
# Convert NIFTI file to mgz format to avoid recon-all incompabilities
subprocess.run([f'mri_convert {anat_noneck_file} {new_anat_file}'], shell = True) 

#############################################################################################
# RECONSTRUCT CORTICAL SURFACE
#############################################################################################

# Perform recon-all with Freesurfer
subprocess.run([f'recon-all -s {subject_id} -sd {recon_all_dir} -all -cw256'], shell = True) # cw256 performs cropping if AFNI deoblique increases image dimensions to > 256




