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
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    power_var = Quantity(
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    pressure_mean = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    pressure_var = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    temperature_mean = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    temperature_var = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    power = Quantity(
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
        type=np.dtype(
            np.float64),
        shape=['*'],
        unit=('s'))

    temperature = Quantity(
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
        type=np.dtype(
            np.float64),
        unit=('W'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='W',
            props=dict(
                minValue=0)))

    pressure = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ubar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ubar',
            props=dict(
                minValue=0)))

    time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(
                minValue=0)))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    plate_spacing = Quantity(
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

        process = PECVDProcess()
        if self.process is not None:
            process = self.process
        if self.recipe is not None and os.path.splitext(self.recipe)[
                1] == ".set":
            from nomad.datamodel.metainfo.eln.helper.parse_files_pecvd_pvcomb import parse_recipe
            with archive.m_context.raw_file(self.recipe) as f:
                parse_recipe(f, process)

        if self.logs is not None:
            logs = []
            for log in self.logs:
                if os.path.splitext(log)[1] == ".log":
                    from nomad.datamodel.metainfo.eln.helper.parse_files_pecvd_pvcomb import parse_log
                    with archive.m_context.raw_file(log) as f:
                        if process.time:
                            data = parse_log(
                                f,
                                process,
                                np.int64(0.9 * process.time),
                                np.int64(0.05 * process.time))
                        else:
                            data = parse_log(f, process)
                        data.name = log
                        logs.append(data)
            process.log_data = logs
        self.process = process

        if self.process is not None and self.process.gases and self.layer_material_name is None:
            formulas = [gas.gas_str.strip() for gas in self.process.gases]
            self.layer_material_name = ",".join(formulas)

        super(PECVDeposition, self).normalize(archive, logger)

        self.method = "Plasma Enhanced Chemical Vapour Deposition"
