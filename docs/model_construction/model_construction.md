---
layout: default
title: Model construction session
nav_order: 3
has_children: True
permalink: docs/model_construction
---

# Model Construction Session

---

## Description

Decoding neurofeedback experiments usually start from this session.

An experimental session takes place to obtain data to train an univariate or in this case, a multivariate machine learning model that will be then applied during real-time neurofeedback training sessions by participant.

Participants are normally required to perform an experimental task which enable researchers to evoke specific brain states and capture specific patterns of brain activation which can be used to train regression or classification models.

Model construction session can be merged onto a single session with the first real-time neurofeedback training session. In these cases, models are trained inmediately after data collection improving data collection speed. However, this is at cost of having enough sampling size, and limits data pre-processing and model performance. In this pipeline, we treat model construction session as it was performed in a different day from other neurofeedback training sessions.

<center>
<br>
<img src="../assets/images/model_construction_session.png" alt="Model Construction Session" width="1100">
</center>

It is important to note that decoding neurofeedback experiments require good performance models (as a criteria, above 70% AUC). Cognitive states should be easely, consistently and accurately discriminated by your model. Otherwise, most of the time you will be giving participant an erroneus feedback to control their performance biasing experimental results. Experimental paradigms of model construction session should be created with that in mind.

pyDecNef includes an example model construction paradigm in OpenSesame along with raw data and scripts for data processing.