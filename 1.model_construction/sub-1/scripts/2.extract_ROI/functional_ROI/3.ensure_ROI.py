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
from nilearn.image import load_img, new_img_like
import numpy as np

#############################################################################################
# DESCRIPTION
#############################################################################################

# Sometimes ROIs images generated with FSL (specially if serveral masks images overlaping 
# partially are merged together) can contain non-zero values distinct from one. 
# This script ensures that all masks are trully binarized.

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent.parent
data_dir = exp_dir / 'data'
preprocessed_dir = data_dir / 'preprocessed/'
ref_vol_dir = preprocessed_dir / 'ref_vol'
rois_dir = preprocessed_dir / 'ROIs_masks'
func_rois_dir = rois_dir / 'functional_ROIs'
subject_id = exp_dir.name.split('-')[1]
rt_resources = data_dir / f'rt_resources/{subject_id}'
rt_resources_rois = rt_resources / 'rois'

#############################################################################################
# PREPARE ROIs MASKS
#############################################################################################

brainmask_ref_vol_file = str(ref_vol_dir / 'ref_vol_deobliqued_brainmask.nii')
brain_mask = load_img(brainmask_ref_vol_file) # Load reference volume

for roi_file in func_rois_dir.glob('*.nii.gz'): # For each ROI image in masks folder
    filename = roi_file.name.split('.nii.gz')[0] # Get mask name
    mask_img = load_img(str(roi_file))
    mask_data = mask_img.get_fdata()
    mask_data = np.where(mask_data != 0, 1, mask_data) # Set as 1 values all non-zero mask values
    new_mask_img = new_img_like(brain_mask, mask_data, copy_header = True)
    new_mask_img.to_filename(str(rois_dir / f'{filename}_func.nii')) # Save corrected mask
    new_mask_img.to_filename(str(rt_resources_rois / f'{filename}_func.nii')) # Save corrected mask to rt_resources folder