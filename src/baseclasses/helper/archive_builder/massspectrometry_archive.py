#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 17:33:35 2024

@author: a2853
"""

from baseclasses.chemical_energy import MassspectrometrySettings, MassspectrometrySpectrum


mass_mapping = {
    2: "H2",
    28: "N2",
    40: "Ar",
    32: "O2"
}


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
    for m in masses:
        try:
            mass_number = int(m.split(" ")[1])
        except Exception as e:
            raise e
        if mass_number in mass_mapping:
            spectra.append(MassspectrometrySpectrum(
                chemical_name=mass_mapping.get(mass_number),
                spectrum_data=data[m]
            ))
        else:
            spectra.append(MassspectrometrySpectrum(
                chemical_name=m,
                spectrum_data=data[m]
            ))
    return settings, spectra
