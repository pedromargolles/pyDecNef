---
layout: default
title: Scripts description
nav_order: 2
has_children: false
permalink: docs/scripts_description
---

# Scripts description
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

pyDecNef library provides a complete framework to perform decoded neurofeedback studies. pyDecNef scripts repository can be accessed <a href="https://github.com/pedromargolles/pyDecNef" target="_blank">through this link</a>. Below are depicted pyDecNef scripts functionality and purpose by each repository folder.

## Neurofeedback training (2.neurofeedback_training)

### 1.realtime_fMRI_scripts

Contains Python scripts required by server computer to perform preprocessing and decoding of neurofeedback training sessions volumes in real-time. This scripts are intended to be run in parallel to experimental design files in *2.experimental_paradigm* folder.

##### main.py

Integrates config, classes and pipelines modules together.

#### Config module

##### exp_config.py

Main experimental configuration file. Here it should be detailed number of MRI scanner heatup volumes, number of baseline volumes, hemodynamic response function peak limits, fMRI TRs, type of zscoring procedure, type of decoding procedure... 

Also routes to essential files to perform decoding neurofeedback for each participant are specified in this file. For example regions of interest binarized masks, trained machine learning model, a reference volume from decoder construction session, zscoring values...

##### connection_config.py

Enables the connection between scripts running in server and client computers and data sharing between them.

##### listener.py

Listener module match specific client requests (i.e., experimental software requests) with custom server actions.

##### shared_instances.py

Serves to share as global variables class objects instantiated in *main.py* file across all *1.realtime_fMRI_scripts* modules.

#### Classes module

##### classes.py

Here are defined attributes and methods of Python classes which interact to store information and processing volumes in real-time: independent volumes, volumes timeseries, independent trials, file watcher, client listener, data logger.

#### Pipelines module

##### corregistration_pipeline.py

Basic pipeline using dcm2niix, AFNI, nipype and nilearn to perform volumes real-time corregistration to a reference volume from decoder construction session and masking of that volume using a region of interest mask file.

##### preproc_vol_to_timeseries_pipeline.py

Contains 3 different pipelines to detrend and zscoring each neurofeedback training session volume using timeseries information of that fMRI session run.

##### trial_decoding_pipeline.py

Contains 3 different pipelines to decode neurofeedback training trials and volumes using previously trained machine learning model.

### 2.experimental_paradigm

Contain example static and dynamic neurofeedback paradigms for Opensesame/Psychopy software which can be readapted for your experimental purposes.

### 3.fMRI_simulator_realdata

##### generate.py

It simulates a fMRI scanner working in real-time. 

Serves to off-line test your decoded neurofeedback experimental paradigm and an accurate synchronization between scripts from *1.realtime_fMRI_scripts* and *2.experimental_paradigm* folders using previous sessions RAW volumes from a specific participant (ex., from decoder construction session).