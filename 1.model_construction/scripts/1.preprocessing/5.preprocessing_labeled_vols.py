############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
############################################################################

#############################################################################################
# IMPORT DEPENDENCIES
#############################################################################################

import pandas as pd
from pathlib import Path
from nilearn.image import load_img, concat_imgs, new_img_like
from nilearn.input_data import NiftiMasker
from nilearn.signal import _detrend
import numpy as np

#############################################################################################
# DESCRIPTION
#############################################################################################

# Preprocess labeled volumes and extract volumes of interest for model construction

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
preprocessed_dir = exp_dir / 'preprocessed/'
preprocessed_func_dir = preprocessed_dir / 'preprocessed_func'
ref_vol_dir = preprocessed_dir / 'ref_vol'
labeled_dir = preprocessed_dir / 'labeled_vols_of_interest'
vols_of_interest_dir = preprocessed_dir / 'preprocessed_vols_of_interest'

# Create dirs
vols_of_interest_dir.mkdir(exist_ok = True, parents = True)

#############################################################################################
# GET LABELED AND CO-REGISTERED FUNCTIONAL DATA
#############################################################################################

labeled_vols = sorted([str(run) for run in labeled_dir.glob('*.nii.gz')]) # Sort labeled runs
vols_of_interest_csv = sorted([str(run) for run in labeled_dir.glob('*_vols_of_interest.csv')]) # Sort volumes of interest CSV files by run
runs = list(zip(labeled_vols, vols_of_interest_csv))

#############################################################################################
# MAPPING VOLUMES' VOXELS IN THE 3D SPACE TO 2D SPACE
#############################################################################################

ref_vol = load_img(str(ref_vol_dir / 'ref_vol_deobliqued_brain.nii'))
dummy_mask = np.ones(ref_vol.shape[0:3]) # Create a matrix of one values with the same ref_vol dimensions
dummy_mask = new_img_like(ref_vol, dummy_mask, copy_header = True) # Create a dummy mask for NIfTI to numpy array conversion of whole-brain information and vice versa

# Use NiLearn NiftiMasker class to convert NiLearn images to flatten numpy arrays and unconvert again to NiLearn image format
# Using this trick you can easely map each voxel in the 3D space (i.e., NiLearn images) to the 2D space (i.e., flatten numpy arrays)
nifti_masker = NiftiMasker(mask_img = dummy_mask,
                           smoothing_fwhm = None, # Don't preprocess data at this point
                           standardize = False,  # Don't preprocess data at this point
                           detrend = False, # Don't preprocess data at this point
                           )

nifti_masker.fit(ref_vol) # Fit NiftiMasker to ref_vol dimensions

#############################################################################################
# PREPROCESS LABELED FUNCTIONAL VOLUMES
#############################################################################################

# Preprocessing pipeline for model construction to be applied to all fMRI runs

# Steps:
#   1 - Linear detrending of labeled functional volumes by fMRI run
#   2 - Stack all runs volumes of interest together and perform Z-scoring standardization

def zscore_func(array):

    """
    Z-scoring standardization function
    
    Inputs:

        array: 2D numpy array of volumes (n_samples, n_voxels) to standardize

    Returns:

        zscored_vols: Z-scored array
        zscoring_mean: BOLD signal mean by voxel
        zscoring_std: BOLD signal STD by voxel
    """

    mean_array = array.mean(axis = 0) # BOLD signal mean by voxel
    std_array = array.std(axis = 0) # BOLD signal STD by voxel
    std_array[std_array < np.finfo(np.float64).eps] = 1. # Avoid numerical problems
    mean_centered_array = array - mean_array # Mean centering
    zscored_vols = mean_centered_array / std_array
    return zscored_vols, mean_array, std_array

vols_of_interest = []
for labeled_vols, vols_of_interest_csv in runs: # Preprocess labeled volumes by fMRI run
    print('\nProcessing:', labeled_vols, vols_of_interest_csv)

    labeled_vols = load_img(labeled_vols) # Load labeled volumes and their respective labels
    vols_of_interest_csv = pd.read_csv(vols_of_interest_csv)

    # Transform 4D Nilearn images to 2D numpy arrays
    labeled_vols = nifti_masker.transform(labeled_vols) # Convert labeled volumes to flatten numpy array
    vols_of_interest_idxs = vols_of_interest_csv.vol_idx.values # Get volumes of interests indexes of that run

    # Detrending step
    labeled_vols = _detrend(labeled_vols, inplace = False, type = 'linear', n_batches = 10) # Linearly detrend whole run timeseries
    vols_of_interest.append(labeled_vols[vols_of_interest_idxs]) # Keep just that run volumes of interest for z-scoring
    
vols_of_interest = np.vstack(vols_of_interest) # Stack together all volumes of interest of all runs
    
# Zscoring step
preprocessed_vols_of_interest, mean_vols_of_interest, std_vols_of_interest = zscore_func(vols_of_interest) # Z-scoring standardization of all volumes of interest

# Inverse transformation from 2D to 4D space
preprocessed_vols_of_interest = nifti_masker.inverse_transform(preprocessed_vols_of_interest) # Convert 2D z-scored array of volumes to a 4D image using NiLearn NiftiMasker inverse transformation
mean_vols_of_interest = nifti_masker.inverse_transform(mean_vols_of_interest) # Convert also BOLD signal mean by voxel to a 3D image 
std_vols_of_interest = nifti_masker.inverse_transform(std_vols_of_interest) # Convert also BOLD signal STD by voxel to a 3D image 

#############################################################################################
# SAVE PRE-PROCESSED DATA
#############################################################################################

preprocessed_vols_of_interest.to_filename(str(vols_of_interest_dir / 'preprocessed_vols_of_interest.nii.gz')) # Save preprocessed volumes of interest
mean_vols_of_interest.to_filename(str(vols_of_interest_dir / 'mean_vols_of_interest.nii.gz')) # Save whole-brain BOLD signal mean by voxel
std_vols_of_interest.to_filename(str(vols_of_interest_dir / 'std_vols_of_interest.nii.gz')) # Save whole-brain BOLD signal STD by voxel

labels_vols_of_interest = [pd.read_csv(str(run_behav)) for run_behav in vols_of_interest_dir.glob('*.csv')] # Stack volumes of interest labels CSVs files
labels_vols_of_interest = pd.concat(labels_vols_of_interest, ignore_index = True)
labels_vols_of_interest.to_csv(str(vols_of_interest_dir / 'labels_vols_of_interest.csv'))