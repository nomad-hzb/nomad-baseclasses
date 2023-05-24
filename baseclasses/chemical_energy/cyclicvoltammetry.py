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

from nomad.metainfo import (Quantity, SubSection, MEnum)
from nomad.datamodel.data import ArchiveSection

from .voltammetry import Voltammetry


class CVProperties(ArchiveSection):

    initial_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    initial_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    limit_potential_1 = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    limit_potential_1_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    limit_potential_2 = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    limit_potential_2_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    final_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    final_potential_measured_against = Quantity(
        type=MEnum('Eoc', 'Eref'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    scan_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('mV/s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV/s'))

    step_size = Quantity(
        type=np.dtype(np.float64),
        unit=('mV'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mV'))

    cycles = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    sample_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))

    open_circuit_potential = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))


class CyclicVoltammetry(Voltammetry):

    voltage_shift = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    resistance = Quantity(
        type=np.dtype(np.float64),
        unit=('ohm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ohm'))

    voltage_rhe = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='V', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage_rhe', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    properties = SubSection(
        section_def=CVProperties)

    def normalize(self, archive, logger):
        super(CyclicVoltammetry, self).normalize(archive, logger)
        self.method = "Cyclic Voltammetry"

        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:
                    if os.path.splitext(self.data_file)[-1] == ".DTA":
                        from ..helper.gamry_parser import get_header_and_data
                        metadata, _ = get_header_and_data(filename=f.name)

                        if "CV" in metadata["TAG"] and self.properties is None:
                            from ..helper.gamry_archive import get_cv_properties
                            properties = CVProperties()
                            get_cv_properties(metadata, properties)
                            self.properties = properties

                    if os.path.splitext(self.data_file)[-1] == ".mpt":
                        from ..helper.mps_file_parser import read_mpt_file

                        metadata, _, technique = read_mpt_file(f.name)

                        if "Cyclic" in technique and self.properties is None:
                            from ..helper.mpt_get_archive import get_cv_properties
                            properties = CVProperties()
                            get_cv_properties(metadata, properties)
                            self.properties = properties

                    if os.path.splitext(self.data_file)[-1] == ".cor":
                        from ..helper.corr_ware_parser import get_header_data_corrware
                        metadata, _, technique = get_header_data_corrware(
                            filename=f.name)
                        if "Cyclic" in technique and self.properties is None:
                            experiment = metadata['Experiment']
                            properties = CVProperties()
                            properties.initial_potential = experiment.get(
                                "Potential #1")
                            properties.initial_potential_measured_against = "Eoc" if experiment.get(
                                'Potential #1 Type') == 0.0 else "Eref"
                            properties.limit_potential_1 = experiment.get(
                                'Potential #2')
                            properties.limit_potential_1_measured_against = "Eoc" if experiment.get(
                                'Potential #2 Type') == 0.0 else "Eref"
                            properties.limit_potential_2 = experiment.get(
                                'Potential #3')
                            properties.limit_potential_2_measured_against = "Eoc" if experiment.get(
                                'Potential #3 Type') == 0.0 else "Eref"
                            properties.final_potential = experiment.get(
                                'Potential #4')
                            properties.final_potential_measured_against = "Eoc" if experiment.get(
                                'Potential #1 Type') == 0.0 else "Eref"
                            properties.scan_rate = experiment.get(
                                'Scan Rate')
                            properties.cycles = experiment.get(
                                'Scan Number')
                            properties.open_circuit_potential = metadata.get(
                                'Open Circuit Potential (V)')
                            self.properties = properties

            except Exception as e:
                logger.error(e)

        if self.properties.sample_area is not None:
            if self.current is not None:
                self.current_density = self.current / self.properties.sample_area
            if self.cycles is not None:
                for cycle in self.cycles:
                    if cycle.current is not None:
                        cycle.current_density = cycle.current / self.properties.sample_area

        if self.resistance is not None and self.voltage_shift:
            resistance = np.array(self.resistance)
            shift = np.array(self.voltage_shift)

            if self.voltage is not None and self.current is not None:
                volts = np.array(self.voltage)
                current = np.array(self.current)/1000
                self.voltage_rhe = (volts + shift) - (resistance*current)
            if self.cycles is not None:
                for cycle in self.cycles:
                    if cycle.voltage is not None and cycle.current is not None:
                        volts = np.array(cycle.voltage)
                        current = np.array(cycle.current)/1000
                        cycle.voltage_rhe = (
                            volts + shift) - (current*resistance)
