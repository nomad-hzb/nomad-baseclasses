# -*- coding: utf-8 -*-
#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from nomad.datamodel.metainfo.common import ProvenanceTracker
from nomad.datamodel.results import (BandGapDeprecated, BandGap, BandStructureElectronic,
                                     ElectronicProperties, OptoelectronicProperties,
                                     Properties, Results, SolarCell)
import numpy as np

from nomad.units import ureg
from nomad.datamodel.results import OptoelectronicProperties, Properties, Results, SolarCell, BandGap, BandStructureElectronic, ElectronicProperties


def add_solar_cell(archive):
    '''Adds metainfo structure for solar cell data.'''
    if not archive.results:
        archive.results = Results()
    if not archive.results.properties:
        archive.results.properties = Properties()
    if not archive.results.properties.optoelectronic:
        archive.results.properties.optoelectronic = OptoelectronicProperties()
    if not archive.results.properties.optoelectronic.solar_cell:
        archive.results.properties.optoelectronic.solar_cell = SolarCell()


# from nomad.datamodel.metainfo.plot import PlotSection


def add_band_gap(archive, band_gap):
    '''Adds a band gap value (in eV) with the additional section structure for solar
    cell data.eV=
    '''
    if band_gap is not None:
        bg = BandGapDeprecated(value=np.float64(band_gap) * ureg('eV'))
        band_gap = BandGap(value=np.float64(band_gap) * ureg('eV'),
                           provenance=ProvenanceTracker(label='solar_cell_database'))  # TODO: check label
        band_structure = BandStructureElectronic(band_gap=[bg])  # TODO: to be removed after reparsing
        electronic = ElectronicProperties(band_structure_electronic=[band_structure],
                                          band_gap=[band_gap])
        archive.results.properties.electronic = electronic


# def addOpticalBandGap(archive):
#     '''Adds metainfo structure for solar cell data.'''
#     if not archive.results:
#         archive.results = Results()
#     if not archive.results.properties:
#         archive.results.properties = Properties()
#     if not archive.results.properties.optoelectronic:
#         archive.results.properties.optoelectronic = OptoelectronicProperties()
#     if not archive.results.properties.optoelectronic.solar_cell:
#         archive.results.properties.optoelectronic.band_gap_optical = BandGapOptical()
#     props = archive.results.properties.available_properties
#     if not props:
#         props = []
#     if 'band_gab_optical' not in props:
#         props.append('band_gab_optical')
#     archive.results.properties.available_properties = props
