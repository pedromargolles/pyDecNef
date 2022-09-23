## Description

The first step in all fMRI Decoding Neurofeedback Studies is constructing a machine learning model.

That model is trained by using functional data from a MRI session.

Then, the trained model is applied in real-time during several neurofeedback training sessions.

This folder (i.e., **sub-1**) contains example functional data and step by step scripts to preprocess fMRI volumes, select a brain Region of Interest (R.O.I.), and train a machine learning model using masked data from that R.O.I.

Given folders structure is stablished as you would use in a real experimental setting. In other words, one folder for each experimental subject containing both data from that subject and scripts.

You just have to replicate it for each of your participants by using your own model construction session data.

Having in place this architecture, the model construction is a really straightforward process.

Scripts can be run sequentially in order to train your model and just minimal changes in the scripts are needed to match your experimental paradigm.

