#############################################################################################
# AUTHORS: Ning Mei, Pedro Margolles & David Soto
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
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, initializers, optimizers, losses, metrics
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

#############################################################################################
# DESCRIPTION
#############################################################################################

# T

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

masked_preprocessed_vols_of_interest_file = str(masked_vols_of_interest_dir / f'preprocessed_vols_of_interest_{ROI_mask_name}.npy')
labels_vols_of_interest_file = str(masked_vols_of_interest_dir / f'labels_vols_of_interest.csv')

#############################################################################################
# MODEL CONSTRUCTION FUNCTIONS
#############################################################################################

def build_logistic_regression_model(input_size = 100, 
                                    output_size = 2, 
                                    special = False, 
                                    kernel_regularizer = None, 
                                    activity_regularizer = None, 
                                    print_model = False,
                                    ):

    """
    This function builds a custom logistic regression classifier
    
    Architecture:

    input_layer --> logistic_layer/output_layer

    Inputs:

        input_size: The 2nd dimension of the input data (int)
        output_size: The number of classes (int)
        special: Just in case you want to use this special combination of activation functions (Bool)
        kernel_regularizer: None or tf.keras.regularizers to control for the layer weights
        activity_regularizer: None or tf.keras.regularizers to control for the output sparsity
        print_model: Whether to show the model architecture in a summary table (Bool)

    Returns:

        logistic_regression: A Keras model that has .fit() (tf.keras.models.Model)
    """

    tf.random.set_seed(12345) # Random seed

    input_layer = layers.Input(shape = (input_size,),
                               name = 'input_layer'
                              )
    
    if special:
        middle_layer = layers.Dense(units = output_size,
                                    activation = 'selu',
                                    use_bias = True,
                                    kernel_initializer = initializers.lecun_normal(),
                                    kernel_regularizer = kernel_regularizer,
                                    activity_regularizer = activity_regularizer,
                                    name = 'middle_layer',
                                    )(input_layer)

        logistic_layer = layers.Activation('softmax',
                                           name = 'logistic_layer'
                                          )(middle_layer)
    else:
        logistic_layer = layers.Dense(units = output_size,
                                      activation = 'softmax',
                                      use_bias = True,
                                      kernel_initializer = initializers.he_normal(),
                                      kernel_regularizer = kernel_regularizer,
                                      activity_regularizer = activity_regularizer,
                                      name = 'logistic_layer'
                                      )(input_layer)
    
    logistic_regression_model = models.Model(input_layer,
                                             logistic_layer,
                                             name = 'logistic_regression'
                                            )
    if print_model:
        print(logistic_regression_model.summary())

    return logistic_regression_model



def make_callbacks_list(model_name, 
                        monitor = 'val_loss',
                        mode = 'min',
                        verbose=0,
                        min_delta=1e-4,
                        patience=50,
                        frequency = 1
                       ):
    
    """
    This function creates a callback list for the keras model
    
    Inputs:

        model_name: The directory where we want to save the model and its name (str)
        monitor: The criterion we use for saving and stopping the model. Default = 'val_loss' (str)
        mode: min - Lower the better; max - Higher the better. Default = 'min' (str)
        verboser: Print out the monitoring messages. Default = 0 (int or bool)
        min_delta: Minimum change for early stopping. Default = 1e-4 (float)
        patience: The temporal window of the minimum change monitoring. Default = 50 (int)
        frequency: Temporal window steps of the minimum change monitoring. Default = 1 (int)

    Returns:

    callbacks_list: A list of callbacks (list of tensorflow.keras.callbacks)
    """

    # Save the best model
    checkPoint = ModelCheckpoint(model_name,
                                 monitor = monitor,
                                 save_best_only = True,
                                 mode = mode,
                                 verbose = verbose,
                                 )
    # Early stop
    earlyStop = EarlyStopping(monitor = monitor,
                              min_delta = min_delta,
                              patience = patience,
                              verbose = verbose, 
                              mode = mode,
                             )

    callbacks_list = [checkPoint, 
                      earlyStop
                     ]

    return callbacks_list



def compile_logistic_regression_model(model,
                                      model_name = 'temp.h5',
                                      optimizer = None,
                                      loss_function = None,
                                      metric = None,
                                      callbacks = None,
                                      learning_rate = 1e-2,
                                      tol = 1e-4,
                                      patience = 5,
                                     ):
    
    """
    Compile the custom logistic regression model
    
    Inputs:

        model: Model (tf.keras.models.Model)
        model_name: The directory where we want to save the model and its name (str)
        optimizer: Keras optimizer. Default = SGD (None or tf.keras.optimizers)
        loss_function: Keras Loss. Default = BinaryCrossentropy (None or tf.keras.losses)
        metric: Keras metric. Default = AUC (None or tf.keras.metrics)
        callbacks: Keras callbacks. Default = [checkpoint, earlystopping] (None or list)
        learning_rate: Learning rate. Default = 1e-2 (float)
        tol: For determining when to stop training. Default = 1e-4 (float)
        patience: For determining when to stop training. Default = 5 (int)

    Returns:
    model: A compiled keras model (tf.keras.models.Model)
    callbacks_list: A list of callbacks (list of tensorflow.keras.callbacks)
    """

    if optimizer is None:
        optimizer = optimizers.SGD(learning_rate = learning_rate)
    
    if loss_function is None:
        loss_function = losses.BinaryCrossentropy()

    if metric is None:
        metric = metrics.AUC()

    if callbacks is None:
        callbacks_list = make_callbacks_list(
                                             model_name = model_name,
                                             monitor = 'val_loss',
                                             mode = 'min',
                                             verbose = 0,
                                             min_delta = tol,
                                             patience = patience,
                                             frequency = 1,
                                            )

    compiled_model = model.compile(optimizer = optimizer,
                                   loss = loss_function,
                                   metrics = [metric],
                                  )

    return compiled_model, callbacks_list



#############################################################################################
# MODEL CONSTRUCTION FUNCTIONS
#############################################################################################











X = np.load(masked_preprocessed_vols_of_interest_file) # Preprocessed & masked volumes
labels = pd.read_csv(labels_vols_of_interest_file) # Volumes labels
y = labels.trial_category # Category targets corresponding to each volume
runs = labels.run # Run corresponding to each volume

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