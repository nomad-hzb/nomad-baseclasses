#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 17:33:35 2024

@author: a2853
"""

from baseclasses.chemical_energy import MassspectrometrySettings, MassspectrometrySpectrum


def get_masssectromentry_archive(metadata, data):
    settings = MassspectrometrySettings(
        channel_count=metadata.get("Channel count"),
        accuracy=metadata.get("Accuracy"),
        sensitivity=metadata.get("Sensitivity (A/mbar)"),
        full_scale_reading=metadata.get("Full scale reading (mbar)"),
        detector_gain=metadata.get("Detector gain"),
        ion_source=metadata.get("Ion Source"),
        extractor_voltage=metadata.get("Extractor voltage"),
        detector_voltage=metadata.get("Detector voltage"),
        filament=metadata.get("Filament"),
    )

    masses = [m for m in data.columns if "mass" in m.lower()]
    chemicals = metadata.get("Measurement")
    if not chemicals:
        return settings, []
    spectra = []
    for m, elm in zip(masses, chemicals.split(",")):
        spectra.append(MassspectrometrySpectrum(
            chemical_name=elm,
            spectrum_data=data[m]
        ))

    return settings, spectra
