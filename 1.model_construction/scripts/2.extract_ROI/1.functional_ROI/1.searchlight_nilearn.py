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
from nilearn.decoding import SearchLight
from nilearn.image import load_img, new_img_like
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, make_scorer
from sklearn.model_selection import LeaveOneGroupOut

#############################################################################################
# DESCRIPTION
#############################################################################################

# Perform a fast searchlight analysis for functional ROI determination by using LogisticRegression
# LogisticRegression for binary classification as decoding model 
# and leave-one-run-out cross-validation

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
preprocessed_dir = exp_dir / 'preprocessed/'
ref_vol_dir = preprocessed_dir / 'ref_vol'
vols_of_interest_dir = preprocessed_dir / 'preprocessed_vols_of_interest'
decoding_results_dir = exp_dir / 'decoding_results'
searchlight_dir = decoding_results_dir / 'searchlight'
rois_dir = preprocessed_dir / 'ROIs_masks'

# Create dirs
decoding_results_dir.mkdir(exist_ok = True, parents = True)
searchlight_dir.mkdir(exist_ok = True, parents = True)
rois_dir.mkdir(exist_ok = True, parents = True)

#############################################################################################
# SETUP VARIABLES
#############################################################################################

# Relevant variables for searchlight analysis
searchlight_radius = 9 # Radius of the searchlight ball (in millimeters). It is recommended
                       # to test different spheres sizes to search for better performance

#############################################################################################
# LOAD PREPROCESSED VOLS OF INTEREST AND CORRESPONDING LABELS
#############################################################################################

preprocessed_vols_of_interest = load_img(str(vols_of_interest_dir / 'preprocessed_vols_of_interest.nii.gz'))
labels_vols_of_interest = pd.read_csv(str(vols_of_interest_dir / 'labels_vols_of_interest.csv'))
brain_mask = load_img(str(ref_vol_dir / 'ref_vol_deobliqued_brainmask.nii'))

#############################################################################################
# PREPARE DATA FOR CLASSIFICATION
#############################################################################################

# Keep just volumes belonging to trials category of 0 or 1
labels_vols_of_interest = labels_vols_of_interest[(labels_vols_of_interest.trial_category == 0) | (labels_vols_of_interest.trial_category == 1)]
preprocessed_vols_of_interest_array = preprocessed_vols_of_interest.get_fdata()
preprocessed_vols_of_interest_array = preprocessed_vols_of_interest[:, :, :, labels_vols_of_interest.index.values] # Select preprocessed volumes
preprocessed_vols_of_interest = new_img_like(preprocessed_vols_of_interest, preprocessed_vols_of_interest_array, copy_header = True)
labels_vols_of_interest.reset_index(inplace = True) # Reset vols of interest labels indexes so they match again with preprocessed_vols_of_interest indexes

# Data for training
train_x = preprocessed_vols_of_interest # Training samples
train_y = labels_vols_of_interest.trial_category.values # Training targets
cv_groups = labels_vols_of_interest.run # Grouping variable to use during cross-validation procedure

#############################################################################################
# DECODING MODEL
#############################################################################################

logistic_model = LogisticRegression(C = 1.0, # Set decoding model
                                    max_iter = 5000,
                                    penalty = 'l2',
                                    solver = 'lbfgs',
                                    random_state = 12345,
                                    )

#############################################################################################
# SETUP SEARCHLIGHT
#############################################################################################

searchlight = SearchLight(mask_img = brain_mask, # To remove non-brain voxels from searchlight
                          radius = searchlight_radius, # Size of searchlight sphere
                          estimator = logistic_model, # Model to train within each searchlight
                          n_jobs = -1, # Maximum number of processors
                          scoring = make_scorer(accuracy_score), # Performance metric
                          verbose = 1,
                          cv = LeaveOneGroupOut(), # Leave-one-group-out cross-validation
                         )

#############################################################################################
# INITIALIZE SEARCHLIGHT
#############################################################################################

searchlight.fit(train_x, 
                train_y, 
                groups = cv_groups
               )

#############################################################################################
# SAVE SEARCHLIGHT RESULTS AS NIFTI FILE
#############################################################################################

searchlight_results = new_img_like(brain_mask, searchlight.scores_) # Match results to brain mask sizes
searchlight_results.to_filename(str(searchlight_dir / f'searchlight_leaveonerunout_radius_{searchlight_radius}.nii.gz'))
