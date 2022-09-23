## What data you will find here?

Here you will find 4 folders. 

Each folder corresponds to a step for neurofeedback model construction.

Folders' scripts are intended to be run sequentially. For that reason folders and their scripts are numbered.

* **1.preprocessing** - Contains scripts to pre-process RAW fMRI volumes. In other words, reference volume extraction, co-registration of all model construction session volumes to reference volume, and data pre-processing for model construction. 

* **2.extract_ROI** - Two approaches to extract your neurofeedback training Region of Interest are provided. *Functional approach*, on which R.O.I. is extracted based on whole brain decoding performance in decoding searchlight analyses. *Anatomical approach*, on which R.O.I. is theoretically motivated and extracted based on participant's brain parcellation.

* **3.ROI_masking** - Model construction data is masked to account just for voxels data in your R.O.I.

* **4.model_training** -  Standard and advanced scripts to construct and train your machine learning model. In this example, a classifier.