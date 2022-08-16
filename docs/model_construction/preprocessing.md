---
layout: default
title: Preprocessing
parent: Model Construction Session
nav_order: 1
---

# Preprocessing
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Description

Model construction session functional volumes are preprocessed in a similar fashion as they are preprocessed during real-time fMRI decoding neurofeedback training, to maximize similarity between pipelines and avoid potential confusion variables. That is to say, using the same neuroimage software and preprocessing steps.

As an starting point, a functional volume is set as reference volume to functional volumes of both model construction and neurofeedback training sessions.

Next, all functional volumes of the decoder construction session are individually corregistered to that reference volume and stacked together by functional run.

All volumes are labeled using log files of experimental paradigm used during model construction session runs. This enables to identify each volume by time from each trial onset, stimuli category, experimental condition...

Once all functional volumes are labeled, some volumes of interest are picked for model training. Volumes of interest are additionally preprocessed for decoding by detrending to volumes timeseries and Z-scored normalized.

Preprocessing scripts of model construction session can be found in 1.model_construction/scripts/1.preprocessing sorted by required execution order.

Further, the pyDecNef pipeline provides example raw data (i.e., DICOM files) of a model construction session following recommended data structure already set in preprocessing scripts. 

You just have to replace these data with yours, modify scripts to match your experimental settings, and you are ready to go.

## 1 - Set an example functional volume as reference

The first preprocessing step consists on selecting 