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

import os
import numpy as np

from nomad.metainfo import (
    Quantity, SubSection, MEnum, Section, Datetime)
from nomad.datamodel.data import ArchiveSection

from .potentiostat_measurement import PotentiostatMeasurement


class EISProperties(ArchiveSection):

    dc_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    dc_voltage_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    initial_frequency = Quantity(
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='Hz'))

    final_frequency = Quantity(
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='Hz'))

    points_per_decade = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    ac_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('mV'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV'))

    sample_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))


class EISResults(ArchiveSection):

    uncompensated_resistance = Quantity(
        type=np.dtype(np.float64),
        unit=('ohm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ohm'))


class EISCycle(ArchiveSection):

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='s')

    frequency = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='Hz', a_plot=[
            {
                "label": "Frequency", 'x': 'time', 'y': 'frequency', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_real = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='ohm', a_plot=[
            {
                "label": "Z Real", 'x': 'time', 'y': 'z_real', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_imaginary = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='ohm', a_plot=[
            {
                "label": "Z Imaginary", 'x': 'time', 'y': 'z_imaginary', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_modulus = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='ohm', a_plot=[
            {
                "label": "Z Modulus", 'x': 'time', 'y': 'z_modulus', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_angle = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='degree', a_plot=[
            {
                "label": "Z Angle", 'x': 'time', 'y': 'z_angle', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])


class EISPropertiesWithData(EISProperties):
    m_def = Section(label_quantity='name',
                    a_plot=[{'label': 'Nyquist Plot',
                             'x': 'data/z_real',
                             'y': 'data/z_imaginary',
                             'layout': {'yaxis': {"fixedrange": False,
                                                  "title": "-Im(Z) (Ω)"},
                                        'xaxis': {"fixedrange": False,
                                                  "title": "Re(Z) (Ω)"}}},
                            {'label': 'Bode Plot',
                             'x': ['data/frequency',
                                   'data/frequency'],
                             'y': ['./data/z_modulus',
                                   './data/z_angle'],
                             'layout': {"showlegend": True,
                                        'yaxis': {"fixedrange": False},
                                        'xaxis': {"fixedrange": False,
                                                  'type': 'log'}},
                             }])

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    name = Quantity(
        type=str,
        description='A short human readable and descriptive name.',
        a_eln=dict(component='StringEditQuantity', label='Short name'))

    datetime = Quantity(
        type=Datetime,
        description='The date and time associated with this section.',
        a_eln=dict(component='DateTimeEditQuantity'))

    data = SubSection(
        section_def=EISCycle)

    results = SubSection(
        section_def=EISResults)


class ElectrochemicalImpedanceSpectroscopy(PotentiostatMeasurement):

    metadata_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='s')

    frequency = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='Hz', a_plot=[
            {
                "label": "Frequency", 'x': 'time', 'y': 'frequency', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_real = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='ohm', a_plot=[
            {
                "label": "Z Real", 'x': 'time', 'y': 'z_real', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_imaginary = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='ohm', a_plot=[
            {
                "label": "Z Imaginary", 'x': 'time', 'y': 'z_imaginary', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_modulus = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='ohm', a_plot=[
            {
                "label": "Z Modulus", 'x': 'time', 'y': 'z_modulus', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    z_angle = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='degree', a_plot=[
            {
                "label": "Z Angle", 'x': 'time', 'y': 'z_angle', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "scrollZoom": True}}])

    properties = SubSection(
        section_def=EISProperties)

    results = SubSection(
        section_def=EISResults)

    def derive_n_values(self):
        if self.time or self.frequency:
            return max(len(self.time), len(self.frequency))
        return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def normalize(self, archive, logger):
        self.method = "Electrochemical Impedance Spectroscopy"
        super(
            ElectrochemicalImpedanceSpectroscopy,
            self).normalize(
            archive,
            logger)

        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:

                    if os.path.splitext(self.data_file)[-1] == ".DTA":
                        from ..helper.gamry_parser import get_header_and_data
                        from ..helper.gamry_archive import get_eis_data, get_meta_data

                        metadata, data = get_header_and_data(filename=f.name)
                        data = data[0]
                        get_eis_data(data, self)
                        get_meta_data(metadata, self)

                        if "EISPOT" in metadata["TAG"] and self.properties is None:
                            from ..helper.gamry_archive import get_eis_properties
                            properties = EISProperties()
                            get_eis_properties(metadata, properties)
                            self.properties = properties

                    if os.path.splitext(self.data_file)[-1] == ".mpt":
                        from ..helper.mps_file_parser import read_mpt_file
                        from ..helper.mpt_get_archive import get_eis_data, get_meta_data, get_eis_properties

                        metadata, data, technique = read_mpt_file(
                            filename=f.name)
                        get_eis_data(data, self)
                        get_meta_data(metadata, self)

                        if "Potentio" in technique and self.properties is None:
                            properties = EISProperties()
                            get_eis_properties(metadata, properties)
                            self.properties = properties

            except Exception as e:
                logger.error(e)


class ElectrochemicalImpedanceSpectroscopyMultiple(PotentiostatMeasurement):

    measurements = SubSection(
        section_def=EISPropertiesWithData, repeats=True)

    def normalize(self, archive, logger):
        super(ElectrochemicalImpedanceSpectroscopyMultiple,
              self).normalize(archive, logger)
        self.method = "Multiple Electrochemical Impedance Spectroscopy"
