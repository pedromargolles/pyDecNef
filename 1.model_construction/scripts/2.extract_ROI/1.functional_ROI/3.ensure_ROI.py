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

exp_dir = Path().absolute().parent.parent
data_dir = exp_dir / 'data'
preprocessed_dir = data_dir / 'preprocessed/'
ref_vol_dir = preprocessed_dir / '1.ref_vol'
rois_dir = preprocessed_dir / '6.ROIs_masks'

#############################################################################################
# PREPARE ROIs MASKS
#############################################################################################

brain_mask = load_img(str(ref_vol_dir / 'ref_vol_deoblique_brainmask.nii')) # Load reference volume

for roi in rois_dir.glob('*.nii.gz'): # For each ROI image in masks folder
    filename = roi.name.split('.nii.gz')[0] # Get mask name
    mask_img = load_img(str(roi))
    mask_data = mask_img.get_fdata()
    mask_data = np.where(mask_data != 0, 1, mask_data) # Set as 1 values all non-zero mask values
    new_mask_img = new_img_like(brain_mask, mask_data, copy_header = True)
    new_mask_img.to_filename(str(rois_dir / f'{filename}_mask_adapted.nii')) # Save corrected mask