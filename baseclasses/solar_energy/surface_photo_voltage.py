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
from nomad.datamodel.data import ArchiveSection


from nomad.metainfo import (
    Quantity,
    Section,
    SubSection)
from .. import BaseMeasurement

class trSPVProperties(ArchiveSection):
    laser_energy = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        a_eln=dict(component='NumberEditQuantity',
                   defaultDisplayUnit='nm'))
    
    laser_pulse_frequency = Quantity(
        type=np.dtype(np.float64),
        unit=('Hz'),
        a_eln=dict(component='NumberEditQuantity',
                   defaultDisplayUnit='Hz'))
    
    laser_pulse_intensity = Quantity(
        type=np.dtype(np.float64),
        unit=('uJ/cm**2'),
        a_eln=dict(component='NumberEditQuantity',
                   defaultDisplayUnit='uJ/cm**2'))
    

class trSPVData(ArchiveSection):

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='s')

    

    voltage = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='mV', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False, 'type': 'log'}}, "config": {
                    "editable": True, "scrollZoom": True}}])



class trSPVMeasurement(BaseMeasurement):
    '''PL Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    properties = SubSection(
        section_def=trSPVProperties)
    
    
    data = SubSection(
        section_def=trSPVData)
    
    def normalize(self, archive, logger):
        self.method = "PL Measurement"
        super(trSPVMeasurement, self).normalize(archive, logger)
