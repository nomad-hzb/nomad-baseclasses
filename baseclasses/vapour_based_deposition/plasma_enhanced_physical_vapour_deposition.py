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

from nomad.metainfo import (Quantity, SubSection, Section)
from nomad.datamodel.data import ArchiveSection

from .. import LayerDeposition


class LogData(ArchiveSection):
    m_def = Section(label_quantity='name',
                    a_plot=[
                        {
                            'x': 'time',
                            'y': ['power', 'pressure'],
                            'layout': {
                                "showlegend": True,
                                'yaxis': {
                                    "fixedrange": False},
                                'xaxis': {
                                    "fixedrange": False}},
                        }])
    name = Quantity(type=str)

    power_mean = Quantity(
        #Link to ontology class 'power'
        links = ['http://purl.obolibrary.org/obo/PATO_0001024'],
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    power_var = Quantity(
        #Link to ontology class 'power'
        links = ['http://purl.obolibrary.org/obo/PATO_0001024'],
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    pressure_mean = Quantity(
        #Link to ontology class 'pressure'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025'],
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    pressure_var = Quantity(
        #Link to ontology class 'pressure'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025'],
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    temperature_mean = Quantity(
        #Link to ontology class 'temperature'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    temperature_var = Quantity(
        #Link to ontology class 'temperature'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    power = Quantity(
        #Link to ontology class 'power' and 'power setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001024','https://purl.archive.org/tfsco/TFSCO_00002104'],
        type=np.dtype(
            np.float64),
        shape=['*'],
        unit=('W'),
        a_plot=[
            {
                'x': 'time',
                'y': 'power',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    pressure = Quantity(
        #Link to ontology class 'pressure' and 'pressure setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025','https://purl.archive.org/tfsco/TFSCO_00005040'],
        type=np.dtype(
            np.float64),
        shape=['*'],
        unit=('mbar'),
        a_plot=[
            {
                'x': 'time',
                'y': 'pressure',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    time = Quantity(
        #Link to ontology class 'time' and 'time setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000165','https://purl.archive.org/tfsco/TFSCO_00005085'],
        type=np.dtype(
            np.float64),
        shape=['*'],
        unit=('s'))

    temperature = Quantity(
        #Link to ontology class 'temperature', Link to ontology class 'temperature setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146','https://purl.archive.org/tfsco/TFSCO_00002071'],
        type=np.dtype(np.float64),
        shape=['*'],
        unit=('°C'),
        a_plot=[
            {
                'x': 'time',
                'y': 'temperature',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])


class GasFlow(ArchiveSection):

    m_def = Section(label_quantity='name')
    name = Quantity(type=str)

    # gas_ref = Quantity(
    #     type=Reference(Gas.m_def),
    #     a_eln=dict(component='ReferenceEditQuantity'))

    gas_str = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    gas_flow_rate = Quantity(
        #Link to ontology class 'gas flow rate' and 'gas flow rate setting datum'
        links = ['https://purl.archive.org/tfsco/TFSCO_00002114','https://purl.archive.org/tfsco/TFSCO_00002108'],
        type=np.dtype(
            np.float64),
        unit=('cm**3/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm**3/minute', props=dict(minValue=0)))

    def normalize(self, archive, logger):
        if self.gas_str:
            if self.gas_flow_rate:
                self.name = f"{self.gas_str} {str(self.gas_flow_rate)}"
            else:
                self.name = self.gas_str

        print(self.name)


class PECVDProcess(ArchiveSection):

    power = Quantity(
        #Link to ontology class 'power' and 'power setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001024','https://purl.archive.org/tfsco/TFSCO_00002104'],
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    pressure = Quantity(
        #Link to ontology class 'pressure' and 'pressure setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0001025','https://purl.archive.org/tfsco/TFSCO_00005040'],
        type=np.dtype(
            np.float64),
        unit=('ubar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ubar',
            props=dict(
                minValue=0)))

    time = Quantity(
        #Link to ontology class 'time' and 'time setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000165','https://purl.archive.org/tfsco/TFSCO_00005085'],
        type=np.dtype(
            np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    temperature = Quantity(
        #Link to ontology class 'temperature' and 'temperature setting datum'
        links = ['http://purl.obolibrary.org/obo/PATO_0000146','https://purl.archive.org/tfsco/TFSCO_00002071'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    plate_spacing = Quantity(
        #Link to ontology class 'plate spacing'
        links = ['https://purl.archive.org/tfsco/TFSCO_00002004'],
        type=np.dtype(
            np.float64), unit=('mm'), a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm'), props=dict(
            minValue=0))

    gases = SubSection(
        section_def=GasFlow, repeats=True)

    log_data = SubSection(
        section_def=LogData, repeats=True)


class PECVDeposition(LayerDeposition):
    '''Base class for evaporation of a sample'''

    recipe = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    logs = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    process = SubSection(
        section_def=PECVDProcess)

    def normalize(self, archive, logger):

        super(PECVDeposition, self).normalize(archive, logger)

        self.method = "Plasma Enhanced Chemical Vapour Deposition"
