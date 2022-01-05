############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021, Python fMRI-Neurofeedback
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: 
############################################################################

#############################################################################################
# IMPORT DEPENDENCIES
#############################################################################################

from pathlib import Path
from nipype.interfaces import afni as afni
from nilearn.masking import apply_mask
from shutil import copyfile
from collections import OrderedDict
import subprocess
import time

#############################################################################################
# FUNCTIONS
#############################################################################################

def corregister_vol(vol_file,
                    mask_file,
                    ref_vol_file,
                    preprocessed_dir,
                    ):

    """
    Inputs:
    vol_file: fMRI volume path (as Pathlib Path)
    mask_file: mask to apply to vol_file (as Pathlib Path)
    ref_vol_file: Volume to which vol_file will be corregistered (as Pathlib Path)
    preprocessed_dir: Path where preprocessed folder for this participant will be created (as Pathlib Path)

    Returns:
    preproc_vol: Array. Already preprocessed volume.
    """
    corregistration_time = OrderedDict()

    # Preprocessing start time
    start_corregistration = time.time()

    # Set working files
    vol_file = Path(vol_file)
    mask_file = Path(mask_file)
    ref_vol_file = Path(ref_vol_file)
    preprocessed_dir = Path(preprocessed_dir)

    # Volume name
    vol_name = vol_file.stem

    # Copy DICOM in preprocessed_dir
    start_dcm_copy = time.time()
    dcm_copy = preprocessed_dir / (vol_name + '.dcm')
    copyfile(vol_file, dcm_copy)
    corregistration_time['dcm_copy_time'] = time.time() - start_dcm_copy

    # Load vol DICOM, convert to Nifti and store the result in preprocessed_dir (subprocess.run will wait until the process ends to continue with next step)
    start_nifti_conver = time.time()
    subprocess.run([f'dcm2niix -z n -f {vol_name} -o {preprocessed_dir} -s y {dcm_copy}'], shell=True)
    nifti_file = preprocessed_dir / (vol_name + '.nii')
    corregistration_time['nifti_conver_time'] = time.time() - start_nifti_conver

    # Deoblique converted Nifti file
    start_deoblique = time.time()
    deoblique = afni.Warp() # Use AFNI 3dWarp command
    deoblique.inputs.in_file = nifti_file
    deoblique.inputs.deoblique = True # Deoblique Nifti files
    deoblique.inputs.gridset = ref_vol_file # Copy train_reference_vol grid so vols dimensions match between sessions
    deoblique.inputs.num_threads = 4 # Set number of threads for processing
    deoblique.inputs.outputtype = 'NIFTI'
    deoblique_file = preprocessed_dir / (vol_name + '_deoblique.nii')
    deoblique.inputs.out_file = deoblique_file
    deoblique.run()
    corregistration_time['deoblique_time'] = time.time() - start_deoblique

    # Perform brain extraction to improve session to session registration of functional data
    start_brainextraction = time.time()
    brainextraction = afni.Automask() # Use AFNI Automask command
    brainextraction.inputs.in_file = deoblique_file
    brainextraction.inputs.erode = 1 # Erode the mask inwards to avoid skull and tissue fragments. Check this parameter for each subject based on brain extraction performance during training session.
    brainextraction.inputs.clfrac = 0.5 # Sets the clip level fraction (0.1 - 0.9). By default 0.5. The larger the restrictive brain extraction is.
    brainextraction.inputs.num_threads = 4 # Set number of threads for processing
    brainextraction.inputs.outputtype = 'NIFTI'
    brain_file = preprocessed_dir / (vol_name + '_deoblique_brain.nii')
    brainmask_file = preprocessed_dir / (vol_name + '_deoblique_brainmask.nii')
    brainextraction.inputs.brain_file = brain_file # Just brain's data
    brainextraction.inputs.out_file = brainmask_file # Brain binarized mask
    brainextraction.run()
    corregistration_time['brainextraction_time'] = time.time() - start_brainextraction

    # Corregister test func vol brain to train reference vol brain
    start_volreg = time.time()
    volreg = afni.Volreg() # Use AFNI 3dvolreg command
    volreg.inputs.in_file = brain_file
    volreg.inputs.basefile = ref_vol_file # Take train_reference_vol as base file for registration
    volreg.inputs.args = '-heptic' # Spatial interpolation
    volreg.inputs.num_threads = 4 # Set number of threads for processing
    volreg.inputs.outputtype = 'NIFTI'
    oned_file = preprocessed_dir / (vol_name + '_deoblique_brain_corregister.1D') 
    oned_matrix_file =  preprocessed_dir / (vol_name + '_deoblique_brain_corregister.aff12.1D')
    md1d_file = preprocessed_dir / (vol_name + '_deoblique_brain_corregister_md.1D')
    corregister_file = preprocessed_dir / (vol_name + '_deoblique_brain_corregister.nii')
    volreg.inputs.oned_file = oned_file # 1D movement parameters output file -1Dfile
    volreg.inputs.oned_matrix_save = oned_matrix_file # Save the matrix transformation. -1Dmatrix_save
    volreg.inputs.md1d_file = md1d_file # Max displacement output file -maxdisp1D
    volreg.inputs.out_file = corregister_file # Corregistered vol
    volreg.run()
    corregistration_time['volreg_time'] = time.time() - start_volreg
    
    # Mask & Smooth
    start_mask = time.time()
    mask_file = str(mask_file) # Transform path from Pathlib Path to string
    corregister_file = str(corregister_file) # Transform path from Pathlib Path to string
    preproc_vol = apply_mask(imgs = corregister_file,
                             mask_img = mask_file,
                             smoothing_fwhm = None,
                             ensure_finite = True)
    corregistration_time['mask_time'] = time.time() - start_mask

    # Preprocessing end time
    corregistration_time['total_corregistration_time'] = time.time() - start_corregistration
    corregistration_time = [corregistration_time] # Convert dict to list to store all times in a pandas dataframe
    
    return preproc_vol, corregistration_time
