---
layout: default
title: fMRI volumes preprocessing
parent: Model construction session
nav_order: 1
---

# fMRI volumes preprocessing
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Preprocessing pipeline

Model construction session functional volumes are preprocessed using the same neuroimage software and preprocessing steps as they are preprocessed during real-time fMRI decoding neurofeedback training. This enables to maximize similarity between pipelines and avoid potential confusion variables.

As an starting point, a functional volume is set as reference volume to functional volumes of both model construction and neurofeedback training sessions.

Next, all functional volumes of the decoder construction session are individually corregistered to that reference volume and stacked together by functional run. All volumes are labeled using log files of experimental paradigm used during model construction session runs to identify each volume by its time from corresponding trial onset; its stimuli category; the experimental condition... 

Once all functional volumes are labeled, volumes are linear detrended by fMRI run. Then, some volumes of interest are selected for model construction. Usually these are volumes falling within the Hemodynamic Response Function peak of each trial. Lastly, volumes of interest are Z-scored normalized at voxel level.

Preprocessing scripts of model construction session can be found in *1.model_construction/scripts/1.preprocessing* sorted by required execution order.

Further, the pyDecNef pipeline provides example raw data (i.e., DICOM files) of a model construction session following recommended data structure already set in preprocessing scripts. 

You just have to replace these data with yours, modify scripts to match your experimental settings, and you are ready to go.

<center>
<br>
<img src="../../assets/images/model_construction_preprocessing.png" alt="Model Construction Preprocessing Pipeline Diagram" width="1100">
</center>

    *NOTE:*

    Ensure that conda environment containing required dependencies for model construction is activated, and dcm2niix and AFNI neuroimage software are preloaded before using preprocessing scripts.

## 1 - Reference volume extraction

The first preprocessing pipeline step consists on selecting selecting a raw functional volume to serve as reference to all other volumes of model construction session, but also to volumes of neurofeedback training sessions.

Usually, fMRI runs start with the acquisition of a number of volumes (5 - 10 volumes) to allow for image stabilization that are then discarded.

In this pipeline, we select the first raw volume after MRI scanner heatup as reference image.

This DICOM volume is converted to NIfTI format using dcm2niix and skull stripped using AFNI to facilitate co-registration to following volumes.