---
layout: page
title: NMMA
description: A framework for fast fitting transients
img: assets/img/projects/nmma/nmmaTitle.jpg
importance: 1
category: work
---

*Updated October 2022*

## Overview

The bulk of my work as a graduate student has thusfar focused on work as part of the Nuclear Multi-Messenger Astronomy (NMMA) collaboration. The NMMA collaboration is led, in part, by Assistant Professor Michael Coughlin, who is my advisor at UMN.

As part of the NMMA collaboration, I have led development on a pipeline to perform rapid fitting of lightcurves from ZTF to determine the fundamental nature of observed objects and inform follow-up observations. This is accomplished by using the machine-learning methods that are part of the NMMA framework, which has been developed in a larger collaboration spanning multiple institutions and continents. 

There are a variety of “fast” transient light curves that exist in these datasets, and confidently identifying their types enables prioritization of notable objects. My scientific interests focus strongly on kilonovae (KNe), highly energetic transient events where a binary system made up of a pair of neutron stars or a neutron star and a black hole merge. Importantly, KNe produce GWs detectable by current instruments, as was the case in 2017 when the first GW in conjunction with a KN was detected.

The NMMA pipeline was developed with the goal of providing rapid fitting of lightcurves to identify potential KN for follow-up observations. I have worked with several collaborators to bring the pipeline online, where we conduct nightly searches for KNe and other fast transients. The pipeline is currently equipped to retrieve ZTF data; it fits daily candidates to before pushing the information to an NMMA slack channel where it can be easily reviewed. I am also working to create a machine learning training set to develop a more robust system for prioritizing candidates for follow-up observations. I am leading a first-authored paper on the NMMA pipeline; this paper will be submitted before the end of the calendar year. The pipeline still has opportunities for further development.

Currently, our primary computing resource is the Minnesota Supercomputing Institute (MSI) cluster. While MSI is capable, its queue-based system can sometimes cause delays in fitting, which is troublesome given the relatively constrained timeframe for deciding on follow-up triggers. My work will benefit greatly from dedicated computing time on a cluster or dedicated hardware. The underlying code scales well with additional resources, and powerful processors would allow for more detailed fits of lightcurves in the same timeframe. This will also enable the pipeline to integrate with the growing ecosystem of observation coordination software referred to as “Marshals.” Primarily, I’ve focused on development with SkyPortal, a project heavily employed by the ZTF collaboration and other surveys, though the pipeline can be integrated with other Marshals. SkyPortal is an open-source web application that allows for the storage and management of observational data with a growing focus on MMA datasets and time-domain astronomy in general. 

I will integrate my existing pipeline so follow-up observations of potential GW companions will be easily accessible in an online database and enable astronomers to perform real-time fitting of data to different models integrated in the NMMA pipeline. The addition of dynamic model integration to the pipeline will be a powerful tool within Marshals as the user community can rapidly and efficiently test new models on uploaded observations within the database. 

Work on the NMMA pipeline has supported the IGWN O4 observing run. My toolkit integrated with Marshals like SkyPortal serves as a centralized framework to access lightcurves from multiple surveys and fit them to bespoke models, greatly enhancing the scientific return from multi-messenger observations. 

This work led to our first-authored publication, [*"An online framework for fitting fast transient light curves"* (MNRAS 2024)](https://doi.org/10.1093/mnras/stae1164), followed by our comprehensive catalog paper, [*"IIb or not IIb: A Catalog of ZTF Kilonova Imposters"* (PASP 2025)](https://doi.org/10.1088/1538-3873/ad7405).

To explore an interactive light curve fitter and see the real-time multi-messenger response architecture in action, visit the [**Interactive Demos Showcase**](/demos/).