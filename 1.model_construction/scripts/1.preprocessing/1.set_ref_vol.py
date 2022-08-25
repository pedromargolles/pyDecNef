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

from nipype.interfaces import afni as afni
from pathlib import Path
import shutil
import subprocess

#############################################################################################
# DESCRIPTION
#############################################################################################

# Deoblique and perform brain extraction over a functional volume (i.e., first volume after MRI 
# scanner heatup volumes of first fMRI run in model construction session) to be the reference
# during next volumes co-registration both in model contruction and neurofeedback training 
# pre-processing
 
#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
raw_dir = exp_dir / 'data'
raw_func_vols_dir = raw_dir / 'func'
raw_func_vols_dir = Path(raw_func_vols_dir)
preprocessed_dir = exp_dir / 'preprocessed/'
ref_vol_dir = preprocessed_dir / 'ref_vol'
rt_resources = exp_dir / 'rt_resources'
rt_resources_coregistration = rt_resources / 'coregistration'
rt_resources_ref_vol_dir = rt_resources_coregistration / 'ref_vol'

# Create dirs
preprocessed_dir.mkdir(exist_ok = True, parents = True)
ref_vol_dir.mkdir(exist_ok = True, parents = True)
rt_resources.mkdir(exist_ok = True, parents = True)
rt_resources_coregistration.mkdir(exist_ok = True, parents = True)
rt_resources_ref_vol_dir.mkdir(exist_ok = True, parents = True)

#############################################################################################
# SETUP VARIABLES
#############################################################################################

n_heatup_vols = 5 # Number of fumctional volumes to consider as heatup volumes used for image
                  # stabilization of MRI scanner

#############################################################################################
# SELECT REFERENCE FUNCTIONAL VOLUME
#############################################################################################

# Pick first raw volume after a number heatup volumes to be the reference volume
raw_func_vols = sorted((raw_func_vols_dir / 'run_1').glob('**/*.dcm')) # Get and sort all DICOM files of the first fMRI model construction run
ref_vol = raw_func_vols[n_heatup_vols] # Set first DICOM after n_heatup_vols as reference functional volume

# Load ref_vol DICOM, convert to NIfTI using dcm2niix and store outputs in ref_vol_dir
subprocess.run([f"dcm2niix -z n -f 'ref_vol' -o {ref_vol_dir} -s y {ref_vol}"], shell = True)

# Deoblique converted NIfTI file
deoblique_vol = afni.Warp() # Use AFNI 3dWarp command
deoblique_vol.inputs.in_file = ref_vol_dir / 'ref_vol.nii' # Get NIfTI file
deoblique_vol.inputs.deoblique = True # Deoblique NIfTI file
deoblique_vol.inputs.outputtype = 'NIFTI'
ref_vol_deobliqued_file = ref_vol_dir / 'ref_vol_deobliqued.nii' # Use *.nii format instead of *.nii.gz to improve processing speed in during real-time decoding neurofeedback training session
deoblique_vol.inputs.out_file = ref_vol_deobliqued_file
deoblique_vol.run()

# Perform brain extraction to improve corregistration of functional data
brainextraction = afni.Automask() # Use AFNI Automask command
brainextraction.inputs.in_file = ref_vol_deobliqued_file
brainextraction.inputs.erode = 1 # Erode the mask inwards to avoid skull and tissue fragments. Check this parameter for each subject based 
                                 # on brain extraction performance during model construction session.
brainextraction.inputs.clfrac = 0.5 # Sets the clip level fraction (0.1 - 0.9). By default 0.5. The larger, the restrictive brain extraction is
brainextraction.inputs.outputtype = 'NIFTI'
brain_file = ref_vol_dir / 'ref_vol_deobliqued_brain.nii'
brainmask_file = ref_vol_dir / 'ref_vol_deobliqued_brainmask.nii' # Use *.nii format instead of *.nii.gz to improve processing speed in during real-time decoding neurofeedback training session
brainextraction.inputs.brain_file = brain_file # Just brain's data
brainextraction.inputs.out_file = brainmask_file # Brain binarized mask
brainextraction.run()

#############################################################################################
# COPY REFERENCE FUNCTIONAL VOLUME TO FOLDER OF RESOURCES REQUIRED FOR REAL-TIME PREPROCESSING
#############################################################################################

# Copy reference volume deobliqued brain to rt_resources folder
shutil.copy(ref_vol, str(rt_resources_ref_vol_dir / 'ref_vol_deobliqued_brain.nii'))