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

from collections import OrderedDict
from nipype.interfaces import afni as afni
from nilearn.masking import apply_mask
import numpy as np
from pathlib import Path
from shutil import copyfile
import subprocess
import time
from typing import Tuple

#############################################################################################
# DESCRIPTION
#############################################################################################

# Corregistration pipeline that will be applied to all incoming fMRI DICOM volumes in real-time

#############################################################################################
# FUNCTIONS
#############################################################################################

def corregister_vol(vol_file: str, mask_file: str, ref_vol_file: str, preprocessed_dir: str) -> Tuple[np.array, list]:

    """
    Corregistration pipeline to be applied to raw DICOM volumes

    Steps:

        1 - Copy DICOM file to preprocessed_dir
        2 - Convert from DICOM format to NifTI
        3 - Deoblique NifTI file
        4 - Brain extraction
        5 - Corregister volume to reference volume file
        6 - Mask volume with a Region of Interest (R.O.I.) binarized mask
        7 - Smoothing (if required)

    Inputs:

        vol_file: raw fMRI volume file path (DICOM file)
        mask_file: R.O.I. mask to apply to vol_file (NifTI file, Uncompressed)
        ref_vol_file: reference volume to which vol_file will be corregistered to (NifTI file, Uncompressed)
        preprocessed_dir: path where preprocessed folder of this participant will be created (String)

    Returns:

        preproc_vol: already corregistered and masked volume (Numpy Array)
        corregistration_time: processing time for each corregistration pipeline step (List)
    """
    
    corregistration_time = OrderedDict() # Dictionary to store processing times for each corregistration pipeline step
    start_corregistration = time.time() # Corregistration start time

    # Set working files
    vol_file = Path(vol_file)
    mask_file = Path(mask_file)
    ref_vol_file = Path(ref_vol_file)
    preprocessed_dir = Path(preprocessed_dir)

    # Get volume name
    vol_name = vol_file.stem

    # Copy DICOM file to preprocessed_dir
    start_dcm_copy = time.time()
    dcm_copy = preprocessed_dir / (vol_name + '.dcm')
    copyfile(vol_file, dcm_copy)
    corregistration_time['dcm_copy_time'] = time.time() - start_dcm_copy

    # Load DICOM, convert to NifTI format, and store uncompressed NifTI in preprocessed_dir
    start_nifti_conver = time.time()
    subprocess.run([f'dcm2niix -z n -f {vol_name} -o {preprocessed_dir} -s y {dcm_copy}'], shell=True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL) # subprocess.run waits until the conversion process ends to continue with the next step
    nifti_file = preprocessed_dir / (vol_name + '.nii') # Uncompressed NifTI to increase processing speed
    corregistration_time['nifti_conver_time'] = time.time() - start_nifti_conver

    # Deoblique uncompressed NifTI file to match cardinal coordinates orientation
    start_deoblique = time.time()
    deoblique = afni.Warp() # Use AFNI 3dWarp command
    deoblique.terminal_output = 'file_split' # Uncomment to see STDOUT and STDERR in terminal
    deoblique.inputs.in_file = nifti_file
    deoblique.inputs.deoblique = True # Deoblique Nifti files
    deoblique.inputs.gridset = ref_vol_file # Copy vol grid from reference volume so volumes dimensions match between sessions
    deoblique.inputs.num_threads = 4
    deoblique.inputs.outputtype = 'NIFTI'
    deoblique_file = preprocessed_dir / (vol_name + '_deoblique.nii')
    deoblique.inputs.out_file = deoblique_file # Deobliqued volume in NifTI format
    deoblique.run()
    corregistration_time['deoblique_time'] = time.time() - start_deoblique

    # Perform brain extraction to improve session to session corregistration of functional data
    start_brainextraction = time.time()
    brainextraction = afni.Automask() # Use AFNI Automask command
    brainextraction.terminal_output = 'file_split' # Uncomment to see STDOUT and STDERR in terminal
    brainextraction.inputs.in_file = deoblique_file
    brainextraction.inputs.erode = 1 # Erode the mask inwards to avoid skull and tissue fragments. Check this parameter for each subject based 
                                     # on brain extraction performance during training session
    brainextraction.inputs.clfrac = 0.5 # Sets the clip level fraction (0.1 - 0.9). By default 0.5. The larger, the restrictive brain extraction is
    brainextraction.inputs.num_threads = 4
    brainextraction.inputs.outputtype = 'NIFTI'
    brain_file = preprocessed_dir / (vol_name + '_deoblique_brain.nii')
    brainmask_file = preprocessed_dir / (vol_name + '_deoblique_brainmask.nii')
    brainextraction.inputs.brain_file = brain_file # Just brain's data in NifTI format
    brainextraction.inputs.out_file = brainmask_file # Brain binarized mask in NifTI format
    brainextraction.run()
    corregistration_time['brainextraction_time'] = time.time() - start_brainextraction

    # Corregister this extracted brain to reference vol brain
    start_volreg = time.time()
    volreg = afni.Volreg() # Use AFNI 3dvolreg command
    volreg.terminal_output = 'file_split' # Uncomment to see STDOUT and STDERR in terminal
    volreg.inputs.in_file = brain_file
    volreg.inputs.basefile = ref_vol_file # Take reference volume as base file for corregistration
    volreg.inputs.args = '-heptic' # Spatial interpolation
    volreg.inputs.num_threads = 4
    volreg.inputs.outputtype = 'NIFTI'
    oned_file = preprocessed_dir / (vol_name + '_deoblique_brain_corregister.1D') 
    oned_matrix_file =  preprocessed_dir / (vol_name + '_deoblique_brain_corregister.aff12.1D')
    md1d_file = preprocessed_dir / (vol_name + '_deoblique_brain_corregister_md.1D')
    corregister_file = preprocessed_dir / (vol_name + '_deoblique_brain_corregister.nii')
    volreg.inputs.oned_file = oned_file # 1D movement parameters output file (-1Dfile command)
    volreg.inputs.oned_matrix_save = oned_matrix_file # Save the matrix transformation (-1Dmatrix_save command)
    volreg.inputs.md1d_file = md1d_file # Max displacement output file (-maxdisp1D command)
    volreg.inputs.out_file = corregister_file # Corregistered volume in NifTI format
    volreg.run()
    corregistration_time['volreg_time'] = time.time() - start_volreg
    
    # Mask & Smooth
    start_mask = time.time()
    mask_file = str(mask_file) # Transform Pathlib Path to string. Nilearn do not get on well with Pathlib
    corregister_file = str(corregister_file)
    preproc_vol = apply_mask(imgs = corregister_file, # Corregistered volume in NifTI format
                             mask_img = mask_file, # Binarized mask in NifTI format
                             smoothing_fwhm = None, # No smoothing here
                             ensure_finite = True)
    corregistration_time['mask_time'] = time.time() - start_mask

    # Corregistration end time
    corregistration_time['total_corregistration_time'] = time.time() - start_corregistration
    corregistration_time = [corregistration_time] # Convert dict to list to store all times
    
    return preproc_vol, corregistration_time
