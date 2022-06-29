---
layout: default
title: Installation
parent: Introduction
---

# Installation
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Infrastructure

An ethernet local area network (LAN) needs to be wired between three computers: 

- MRI scanner host computer used to manage scanning sessions and MRI sequences configuration.

- The server computer which will be running real-time preprocessing and decoding scripts

- The client computer which will be running the experimental presentation software, and presenting stimuli and feedback to participant in the MRI scanner.

![Ethernet Local Area Network Diagram](/assets/images/ethernet_lan.png)

## MRI scanner host computer

As stated in diagram above, MRI scanner host computer should be able to copy fMRI DICOM files into a specific Server's folder in real-time. Real-time processing scripts running in server computer include a watcher class, which will be in charge of looking at that folder to initialize volume preprocessing as fast a new volume is copied.

Siemens and Prisma scanners host computers can use **ideacmdtool** in combination with FIRMM with that goal.

- <a href="https://firmm.readthedocs.io/en/3.2/installation/" target="_blank">FIRMM</a>
- <a href="https://firmm.readthedocs.io/en/3.2/siemens_ideacmdtool/" target="_blank">ideacmdtool</a>

## Python version

pyDecNef scripts are intended to be run in Python 3.6 or above using as minimum external libraries as possible and relying on [Python standard library](https://docs.python.org/3/library/) to maximize compatibility across Python versions. Python should be installed both in Server and Client computers.

## Server: fMRI volumes preprocessing and decoding computer

### System requirements

A computer with great performance and storage capabilities is recomended to play server's role as fMRI volumes will be collected and processed in real-time. Specifically, server computer should be able to perform volumes preprocessing and decoding in less than the selected fMRI repetition time (TR).

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

## Client: Experimental presentation computer

- <a href="https://osdoc.cogsci.nl/" target="_blank">Opensesame</a>
- <a href="https://www.psychopy.org/" target="_blank">PsychoPy</a>