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

# Extract anatomical ROIs by using reconstructed surface labels and then transform generated
# ROIs to functional space using reference volume

# Labels IDs: 
# https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT

#############################################################################################
# SETUP VARIABLES
#############################################################################################

rois = {
        "FFG_left_comp": "1007",
        "FFG_right_comp": "2007",
       }

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent.parent
data_dir = exp_dir / 'data'
preprocessed_dir = data_dir / 'preprocessed/'
ref_vol_dir = preprocessed_dir / 'ref_vol'
preprocessed_anat_dir = preprocessed_dir / 'anat'
recon_all_dir = preprocessed_dir / 'recon_all'
subject_id = exp_dir.name.split('-')[1]
subject_dir = recon_all_dir / subject_id
orig_dir = subject_dir / 'mri/orig'
rois_dir = preprocessed_dir / 'ROIs_masks'
anat_rois_dir = rois_dir / 'anatomical_ROIs'
func_rois_dir = rois_dir / 'functional_ROIs'

# Create dirs
recon_all_dir.mkdir(exist_ok = True, parents = True)
subject_dir.mkdir(exist_ok = True, parents = True)
rois_dir.mkdir(exist_ok = True, parents = True)
anat_rois_dir.mkdir(exist_ok = True, parents = True)
func_rois_dir.mkdir(exist_ok = True, parents = True)

#############################################################################################
# EXTRACT ANATOMICAL ROIS FROM RECON-ALL APARC+ASEG LABELED SURFACES
#############################################################################################

aparc_aseg_file = str(orig_dir / f'mri/aparc+aseg.mgz')
mgz_anat_file = str(subject_dir / f'{subject_id.zfill(3)}.mgz')

for roi_name, roi_id in rois.items():
    anat_roi_file = str(anat_rois_dir / f'{roi_name}.nii.gz')
    # Extract anatomical ROI by using Freesurfer labels
    subprocess.run([f'mri_binarize --i {aparc_aseg_file} --match {roi_id} --o {anat_roi_file}'], shell = True)
    # Swaps dimensions to avoid FSL errors
    subprocess.run([f'fslswapdim {anat_roi_file} x z -y {anat_roi_file}'], shell = True)
    # Match swaped file to anatomical file used for reconstruction
    subprocess.run([f'mri_convert -i {anat_roi_file} -rl {mgz_anat_file} -o {anat_roi_file}'], shell = True)

#############################################################################################
# MATCH FUNCTIONAL REFERENCE VOLUME TO ANATOMICAL SPACE
#############################################################################################

ref_vol_file = str(ref_vol_dir / 'ref_vol_deobliqued_brain.nii')
anat_noneck_file = str(preprocessed_anat_dir / 'anat_deobliqued_noneck.nii.gz')
brain_anat_noneck_file = str(preprocessed_anat_dir / 'anat_deobliqued_noneck_brain.nii.gz')
refvol2anat_file = str(preprocessed_anat_dir / 'refvol2anat.nii.gz')
 # Convert reference volume to anatomical space
subprocess.run([f'epi_reg --epi={ref_vol_file} --t1={anat_noneck_file} --t1brain={brain_anat_noneck_file } --out={refvol2anat_file}'], shell = True)

#############################################################################################
# INVERT THE DIRECTION OF TRANSFORMATION PARAMETERS (REFVOL2ANAT.MAT TO ANAT2REFVOL.MAT)
#############################################################################################

refvol2anat_matrix_file = str(preprocessed_anat_dir / 'refvol2anat.mat')
anat2refvol_matrix_file = str(preprocessed_anat_dir / 'anat2refvol.mat')
# Invert transformation parameters to transform anatomical data to functional space
subprocess.run([f'convert_xfm -omat {anat2refvol_matrix_file} -inverse {refvol2anat_matrix_file}'], shell = True)

#############################################################################################
# CONVERT ANATOMICAL ROIs to FUNCTIONAL SPACE
#############################################################################################

for roi_name, roi_id in rois.items():
    anat_roi_file = str(anat_rois_dir / f'{roi_name}.nii.gz')
    func_roi_file = str(func_rois_dir / f'{roi_name}_func.nii.gz')
    # Convert anatomical ROI to functional space using inverted transformation parameters
    subprocess.run([f'flirt -in {anat_roi_file} -ref {ref_vol_file} -applyxfm -init {anat2refvol_matrix_file} -o {func_roi_file}'], shell = True)
     # Binarize and refine functional ROI
    subprocess.run([f'fslmaths {func_roi_file} -mul 2 -thr `fslstats {func_roi_file} -p 99.6` -bin {func_roi_file}'], shell = True)