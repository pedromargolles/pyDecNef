---
layout: default
title: Installation
parent: Introduction
---

# Requirements
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Infrastructure

INFRASTRUCTURE IMAGE

## MRI scanner management computer
- <a href="https://firmm.readthedocs.io/en/3.2/installation/" target="_blank">FIRMM</a>
- <a href="https://firmm.readthedocs.io/en/3.2/siemens_ideacmdtool/" target="_blank">ideacmdtool</a>

## Python version

pyDecNef scripts are intended to be run in Python 3.6 or above using as minimum external libraries as possible and relying on [Python standard library](https://docs.python.org/3/library/) to maximize compatibility across systems and Python versions.

## fMRI volumes pre-processing and decoding computer (i.e., Server)

### System requirements

A computer with great performance and storage capabilities is recomended to play server's role as fMRI volumes will be collected and processed in real-time. Specifically, server computer should be able to perform volumes pre-processing and decoding in less than the fMRI repetition time (TR).

pyDecNef real-time scripts has succesfully been used in a computer running CentOS operating system with following specifications:

SPECIFICATIONS

### Global requirements

- <a href="https://numpy.org/" target="_blank">Numpy</a>
- <a href="https://pandas.pydata.org/" target="_blank">Pandas</a>

### Data pre-processing

- <a href="https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/main_toc.html" target="_blank">AFNI</a>
- <a href="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/" target="_blank">FSL</a>
- <a href="https://www.nitrc.org/plugins/mwiki/index.php/dcm2nii:MainPage" target="_blank">dcm2niix</a>
- <a href="https://nipype.readthedocs.io/en/latest/" target="_blank">Nipype</a>
- <a href="https://nilearn.github.io/stable/index.html" target="_blank">Nilearn</a>

### Decoding

- <a href="https://scikit-learn.org/stable/" target="_blank">scikit-learn</a>
- <a href="https://www.tensorflow.org/" target="_blank">Tensorflow</a>

### Results visualization

- <a href="https://pypi.org/project/colorama/" target="_blank">Colorama</a>
- <a href="https://matplotlib.org/" target="_blank">Matplotlib</a>
- <a href="https://seaborn.pydata.org/" target="_blank">seaborn</a>
- <a href="https://plotly.com/python/getting-started/" target="_blank">plotly</a>
- <a href="https://dash.plotly.com/installation" target="_blank">Dash</a>

## Experimental presentation computer (i.e., Client)

- <a href="https://osdoc.cogsci.nl/" target="_blank">Opensesame</a>
- <a href="https://www.psychopy.org/" target="_blank">PsychoPy</a>