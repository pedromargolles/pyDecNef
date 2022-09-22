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

subject_id = 1
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
subject_dir = recon_all_dir / str(subject_id)
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

aparc_aseg_file = str(subject_dir / f'mri/aparc+aseg.mgz')
mgz_anat_file = str(subject_dir / f'{subject_id.zfill(3)}.mgz')

for roi_name, roi_id in rois.items():
    anat_roi = str(anat_rois_dir / f'{roi_name}.nii.gz')
    subprocess.run([f'mri_binarize --i {aparc_aseg_file} --match {roi_id} --o {anat_roi}'], shell = True)
    subprocess.run([f'fslswapdim {anat_roi} x z -y {anat_roi}'], shell = True)
    subprocess.run([f'mri_convert -i {anat_roi} -rl {mgz_anat_file} -o {anat_roi}'], shell = True)

#############################################################################################
# MATCH ANATOMICAL TO REFERENCE VOLUME FUNCTIONAL SPACE
#############################################################################################

ref_vol = str(ref_vol_dir / 'ref_vol_deobliqued_brain.nii')
anat_noneck_file = str(preprocessed_anat_dir / 'anat_deobliqued_noneck.nii.gz')
brain_anat_noneck_file = str(preprocessed_anat_dir / 'anat_deobliqued_noneck_brain.nii.gz')
refvol2anat = str(preprocessed_anat_dir / 'refvol2anat.nii.gz')
subprocess.run([f'epi_reg --epi={ref_vol} --t1={anat_noneck_file} --t1brain={brain_anat_noneck_file } --out={refvol2anat}'], shell = True)

#############################################################################################
# INVERT THE DIRECTION OF TRANSFORMATION PARAMETERS (REFVOL2ANAT.MAT TO ANAT2REFVOL.MAT)
#############################################################################################

refvol2anat_matrix = str(preprocessed_anat_dir / 'refvol2anat.mat')
anat2refvol_matrix = str(preprocessed_anat_dir / 'anat2refvol.mat')
subprocess.run([f'convert_xfm -omat {anat2refvol_matrix} -inverse {refvol2anat_matrix}'], shell = True)

#############################################################################################
# CONVERT ANATOMICAL ROIs to FUNCTIONAL SPACE
#############################################################################################

for roi_name, roi_id in rois.items():
    anat_roi = str(anat_rois_dir / f'{roi_name}.nii.gz')
    func_roi = str(func_rois_dir / f'{roi_name}_func.nii.gz')
    subprocess.run([f'flirt -in {anat_roi} -ref {ref_vol} -applyxfm -init {anat2refvol_matrix} -o {func_roi}'], shell = True) # Convert anatomical ROI to functional space using inverted transformation parameters
    subprocess.run([f'fslmaths {func_roi} -mul 2 -thr `fslstats {func_roi} -p 99.6` -bin {func_roi}'], shell = True) # Binarize and refine functional ROI