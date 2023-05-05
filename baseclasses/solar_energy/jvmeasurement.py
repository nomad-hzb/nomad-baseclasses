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

from nomad.units import ureg
from nomad.metainfo import (
    Quantity,
    SubSection,
    Section)

from nomad.datamodel.metainfo.eln import SolarCellJVCurve
from .. import MeasurementOnSample
from ..helper.add_solar_cell import add_solar_cell


class SolarCellJVCurveCustom(SolarCellJVCurve):
    m_def = Section(
        label_quantity='cell_name',
        a_eln=dict(
            hide=[
                'data_file',
                'certified_values',
                'certification_institute']))


class JVMeasurement(MeasurementOnSample):

    m_def = Section(label_quantity='data_file', validate=False)

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    active_area = Quantity(
        type=np.dtype(
            np.float64),
        unit=('cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm^2',
            props=dict(
                minValue=0)))

    intensity = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mW/cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mW/cm^2', props=dict(minValue=0)))

    integration_time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ms'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ms',
            props=dict(
                minValue=0)))

    settling_time = Quantity(
        type=np.dtype(
            np.float64),
        unit=('ms'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ms',
            props=dict(
                minValue=0)))

    averaging = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        a_eln=dict(component='NumberEditQuantity'))

    compliance = Quantity(
        type=np.dtype(
            np.float64),
        unit=('mA/cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mA/cm^2', props=dict(minValue=0)))

    jv_curve = SubSection(
        section_def=SolarCellJVCurveCustom,
        repeats=True,
        label_quantity='cell_name')

    def normalize(self, archive, logger):
        super(JVMeasurement, self).normalize(archive, logger)
        self.method = "JV Measurement"

        if self.data_file:
            # todo detect file format
            from ..helper.utilities import get_encoding
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)
            
            with archive.m_context.raw_file(self.data_file, "br") as f:
                import chardet
                encoding = chardet.detect(f.read())["encoding"]

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                if "LTI @ KIT" in f.readline():
                    from ..helper.KIT_jv_parser import get_jv_data
                else:
                    from ..helper.jv_parser import get_jv_data
                from ..helper.jv_archive import get_jv_archive

                jv_dict = get_jv_data(f.name, encoding)
                get_jv_archive(jv_dict, self.data_file, self)

                add_solar_cell(archive)
                archive.results.properties.optoelectronic.solar_cell.open_circuit_voltage = np.average(
                    jv_dict['V_oc']) * ureg('V')
                archive.results.properties.optoelectronic.solar_cell.short_circuit_current_density = np.average(
                    jv_dict['J_sc']) * ureg('mA/cm^2')
                archive.results.properties.optoelectronic.solar_cell.fill_factor = np.average(
                    jv_dict['Fill_factor'])
                archive.results.properties.optoelectronic.solar_cell.efficiency = np.average(
                    jv_dict['Efficiency'])
                archive.results.properties.optoelectronic.solar_cell.illumination_intensity = jv_dict['intensity'] * ureg(
                    'mW/cm^2') if 'intensity' in jv_dict else None
