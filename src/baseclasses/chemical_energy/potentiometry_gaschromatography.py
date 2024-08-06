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

from nomad.metainfo import (Quantity, Section, SubSection, Datetime)
from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.datamodel.metainfo.basesections import CompositeSystemReference

from .. import BaseMeasurement, ReadableIdentifiersCustom
from .cesample import build_initial_id, create_id


class NECCFeedGas(ArchiveSection):

    name = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'CO2',
                    'CO',
                    'H2'
                ])))

    flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))


class NECCExperimentalProperties(ArchiveSection):

    anode = SubSection(
        section_def=CompositeSystemReference,
    )

    cathode = SubSection(
        section_def=CompositeSystemReference,
    )

    fill_in_default = Quantity(
        type=bool,
        default=False,
        description='Check this box and press the save button to load default entries. '
                    'Attention: Already entered values will be overwritten.',
        a_eln=dict(component='BoolEditQuantity'))

    cell_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Zero-Gap',
                    'Catholyte Flow',
                    'H-Cell'
                ])))

    has_reference_electrode = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))

    reference_electrode_type = Quantity(
        type=str,
        shape=[],
        description='If has reference electrode is not checked, '
                    'this reference electrode type must be N/A.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Ag/AgCl',
                    'Hg/HgO',
                    'N/A'
                ])))

    cathode_geometric_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))

    membrane_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'AEM',
                    'CEM'
                ])))

    membrane_name = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'PiperION',
                    'SustainION',
                    'Fumasep',
                    'Nafion'
                ])))

    membrane_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='um', props=dict(minValue=0)))

    gasket_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('um'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='um', props=dict(minValue=0)))

    anolyte_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'KOH',
                    'KHCO3'
                ])))

    anolyte_concentration = Quantity(
        type=np.dtype(np.float64),
        unit=('mol/L'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mol/L'))

    anolyte_flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    anolyte_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    has_humidifier = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity')
    )

    humidifier_temperature = Quantity(
        type=np.dtype(np.float64),
        unit='°C',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    water_trap_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    feed_gases = SubSection(
        section_def=NECCFeedGas, repeats=True)

    bleedline_flow_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('ml/minute'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml/minute',
            props=dict(minValue=0)
        ))

    nitrogen_start_value = Quantity(
        type=np.dtype(np.float64),
        description='Specified in ppm',
        a_eln=dict(component='NumberEditQuantity'))

    chronoanalysis_method = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['Chronoamperometry (CA)', 'Chronopotentiometry (CP)'])
        ))

    remarks = Quantity(
        type=str,
        a_eln=dict(
            component='RichTextEditQuantity',
            label="Remarks"
        ))

    def normalize(self, archive, logger):

        if self.anode is not None:
            self.anode.normalize(archive, logger)

        if self.cathode is not None:
            self.cathode.normalize(archive, logger)

        if self.has_reference_electrode is False:
            self.reference_electrode_type = 'N/A'

        if self.fill_in_default:
            self.fill_in_default = False
            self.cell_type = 'Zero-Gap'
            self.has_reference_electrode = False
            self.reference_electrode_type = 'N/A'
            self.cathode_geometric_area = 8
            self.membrane_type = 'AEM'
            self.membrane_name = 'PiperION'
            self.membrane_thickness = 40
            self.gasket_thickness = 200
            self.anolyte_type = 'KOH'
            self.anolyte_concentration = 1.0
            self.anolyte_flow_rate = 15
            self.anolyte_volume = 25
            self.has_humidifier = True
            self.humidifier_temperature = 25
            self.water_trap_volume = 10
            self.feed_gases = [NECCFeedGas(name='CO2', flow_rate=60)]
            self.bleedline_flow_rate = 20
            self.chronoanalysis_method = 'Chronopotentiometry (CP)'


class GasChromatographyMeasurement(ArchiveSection):

    m_def = Section(label_quantity='gas_type')

    instrument_file_name = Quantity(
        type=str,
        shape=['*'])

    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    gas_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['CO', 'CH4', 'C2H4', 'C2H6', 'H2', 'N2'])
        ))

    retention_time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='minute')

    area = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='pA*minute')

    ppm = Quantity(
        type=np.dtype(np.float64),
        description='Specified in ppm',
        shape=['*'])


class PotentiostatMeasurement(ArchiveSection):

    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    current = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='mA', a_plot=[
            {
                'label': 'Current', 'x': 'datetime', 'y': 'current',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False}},
                'config': {
                    'editable': True, 'scrollZoom': True}}])

    working_electrode_potential = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='V', a_plot=[
            {
                'label': 'Working Electrode Potential (Ewe)',
                'x': 'datetime', 'y': 'working_electrode_potential',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False}},
                'config': {
                    'editable': True, 'scrollZoom': True}}])

    mean_current = Quantity(type=np.dtype(np.float64))
    variance_current = Quantity(type=np.dtype(np.float64))
    minimum_current = Quantity(type=np.dtype(np.float64))
    maximum_current = Quantity(type=np.dtype(np.float64))

    mean_working_electrode_potential = Quantity(type=np.dtype(np.float64))
    variance_working_electrode_potential = Quantity(type=np.dtype(np.float64))
    minimum_working_electrode_potential = Quantity(type=np.dtype(np.float64))
    maximum_working_electrode_potential = Quantity(type=np.dtype(np.float64))

    def normalize(self, archive, logger):
        self.mean_current = np.mean(self.current)
        self.minimum_current = np.min(self.current)
        self.maximum_current = np.max(self.current)
        self.variance_current = np.var(self.current)

        self.mean_working_electrode_potential = np.mean(self.working_electrode_potential)
        self.minimum_working_electrode_potential = np.min(self.working_electrode_potential)
        self.maximum_working_electrode_potential = np.max(self.working_electrode_potential)
        self.variance_working_electrode_potential = np.var(self.working_electrode_potential)


class ThermocoupleMeasurement(PlotSection, ArchiveSection):
    m_def = Section(
        a_plotly_graph_object=[
            {
                'label': 'Anode/Cathode Temperatures',
                'data': [{
                    'method': 'line',
                    'name': 'Cathode',
                    'x': '#datetime',
                    'y': '#temperature_cathode'
                }, {
                    'method': 'line',
                    'name': 'Anode',
                    'x': '#datetime',
                    'y': '#temperature_anode'
                }],
                'layout': {
                    'title': {
                        'text': 'Anode and Cathode Temperature over Time'
                    },
                    'xaxis': {
                        'title': {
                            'text': 'Time'
                        }
                    },
                    'yaxis': {
                        'title': {
                            'text': 'Temperature'
                        }
                    },
                    'showlegend': True
                }
            }])

    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    pressure = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='bar', a_plot=[
            {
                "label": "Pressure (in barg)", 'x': 'datetime', 'y': 'pressure', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    temperature_cathode = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='°C', a_plot=[
            {
                'label': 'Temperature Cathode',
                'x': 'datetime', 'y': 'temperature_cathode',
                'layout': {
                    'yaxis': {'fixedrange': False},
                    'xaxis': {'fixedrange': False}},
                'config': {
                    "editable": True, "scrollZoom": True}}])

    temperature_anode = Quantity(
        type=np.dtype(np.float64), shape=['*'], unit='°C',
        a_plot=[
            {
                "label": "Temperature Anode", 'x': 'datetime', 'y': 'temperature_anode', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])


class GasFEResults(ArchiveSection):

    m_def = Section(label_quantity='gas_type')

    gas_type = Quantity(
        type=str,
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=['CO', 'CH4', 'C2H4', 'H2'])
        ))

    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    current = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA')

    faradaic_efficiency = Quantity(
        type=np.dtype(np.float64),
        description='Faradaic efficiency specified in %',
        shape=['*'],
        a_plot=[
            {
                "label": "FE over time", 'x': 'datetime', 'y': 'faradaic_efficiency', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    mean_fe = Quantity(type=np.dtype(np.float64))

    variance_fe = Quantity(type=np.dtype(np.float64))

    minimum_fe = Quantity(type=np.dtype(np.float64))

    maximum_fe = Quantity(type=np.dtype(np.float64))

    def normalize(self, archive, logger):
        if any(fe < -100 for fe in self.faradaic_efficiency):
            self.faradaic_efficiency = [0] * len(self.faradaic_efficiency)
            logger.warn(f'The FE of {self.gas_type} is removed because it is more than 100%. '
                        f'Please check if {self.gas_type} is a feed gas.')
        self.mean_fe = np.mean(self.faradaic_efficiency)
        self.minimum_fe = np.min(self.faradaic_efficiency)
        self.maximum_fe = np.max(self.faradaic_efficiency)
        self.variance_fe = np.var(self.faradaic_efficiency)


class PotentiometryGasChromatographyResults(ArchiveSection):

    datetime = Quantity(
        type=Datetime,
        shape=['*'])

    total_flow_rate = Quantity(
        type=np.dtype(
            np.float64),
        shape=['*'],
        unit=('ml/minute'))

    cell_current = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA')

    cell_voltage = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='V')

    gas_results = SubSection(
        section_def=GasFEResults, repeats=True)

    total_fe = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='Total faradaic efficiency specified in %')

    def normalize(self, archive, logger):
        for gas_result in self.gas_results:
            gas_result.normalize(archive, logger)
        super(PotentiometryGasChromatographyResults, self).normalize(archive, logger)


class CENECCExperimentID(ReadableIdentifiersCustom):

    m_def = Section(
        a_eln=dict(
            hide=["sample_owner", "sample_short_name", "sample_id", "short_name"]
        ))

    institute = Quantity(
        type=str,
        description='Alias/short name of the home institute of the owner, i.e. *HZB*.',
        default='CE-NECC',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'CE-NECC'])))

    def normalize(self, archive, logger):
        author = archive.metadata.main_author
        if author and self.owner is None:
            self.owner = ' '.join([author.first_name, author.last_name])

        super(CENECCExperimentID, self).normalize(archive, logger)

        if archive.data.lab_id:
            return
        if not self.datetime:
            from datetime import date
            self.datetime = date.today()

        if self.institute and self.owner and self.datetime:
            self.lab_id = build_initial_id(self.institute, self.owner, self.datetime)

        create_id(archive, self.lab_id)


class PotentiometryGasChromatographyMeasurement(BaseMeasurement):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    experiment_id = SubSection(
        section_def=CENECCExperimentID)

    properties = SubSection(
        section_def=NECCExperimentalProperties)

    gaschromatographies = SubSection(
        section_def=GasChromatographyMeasurement, repeats=True)

    potentiometry = SubSection(
        section_def=PotentiostatMeasurement)

    thermocouple = SubSection(
        section_def=ThermocoupleMeasurement)

    fe_results = SubSection(
        section_def=PotentiometryGasChromatographyResults)

    def normalize(self, archive, logger):
        self.experiment_id = CENECCExperimentID()
        self.experiment_id.normalize(archive, logger)
        super(PotentiometryGasChromatographyMeasurement, self).normalize(archive, logger)
