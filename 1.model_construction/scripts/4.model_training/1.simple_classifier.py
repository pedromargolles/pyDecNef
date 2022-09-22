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

import joblib
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, cross_validate
from sklearn.model_selection import LeaveOneGroupOut
import numpy as np

#############################################################################################
# DESCRIPTION
#############################################################################################

# Training a simple classifier using LogisticRegression and storing model for later use
# during neurofeedback training sessions

#############################################################################################
# SET FILE STRUCTURE
#############################################################################################

exp_dir = Path().absolute().parent.parent
data_dir = exp_dir / 'data'
preprocessed_dir = data_dir / 'preprocessed/'
masked_vols_of_interest_dir = preprocessed_dir / 'masked_vols_of_interest'
model_dir = preprocessed_dir / 'model'
rt_resources = exp_dir / 'rt_resources'
rt_resources_model = rt_resources / 'model'

# Create dirs
model_dir.mkdir(exist_ok = True, parents = True)
rt_resources_model.mkdir(exist_ok = True, parents = True)

#############################################################################################
# SETUP VARIABLES
#############################################################################################

# ROI mask_name
ROI_mask_name = 'ROI'

# Output model name
model_name = 'model'

#############################################################################################
# LOAD MASKED VOLUMES OF INTEREST AND THEIR LABELS
#############################################################################################

X = np.load(np.save(str(masked_vols_of_interest_dir / f'preprocessed_vols_of_interest_{ROI_mask_name}.npy'))) # Preprocessed & masked volumes
labels = pd.read_csv(str(masked_vols_of_interest_dir / f'labels_vols_of_interest.csv')) # Volumes labels
y = labels.trial_category # Category targets corresponding to each volume
runs = labels.run # Runs corresponding to each volume

#############################################################################################
# DISCARD CATEGORY OF VOLUMES FOR BINARY CLASSIFICATION
#############################################################################################

discard_idxs = np.where(y != 2) # Discard volumes labeled as 2
X = X[discard_idxs]
y = y[discard_idxs]
runs = runs[discard_idxs]

#############################################################################################
# LEAVE-ONE-RUN-OUT CROSS-VALIDATION
#############################################################################################

loro = LeaveOneGroupOut()
loro.split(X, y, runs)

#############################################################################################
# LOGISTIC REGRESSION MODEL
#############################################################################################

clf = LogisticRegression(solver = 'liblinear', random_state = 123)

#############################################################################################
# EVALUATE MODEL WITH ROC_AUC BY USING ONE-RUN-OUT CROSS-VALIDATION
#############################################################################################

scores_by_run = cross_validate(clf, X, y, cv = loro, scoring = 'roc_auc') # One-run-out cross-validation using 
                                                                          # 'roc_auc' as scoring metric
mean_score = scores_by_run.mean() # Mean ROC-AUC across runs
std_score = scores_by_run.std() # STD ROC-AUC across runs

print('\n')
print('----------------------')
print('Model:', model_name)
print('Mean ROC-AUC:', mean_score, 'STD ROC-AUC:', std_score)
print('----------------------')
print('\n')

#############################################################################################
# TRAIN MODEL WITH DATA FROM ALL RUNS
#############################################################################################

clf.fit(X, y)

#############################################################################################
# SAVE MODEL
#############################################################################################

# Save trained model in preprocessed folder
joblib.dump(clf, str(model_dir / f'{ROI_mask_name}_{model_name}.joblib'))

# Copy trained model for volumes decoding in real time to rt_resources folder
joblib.dump(clf, str(rt_resources_model / f'{ROI_mask_name}_{model_name}.joblib')) 