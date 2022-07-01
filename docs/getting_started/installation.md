---
layout: default
title: Installation
nav_order: 1
parent: Getting started
---

# Installation
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Infrastructure

An ethernet local area network (LAN) is required between three computers: 

- MRI scanner host computer used to manage scanning sessions and MRI sequences configuration.

- The server computer which will be running real-time volumes preprocessing and decoding scripts.

- The client computer running the experimental software, and presenting stimuli and feedback to participant in the MRI scanner.

<center>
<br>
<img src="../assets/images/ethernet_lan.png" alt="Ethernet Local Area Network Diagram" width="500">
</center>

## MRI scanner

While pyDecNef framework might work with any type of MRI scanner, as it does not rely on any specific brand functionality, the integration with FIRMM software required to transfer volumes from MRI scanner host computer to the server computer, works better with Siemens or GE scanner models.

## MRI scanner host computer

As suggested, MRI scanner host computer needs to be configured to copy in real-time functional DICOM files into a specific server computer folder. 

Real-time processing scripts running in server computer include a watcher class, which will be in charge of looking at that folder to initialize volume preprocessing as fast a new volume is written out.

With that goal, Siemens Trio and Prisma scanners host computers can use ideacmdtool program in combination with FIRMM software, while GE scanners can make use rsync protocol.

- <a href="https://firmm.readthedocs.io/en/3.2/siemens_ideacmdtool/" target="_blank">Using ideacmdtool + FIRMM with SIEMENS scanners</a>

- <a href="https://firmm.readthedocs.io/en/3.2/ge_dicom_streaming/" target="_blank">Using rsync + FIRMM with GE scanners</a>

## Server computer

### System requirements

A computer with great performance and storage capabilities is recomended to play server's role as fMRI volumes will be collected and processed in real-time. 

Specifically, the server computer requires to perform volumes preprocessing and decoding in less than the selected fMRI repetition time (TR).

Ideally server computer should use a Linux system as Debian/Ubuntu 16+ or Redhat/CentOS 7+ to be able to run either Docker or Singularity for FIRMM software and either samba or rsync protocols for DICOM transfer.

pyDecNef real-time scripts have succesfully been used in a computer running CentOS Linux 7 operating system with following specifications:

    Memory: 31 GB
    Processor: Intel© Core™ i9-9900K CPU @ 3.60GHz x 16
    Graphics: Intel© HD Graphics (Coffeelake 3x8 GT2)
    GNOME: Version 3.28.2
    OS type: 64-bit
    Disk: 2.0TB

### FIRMM

FIRMM version 2.1 or greater needs to be installed in the server computer to receive fMRI volumes from MRI scanner host computer by means of samba or rsync transfer methods as a function MRI scanner is Siemens or GE respectively.

- <a href="https://firmm.readthedocs.io/en/3.2/installation/" target="_blank">FIRMM installation</a>

### Neuroimage analysis software

To maximize preprocessing speed of fMRI volumes and keep the versatilty which Python language provides to the researcher, pyDecNef makes use of several specialized neuroimage analysis software written in C which are then integrated within a single Python workflow by means of Nipype library.

- <a href="https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/main_toc.html" target="_blank">AFNI installation</a>
- <a href="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation" target="_blank">FSL installation</a>
- <a href="https://www.nitrc.org/plugins/mwiki/index.php/dcm2nii:MainPage" target="_blank">dcm2niix installation</a>

### Python

#### Python version

pyDecNef scripts are intended to be run in Python 3.6 or above using as minimum external libraries as possible and relying on Python standard library to maximize compatibility across Python versions. 

Python should be installed both in server and client computers.

#### Python dependencies

##### Global requirements

- <a href="https://numpy.org/" target="_blank">Numpy</a>
- <a href="https://pandas.pydata.org/" target="_blank">Pandas</a>

##### Data preprocessing

- <a href="https://nipype.readthedocs.io/en/latest/" target="_blank">Nipype</a>
- <a href="https://nilearn.github.io/stable/index.html" target="_blank">Nilearn</a>

##### Decoding

- <a href="https://scikit-learn.org/stable/" target="_blank">scikit-learn</a>
- <a href="https://www.tensorflow.org/" target="_blank">Tensorflow</a>

##### Results visualization

- <a href="https://pypi.org/project/colorama/" target="_blank">Colorama</a>
- <a href="https://matplotlib.org/" target="_blank">Matplotlib</a>
- <a href="https://seaborn.pydata.org/" target="_blank">seaborn</a>
- <a href="https://plotly.com/python/getting-started/" target="_blank">plotly</a>
- <a href="https://dash.plotly.com/installation" target="_blank">Dash</a>

## Client computer

For experimental development and presentation of stimuli to the participant, cross-platform packages based on Python language for development of neuroscience, psychology, psychophysics or linguistics paradigms are recommended:

- <a href="https://osdoc.cogsci.nl/3.3/download/" target="_blank">Opensesame installation</a>
- <a href="https://www.psychopy.org/download.html" target="_blank">PsychoPy installation</a>

## Decoder construction & postprocessing computer

System used to run decoder construction session & postprocessing scripts requires the same software and python dependencies as server computer (except for FIRMM software). 

Decoder construction session pipeline was built to maximize its similarity to neurofeedback training pipeline and avoid confusion factors.

Additionally other neuroimage analysis software and python libraries are recommended:

- <a href="https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall" target="_blank">Freesurfer installation</a>
- <a href="https://brainiak.org/" target="_blank">Brainiak installation</a>