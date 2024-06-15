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

import numpy as np
import os

from nomad.metainfo import (Quantity, Reference, SubSection)
from nomad.datamodel.data import ArchiveSection

from .. import BaseMeasurement
from .voltammetry import Voltammetry


class PhotoCurrentProperties(ArchiveSection):
    cell_type = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))

    ref_electrode = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007204'],
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))

    counter_electrode = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007203'],
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))

    electrolyte = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007224'],
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))

    electrolyte_concentration = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007244'],
        type=np.dtype(np.float64),
        unit='mol',

        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mol'

        ))

    modulation_frequency = Quantity(
        type=np.dtype(np.float64),
        unit='Hz',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='Hz'
        ))

    lock_in_phase = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity',
        ))

    potentiostat_i_range = Quantity(
        type=np.dtype(np.float64),
        unit='uA',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='uA'
        ))

    analog_output_conversion = Quantity(
        type=np.dtype(np.float64),
        unit='V/mA',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V/mA'
        ))

    average_number = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity'
        ))


class PhotoCurrent(BaseMeasurement):

    photo_current_properties = SubSection(
        section_def=PhotoCurrentProperties)

    data_files = Quantity(
        type=str,
        shape=["*"],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    reference_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    electro_measurements = Quantity(
        type=Reference(Voltammetry),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    energy = Quantity(
        type=np.dtype(
            np.float64),
        shape=['n_values'],
        unit='eV',
        a_plot=[
            {
                "label": "Energy",
                'x': 'wavelength',
                'y': 'voltage',
                'layout': {
                    'yaxis': {
                        'type': 'lin',
                        "title": "Energy"}},
                "config": {
                    "editable": True,
                    "scrollZoom": True}}])

    wavelength = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0000176'],
        type=np.dtype(
            np.float64),
        shape=['n_values'],
        unit='nm',
        a_plot=[
            {
                "label": "Wavelength",
                'x': 'wavelength',
                'y': 'voltage',
                'layout': {
                    'yaxis': {
                        'type': 'lin',
                        "title": "Wavelength"}},
                "config": {
                    "editable": True,
                    "scrollZoom": True}}])

    voltage = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007219'],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='V',
        a_plot=[{"label": "Voltage",
                 'x': 'energy', 'y': 'voltage', 'layout': {'yaxis': {'type': 'lin', "title": "Voltage"}},
                 "config": {
                     "editable": True,
                     "scrollZoom": True
                 }
                 }]
    )

    def derive_n_values(self):
        if self.current or self.ewe:
            return max(len(self.current_density), len(self.voltage))
        return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def normalize(self, archive, logger):
        super(PhotoCurrent, self).normalize(archive, logger)
        self.method = "Photo Current"

        if self.data_files and len(self.data_files) > 0:
            for data_file in self.data_files:
                try:
                    with archive.m_context.raw_file(data_file) as f:
                        if os.path.splitext(data_file)[-1] == ".mps":
                            from ..helper.mps_file_parser import read_mps_file
                            self.electro_meta_data = read_mps_file(f.name)
                            self.electro_meta_data_file_name = os.path.basename(
                                f.name)

                except Exception as e:
                    logger.error(e)

            for data_file in self.data_files:
                try:
                    with archive.m_context.raw_file(data_file) as f:

                        if os.path.splitext(data_file)[-1] == ".txt":
                            import pandas as pd
                            data = pd.read_csv(
                                f.name, delimiter="\t", header=0, skipfooter=1)
                            self.energy = np.array(data["Energy(eV)"])
                            self.wavelength = np.array(data["Wavelength(nm)"])
                            self.voltage = np.array(data["Voltage(V)"])
                except Exception as e:
                    logger.error(e)
