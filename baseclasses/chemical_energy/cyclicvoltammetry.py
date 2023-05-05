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


def get_parameter(key, metadata):
    return metadata[key] if key in metadata else None


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

    properties = SubSection(
        section_def=CVProperties)

    def normalize(self, archive, logger):
        super(CyclicVoltammetry, self).normalize(archive, logger)
        self.method = "Cyclic Voltammetry"

        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:
                    if os.path.splitext(self.data_file)[-1] == ".DTA":
                        from nomad.datamodel.metainfo.eln.helper.gamry_parser import get_header_and_data
                        metadata, _ = get_header_and_data(filename=f.name)

                        if "CV" in metadata["TAG"] and self.properties is None:
                            properties = CVProperties()
                            from nomad.datamodel.metainfo.eln.helper.gamry_archive import get_cv_properties
                            get_cv_properties(metadata, properties)

                            self.properties = properties

                    if os.path.splitext(self.data_file)[-1] == ".mpt":
                        from nomad.datamodel.metainfo.eln.helper.mps_file_parser import read_mpt_file
                        metadata, _, technique = read_mpt_file(datafile=f.name)

                        if "Cyclic" in technique and self.properties is None:
                            properties = CVProperties()
                            properties.initial_potential = get_parameter(
                                "Ei (V)", metadata)
                            properties.initial_potential_measured_against = "Eoc" if get_parameter(
                                "Ei (V) vs.", metadata) == "Eoc" else "Eref"
                            properties.limit_potential_1 = get_parameter(
                                "E1 (V)", metadata)
                            properties.limit_potential_1_measured_against = "Eoc" if get_parameter(
                                "E1 (V) vs.", metadata) == "Eoc" else "Eref"
                            properties.limit_potential_2 = get_parameter(
                                "E2 (V)", metadata)
                            properties.limit_potential_2_measured_against = "Eoc" if get_parameter(
                                "E2 (V) vs.", metadata) == "Eoc" else "Eref"
                            properties.final_potential = get_parameter(
                                "Ef (V)", metadata)
                            properties.final_potential_measured_against = "Eoc" if get_parameter(
                                "Ef (V) vs.", metadata) == "Eoc" else "Eref"
                            properties.scan_rate = get_parameter(
                                "dE/dt", metadata)
                            properties.cycles = get_parameter(
                                "nc cycles", metadata)
                            self.properties = properties

                    if os.path.splitext(self.data_file)[-1] == ".cor":
                        from nomad.datamodel.metainfo.eln.helper.corr_ware_parser import get_header_data_corrware
                        metadata, _, technique = get_header_data_corrware(
                            filename=f.name)
                        if "Cyclic" in technique and self.properties is None:

                            properties = CVProperties()
                            properties.initial_potential = get_parameter(
                                "Potential #1", metadata['Experiment'])
                            properties.initial_potential_measured_against = "Eoc" if get_parameter(
                                'Potential #1 Type', metadata['Experiment']) == 0.0 else "Eref"
                            properties.limit_potential_1 = get_parameter(
                                'Potential #2', metadata['Experiment'])
                            properties.limit_potential_1_measured_against = "Eoc" if get_parameter(
                                'Potential #2 Type', metadata['Experiment']) == 0.0 else "Eref"
                            properties.limit_potential_2 = get_parameter(
                                'Potential #3', metadata['Experiment'])
                            properties.limit_potential_2_measured_against = "Eoc" if get_parameter(
                                'Potential #3 Type', metadata['Experiment']) == 0.0 else "Eref"
                            properties.final_potential = get_parameter(
                                'Potential #4', metadata['Experiment'])
                            properties.final_potential_measured_against = "Eoc" if get_parameter(
                                'Potential #1 Type', metadata['Experiment']) == 0.0 else "Eref"
                            properties.scan_rate = get_parameter(
                                'Scan Rate', metadata['Experiment'])
                            properties.cycles = get_parameter(
                                'Scan Number', metadata['Experiment'])
                            properties.open_circuit_potential = get_parameter(
                                'Open Circuit Potential (V)', metadata)
                            self.properties = properties

            except Exception as e:
                logger.error(e)
