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

## Model construction (1.model_construction):

To fill

## Neurofeedback training (2.neurofeedback_training):

### 1.realtime_fMRI_scripts

Contains Python scripts required by server computer to perform fMRI volumes preprocessing and decoding analysis in real-time. This scripts are intended to be run in parallel to experimental design files in 2.experimental_paradigm folder.

*main.py* - Integrates config, classes and pipelines modules together.

##### Config module
<br>
*modules/config/connection_config.py* - rver computer
<br>
*modules/config/exp_config.py* - rver computer
<br>
*modules/config/listener.py* - rver computer
<br>
*modules/config/shared_instances.py* - rver computer

##### Classes module
<br>
*modules/classes/classes.py* - rver computer

##### Pipelines module
<br>
*modules/pipelines/corregistration_pipeline.py* - rver computer

*modules/pipelines/preproc_vol_to_timeseries_pipeline.py* - rver computer

*modules/pipelines/trial_decoding_pipeline.py* - rver computer

### 2.experimental_paradigm

Contain 

### 3.fMRI_simulator_realdata

*generate.py* - rver computer

## Postprocessing scripts (3.postprocessing):

To fill