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
    Quantity, SubSection, MEnum, Datetime, Section)
from nomad.datamodel.data import ArchiveSection

from .voltammetry import Voltammetry, VoltammetryCycle
from .potentiostat_measurement import PotentiostatMeasurement


class CAProperties(ArchiveSection):

    pre_step_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    pre_step_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    pre_step_delay_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    step_1_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    step_1_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    step_1_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    step_2_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    step_2_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    step_2_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    sample_period = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'))

    sample_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))


class CAPropertiesWithData(CAProperties):
    m_def = Section(label_quantity='name',
                    a_plot=[{'label': 'Current',
                             'x': 'data/time',
                             'y': 'data/current',
                             'layout': {'yaxis': {"fixedrange": False},
                                        'xaxis': {"fixedrange": False}},
                             "config": {"scrollZoom": True,
                                        'staticPlot': False,
                                        }}])

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
        section_def=VoltammetryCycle)


class Chronoamperometry(Voltammetry):

    properties = SubSection(
        section_def=CAProperties)

    def normalize(self, archive, logger):
        super(Chronoamperometry, self).normalize(archive, logger)
        self.method = "Chronoamperometry"

        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:
                    if os.path.splitext(self.data_file)[-1] == ".DTA":
                        from nomad.datamodel.metainfo.eln.helper.gamry_parser import get_header_and_data
                        metadata, _ = get_header_and_data(filename=f.name)

                        if "CHRONOA" in metadata["TAG"] and self.properties is None:
                            from nomad.datamodel.metainfo.eln.helper.gamry_archive import get_ca_properties

                            properties = CAProperties()
                            get_ca_properties(metadata, properties)

                            self.properties = properties

            except Exception as e:
                logger.error(e)


class ChronoamperometryMultiple(PotentiostatMeasurement):

    measurements = SubSection(
        section_def=CAPropertiesWithData, repeats=True)

    def normalize(self, archive, logger):
        super(ChronoamperometryMultiple, self).normalize(archive, logger)
        self.method = "Multiple Chronoamperometry"
