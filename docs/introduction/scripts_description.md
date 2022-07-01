---
layout: default
title: Scripts description
nav_order: 2
has_children: false
permalink: docs/scripts-description
---

# Scripts description
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

pyDecNef library provides a complete framework to perform decoded neurofeedback studies. pyDecNef scripts repository can be accessed [through this link](https://github.com/pedromargolles/pyDecNef). Below are depicted pyDecNef scripts functionality and purpose by each repository folder. 

## Model construction (1.model_construction)

To fill

## Neurofeedback training (2.neurofeedback_training)

### 1.realtime_fMRI_scripts

Contains Python scripts required by server computer to perform fMRI volumes preprocessing and decoding analysis in real-time. This scripts are intended to be run in parallel to experimental design files in 2.experimental_paradigm folder.

##### main.py

Integrates config, classes and pipelines modules together.

#### Config module

##### modules/config/exp_config.py

Main experimental configuration file. Here it should be detailed: number of MRI scanner heatup volumes, number of baseline volumes, hemodynamic response function peak limits, fMRI TRs, type of zscoring procedure, type of decoding procedure... 

Also routes to essential files to perform decoding neurofeedback for each participant are specified in this file. For example: regions of interest binarized masks, trained machine learning model, a reference volume from decoder construction session, zscoring values...

##### modules/config/connection_config.py

Enables the connection between scripts running in server and client computers and data sharing between them.

##### modules/config/listener.py

Defines 

##### modules/config/shared_instances.py

Serves to 

#### Classes module

##### modules/classes/classes.py

Here are defined attributes and methods of Python classes which interact to perform 

#### Pipelines module

##### modules/pipelines/corregistration_pipeline.py

Basic pipeline using dcm2niix, AFNI, nipype and nilearn to perform neurofeedback training session volumes real-time corregistration to a reference volume from decoder construction session and masking of that volume using a region of interest mask file.

##### modules/pipelines/preproc_vol_to_timeseries_pipeline.py

Contains 3 different pipelines to detrend and zscoring each neurofeedback training session volume using timeseries information of that fMRI session run.

##### modules/pipelines/trial_decoding_pipeline.py

Contains 3 different pipelines to decode neurofeedback training session trials and volumes.

### 2.experimental_paradigm

Contain 

### 3.fMRI_simulator_realdata

*generate.py* - rver computer

## Postprocessing scripts (3.postprocessing)

To fill