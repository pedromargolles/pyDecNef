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
import subprocess

#############################################################################################
# DESCRIPTION
#############################################################################################

# Co-register all raw functional volumes of model construction session to the reference volume 
# deobliqued brain

#############################################################################################
# SETUP VARIABLES
#############################################################################################

# Parameter to perform brain extraction before co-registration
erode = 1 # Erode the brain mask inwards to avoid skull and tissue fragments. 
          # Check this parameter for each subject based on brain extraction performance during 
          # model construction session

clfrac = 0.5 # Sets the clip level fraction (0.1 - 0.9). By default 0.5. 
             # The larger, the restrictive brain extraction is

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
data_dir = exp_dir / 'data'
raw_dir = data_dir / 'raw'
raw_func_vols_dir = raw_dir / 'func'
preprocessed_dir = data_dir / 'preprocessed/'
ref_vol_dir = preprocessed_dir / '1.ref_vol'
preprocessed_func_dir = preprocessed_dir / '2.preprocessed_func'
rt_resources = data_dir / 'rt_resources'
rt_resources_coregistration = rt_resources / 'coregistration'

# Create dirs
preprocessed_func_dir.mkdir(exist_ok = True, parents = True)

#############################################################################################
# CO-REGISTER ALL DICOM FILES OF MODEL CONSTRUCTION SESSION TO REFERENCE VOLUME
#############################################################################################

# Co-registration pipeline to be applied to all raw DICOM volumes

# Steps:
#   1 - Copy each volume DICOM file to preprocessed_dir
#   2 - Convert that volume from DICOM to NifTI format
#   3 - Deoblique NIfTI file
#   4 - Perform brain extraction
#   5 - Co-register volume to reference volume

ref_vol = str(ref_vol_dir / 'ref_vol_deobliqued_brain.nii') # Set reference volume for co-registration

for folder in raw_func_vols_dir.iterdir():
    if folder.is_dir(): # Iterate over all functional runs folders

        run_dir = preprocessed_func_dir / folder.stem # Get functional run name and create a new folder in preprocessed_dir
        run_dir.mkdir(exist_ok = True, parents = True)
        
        for vol_file in folder.glob('*.dcm'): # Co-register each volume in that run to reference volume
            
            # Convert volume DICOM to NIfTI using dcm2niix and store it in run_dir
            vol_name = vol_file.stem
            subprocess.run([f'dcm2niix -z n -f {vol_name} -o {run_dir} -s y {vol_file}'], shell = True)
                                        
            # Deoblique converted Nifti file
            deoblique = afni.Warp() # Use AFNI 3dWarp command
            nifti_file = str(run_dir / (vol_name + '.nii')) # To save each vol as .nii instead to .nii.gz to load faster
            deoblique.inputs.in_file = nifti_file # Get NIfTI file
            deoblique.inputs.deoblique = True # Deoblique NIfTI files
            deoblique.inputs.gridset = ref_vol # Copy ref_vol grid so volumes dimensions match between runs and sessions
            deoblique.inputs.outputtype = 'NIFTI'
            deobliqued_file = str(run_dir / (vol_name + '_deobliqued.nii')) # Use *.nii format instead of *.nii.gz to improve processing speed in during real-time decoding neurofeedback training session
            deoblique.inputs.out_file = deobliqued_file
            deoblique.run()
            
            # Perform brain extraction to improve co-registration of functional data
            brainextraction = afni.Automask() # Use AFNI Automask command
            brainextraction.inputs.in_file = deobliqued_file
            brainextraction.inputs.erode = erode # Erode the mask inwards to avoid skull and tissue fragments. Check this parameter for each subject based 
                                                 # on brain extraction performance during model construction session
            brainextraction.inputs.clfrac = clfrac # Sets the clip level fraction (0.1 - 0.9). By default 0.5. The larger, the restrictive brain extraction is
            brainextraction.inputs.outputtype = 'NIFTI'
            brain_file = str(run_dir / (vol_name + '_deobliqued_brain.nii'))
            brainmask_file = str(run_dir / (vol_name + '_deobliqued_brainmask.nii')) # Use *.nii format instead of *.nii.gz to improve processing speed in during real-time decoding neurofeedback training session
            brainextraction.inputs.brain_file = brain_file # Just brain's data
            brainextraction.inputs.out_file = brainmask_file # Brain binarized mask
            brainextraction.run()
        
            # Co-register functional volume brain to reference volume brain
            volreg = afni.Volreg() # Use AFNI 3dvolreg command
            volreg.inputs.in_file = brain_file
            volreg.inputs.basefile = ref_vol # Take reference volume as base file during co-registration
            volreg.inputs.args = '-heptic' # Spatial interpolation
            volreg.inputs.outputtype = 'NIFTI'
            oned_file = str(run_dir / (vol_name + '_deoblique_brain_coregistered.1D')) 
            oned_matrix_file =  str(run_dir / (vol_name + '_deoblique_brain_coregistered.aff12.1D'))
            md1d_file = str(run_dir / (vol_name + '_deoblique_brain_coregistered_md.1D'))
            coregister_file = str(run_dir / (vol_name + '_deoblique_brain_coregistered.nii'))
            volreg.inputs.oned_file = oned_file # 1D movement parameters output file -1Dfile
            volreg.inputs.oned_matrix_save = oned_matrix_file # Save the matrix transformation. -1Dmatrix_save
            volreg.inputs.md1d_file = md1d_file # Max displacement output file -maxdisp1D
            volreg.inputs.out_file = coregister_file # Co-registered vol
            volreg.run()
            
            for file in run_dir.glob('*'): # To save space, remove all files from preprocessed runs folders which does not contain 'coregister.nii' string in their name
                if 'coregistered.nii' not in str(file):
                    file.unlink()

#############################################################################################
# SAVE CO-REGISTRATION BRAIN EXTRACTION CONFIGURATION FOR REAL-TIME PREPROCESSING
#############################################################################################
with open(str(rt_resources_coregistration / "bet_config.txt"), "w") as file:
    content = [f"erode = {erode}\n", f"clfrac = {clfrac}\n"]
    file.writelines(content)
    file.close()