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
from nomad.datamodel.metainfo.basesections import (
    CompositeSystem,
    CompositeSystemReference,
)
from nomad.datamodel.results import Material  # BandGapOptical, Material
from nomad.metainfo import Quantity, Reference, SubSection
from nomad.units import ureg

from .. import ReadableIdentifiersCustom
from ..helper.add_solar_cell import add_band_gap, add_band_gaps, add_solar_cell
from ..helper.utilities import get_reference
from .module import ModuleConfiguration
from .multijunction import MultijunctionConfiguration, MultijunctionReference
from .substrate import Substrate


def collectBaseProcesses(entry, entry_id, entry_data):
    # read out information
    if 'positon_in_experimental_plan' in entry_data:
        entry[entry_id].update(
            {'positon_in_experimental_plan': entry_data['positon_in_experimental_plan']}
        )
    # Check if it is a layer deposition
    import inspect

    import baseclasses

    entry[entry_id].update({'layer_deposition': False})
    module = entry_data['m_def'].split('.')[0]
    eval(f"exec('import {module}')")
    if baseclasses.LayerDeposition in inspect.getmro(eval(entry_data['m_def'])):
        entry[entry_id].update({'layer_deposition': True})

    if 'method' in entry_data:
        entry[entry_id].update({'method': entry_data['method']})

    entry[entry_id].update({'name': entry_data['method']})
    if 'name' in entry_data:
        entry[entry_id].update({'name': entry_data['name']})

    if 'datetime' in entry_data:
        entry[entry_id].update({'datetime': entry_data['datetime']})

    entry[entry_id].update({'layer_material': ''})
    if 'layer' in entry_data:
        entry[entry_id].update({'layer': [layer for layer in entry_data['layer']]})


def collectJVMeasurement(entry, entry_id, entry_data):
    efficiency = [
        curve['efficiency'] if 'efficiency' in curve else np.nan
        for curve in entry_data['jv_curve']
    ]
    fill_factor = [
        curve['fill_factor'] if 'fill_factor' in curve else np.nan
        for curve in entry_data['jv_curve']
    ]
    open_circuit_voltage = [
        curve['open_circuit_voltage'] if 'open_circuit_voltage' in curve else np.nan
        for curve in entry_data['jv_curve']
    ]
    short_circuit_current_density = [
        curve['short_circuit_current_density']
        if 'short_circuit_current_density' in curve
        else np.nan
        for curve in entry_data['jv_curve']
    ]
    light_intensity = [
        curve['light_intensity'] if 'light_intensity' in curve else np.nan
        for curve in entry_data['jv_curve']
    ]
    device_area = entry_data['active_area'] if 'active_area' in entry_data else np.nan
    subcell_index = (
        entry_data['subcell_index'] if 'subcell_index' in entry_data else None
    )

    entry[entry_id].update(
        {
            'efficiency': efficiency,
            'fill_factor': fill_factor,
            'open_circuit_voltage': open_circuit_voltage,
            'short_circuit_current_density': short_circuit_current_density,
            'light_intensity': light_intensity,
            'device_area': device_area,
            'subcell_index': subcell_index,
        }
    )


def collectEQEMeasurement(entry, entry_id, entry_data):
    band_gap = []
    if 'eqe_data' in entry_data:
        band_gap = [
            eqe['bandgap_eqe'] if 'bandgap_eqe' in eqe else np.nan
            for eqe in entry_data['eqe_data']
        ]
    if 'data' in entry_data and 'bandgap_eqe' in entry_data['data']:
        band_gap.append(entry_data['data']['bandgap_eqe'])
    subcell_index = (
        entry_data['subcell_index'] if 'subcell_index' in entry_data else None
    )
    entry[entry_id].update({'band_gap': band_gap, 'subcell_index': subcell_index})


SUBCELL_STACK_KEYS = (
    'device_stack',
    'absorber',
    'electron_transport_layer',
    'hole_transport_layer',
    'back_contact',
)


def collectSubcellSample(entry, entry_id, upload_id, entry_archive, multijunction_id):
    # A sample that declares itself as a subcell of the multijunction sample
    # multijunction_id. Collects its index and the values from its own results.
    subcell_index = None
    for membership in entry_archive['data']['part_of_multijunction']:
        if (
            'reference' in membership
            and multijunction_id in str(membership['reference'])
            and 'subcell_index' in membership
        ):
            subcell_index = membership['subcell_index']

    def from_results(*path):
        try:
            value = entry_archive['results']
            for key in path:
                value = value[key]
            return value
        except (KeyError, IndexError, TypeError):
            return None

    band_gap = from_results('properties', 'electronic', 'band_gap', 0, 'value')
    entry[entry_id].update(
        {
            'subcell_index': subcell_index,
            'reference': get_reference(upload_id, entry_id),
            'efficiency': from_results(
                'properties', 'optoelectronic', 'solar_cell', 'efficiency'
            ),
            # the subcell's layers, to rebuild the stack of the multijunction
            **{
                key: list(
                    from_results('properties', 'optoelectronic', 'solar_cell', key)
                    or []
                )
                for key in SUBCELL_STACK_KEYS
            },
            # results store band gaps in joule
            'band_gap': (band_gap * ureg('J')).to('eV').magnitude
            if band_gap is not None
            else None,
        }
    )


def sortProcesses(processes):
    processes_working = [p for key, p in processes.items()]
    process_positions = [
        p['positon_in_experimental_plan'] if 'positon_in_experimental_plan' in p else -1
        for p in processes_working
    ]
    return [
        x
        for _, x in sorted(
            zip(process_positions, processes_working), key=lambda pair: pair[0]
        )
    ]


def collectSampleData(archive):
    # This function gets all archives whcih reference this archive.
    # Iterates over them and selects relevant data for the
    # result section of the solarcellsample
    # At the end the synthesis steps are ordered
    # returns a dictionary containing synthesis process, JV and EQE information

    import inspect

    from nomad import files
    from nomad.app.v1.models import MetadataPagination
    from nomad.search import search

    import baseclasses

    # search for all archives referencing this archive
    query = {
        'entry_references.target_entry_id': archive.metadata.entry_id,
    }
    pagination = MetadataPagination()
    pagination.page_size = 100
    search_result = search(
        owner='all',
        query=query,
        pagination=pagination,
        user_id=archive.metadata.main_author.user_id,
    )

    # filter the result by synthesis processes, JV and EQE Measurement, and
    # samples that are subcells of this (multijunction) sample
    result = {'processes': {}, 'JVs': {}, 'EQEs': {}, 'subcells': {}}

    for res in search_result.data:
        try:
            # Open Archives
            with files.UploadFiles.get(upload_id=res['upload_id']).read_archive(
                entry_id=res['entry_id']
            ) as arch:
                entry_id = res['entry_id']
                entry_data = arch[entry_id]['data']
                entry = {entry_id: {}}
                try:
                    entry[entry_id]['elements'] = arch[entry_id]['results']['material'][
                        'elements'
                    ]
                except BaseException:
                    entry[entry_id]['elements'] = []
                # Check if it is a BaseProcess
                module = entry_data['m_def'].split('.')[0]
                eval(f"exec('import {module}')")
                if baseclasses.BaseProcess in inspect.getmro(eval(entry_data['m_def'])):
                    collectBaseProcesses(entry, entry_id, entry_data)
                    result['processes'].update(entry)

                # check if it is a JV measurement
                if (
                    baseclasses.solar_energy.jvmeasurement.JVMeasurement
                    in inspect.getmro(eval(entry_data['m_def']))
                ):
                    collectJVMeasurement(entry, entry_id, entry_data)
                    result['JVs'].update(entry)

                # check if EQ Measurement
                if (
                    baseclasses.solar_energy.eqemeasurement.EQEMeasurement
                    in inspect.getmro(eval(entry_data['m_def']))
                ):
                    collectEQEMeasurement(entry, entry_id, entry_data)
                    result['EQEs'].update(entry)

                # check if it is a subcell sample of this sample
                if 'part_of_multijunction' in entry_data:
                    collectSubcellSample(
                        entry,
                        entry_id,
                        res['upload_id'],
                        arch[entry_id],
                        archive.metadata.entry_id,
                    )
                    if entry[entry_id]['subcell_index'] is not None:
                        result['subcells'].update(entry)
        except Exception as e:
            print('Error in processing data: ', e)

    # sort processes by the filled previous process
    result['processes'] = sortProcesses(result['processes'])
    return result


def getLayerForStack(layer):
    if (
        'layer_material_name' in layer
        and layer['layer_material_name'] is not None
        and layer['layer_material_name'].strip()
    ):
        return layer['layer_material_name'].strip()
    return layer.get('layer_material')


def addLayerDepositionToStack(archive, process):
    for layer in process.get('layer', []):
        layer_name = getLayerForStack(layer)
        archive.results.properties.optoelectronic.solar_cell.device_stack.append(
            layer_name
        )

        if 'absorber' in layer.get('layer_type', '').lower():
            archive.results.properties.optoelectronic.solar_cell.absorber.append(
                layer_name
            )
            archive.results.properties.optoelectronic.solar_cell.absorber_fabrication = [
                f'{process["method"]}'
            ]

        if (
            'etl' in layer.get('layer_type', '').lower()
            or 'electron' in layer.get('layer_type', '').lower()
        ):
            archive.results.properties.optoelectronic.solar_cell.electron_transport_layer.append(
                layer_name
            )

        if (
            'htl' in layer.get('layer_type', '').lower()
            or 'hole' in layer.get('layer_type', '').lower()
        ):
            archive.results.properties.optoelectronic.solar_cell.hole_transport_layer.append(
                layer_name
            )

        if 'back' in layer.get('layer_type', '').lower():
            archive.results.properties.optoelectronic.solar_cell.back_contact.append(
                layer_name
            )


def add_subcell_stacks(archive, subcell_samples):
    # The layers of a multijunction live in its subcell samples. Add their
    # stacks from bottom to top, before the processes on the multijunction
    # sample itself (e.g. lamination, encapsulation).
    solar_cell = archive.results.properties.optoelectronic.solar_cell
    for subcell_sample in sorted(subcell_samples, key=lambda s: s['subcell_index']):
        for key in SUBCELL_STACK_KEYS:
            getattr(solar_cell, key).extend(subcell_sample[key])
        archive.results.material.elements.extend(subcell_sample['elements'])


class BasicSampleWithID(CompositeSystem):
    sample_id = SubSection(section_def=ReadableIdentifiersCustom)


class SolcarCellSample(CompositeSystem):
    substrate = Quantity(
        type=Reference(Substrate.m_def), a_eln=dict(component='ReferenceEditQuantity')
    )

    architecture = Quantity(
        type=str,
        shape=[],
        description="""
            The cell architecture with respect to the direction of current flow and
            the order in which layers are deposited.
            The two most common are nip (also referred to as normal) and pin
            (also referred to as inverted)
            but there are also a few others, e.g. Back contacted.
            - *nip* architecture means that the electrons are collected at the
            substrate side.
            The typical example is in perovskite solar cells when a TiO2 electron
            selective contact is deposited
            between the perovskite and the substrate
            (e.g. SLG | FTO | TiO2-c | Perovskite | …)
            - *pin* architecture means that it instead is the holes that are collected
            at the substrate side. The typical example is when a PEDOT:PSS hole
            selective contact is deposited between the perovskite and the
            substrate (e.g. SLG | FTO | PEDOT:PSS |Perovskite | …)
        """,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Unknown',
                    'Pn-Heterojunction',
                    'Front contacted',
                    'Back contacted',
                    'pin',
                    'nip',
                    'Schottky',
                ]
            ),
        ),
    )

    number_of_junctions = Quantity(type=int, a_eln=dict(component='NumberEditQuantity'))

    sample_id = SubSection(section_def=ReadableIdentifiersCustom)
    parent = SubSection(section_def=CompositeSystemReference)

    module_configuration = SubSection(
        section_def=ModuleConfiguration,
        description=(
            'Section present when sample is module'
            'Module-level configuration: whether pixels are connected and how. '
            'Orthogonal to multijunction_configuration — a tandem can also be a module.'
        ),
    )

    multijunction_configuration = SubSection(
        section_def=MultijunctionConfiguration,
        description=(
            'Section present when the sample is a multijunction (tandem) device: '
            'how the subcells are combined and contacted, and the subcells.'
        ),
    )

    part_of_multijunction = SubSection(
        section_def=MultijunctionReference,
        repeats=True,
        description=(
            'Present when the sample is a subcell of one or more multijunction '
            'devices: the multijunction sample and the subcell index in it.'
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        normalized_substrate = self.substrate
        if normalized_substrate is not None and hasattr(normalized_substrate, 'normalize'):
            try:
                normalized_substrate.normalize(archive, logger)
            except Exception:
                if logger:
                    logger.debug('Substrate normalize failed in SolcarCellSample.', exc_info=True)

        add_solar_cell(archive)
        archive.results.properties.optoelectronic.solar_cell.device_stack = []
        archive.results.properties.optoelectronic.solar_cell.substrate = []
        if normalized_substrate is not None:
            if normalized_substrate.substrate is not None:
                archive.results.properties.optoelectronic.solar_cell.substrate = [
                    normalized_substrate.substrate
                ]
                archive.results.properties.optoelectronic.solar_cell.device_stack.append(
                    normalized_substrate.substrate
                )
            if normalized_substrate.conducting_material is not None:
                archive.results.properties.optoelectronic.solar_cell.substrate.extend(
                    normalized_substrate.conducting_material
                )
                archive.results.properties.optoelectronic.solar_cell.device_stack.extend(
                    normalized_substrate.conducting_material
                )

            per_cell_area = (
                getattr(normalized_substrate, 'active_area', None)
                or normalized_substrate.pixel_area
            )
            if per_cell_area:
                archive.results.properties.optoelectronic.solar_cell.device_area = (
                    per_cell_area
                )

        if self.architecture:
            archive.results.properties.optoelectronic.solar_cell.device_architecture = (
                self.architecture
            )

        # Compute module_active_area: per-cell area × number_of_pixels on substrate
        if (
            self.module_configuration
            and self.module_configuration.is_module 
            and normalized_substrate
        ):
            n_pixels = normalized_substrate.number_of_pixels
            per_cell_active = (
                getattr(normalized_substrate, 'active_area', None)
                or normalized_substrate.pixel_area
            )
            if per_cell_active is not None and n_pixels:
                self.module_configuration.module_active_area = (
                    per_cell_active * n_pixels
                )
            per_cell_dead = getattr(normalized_substrate, 'dead_area', None)
            if per_cell_dead is not None and n_pixels:
                self.module_configuration.module_dead_area = per_cell_dead * n_pixels

            gff = getattr(normalized_substrate, 'geometrical_fill_factor', None)
            if gff is not None:
                self.module_configuration.module_geometrical_fill_factor = gff

            module_active_area = self.module_configuration.module_active_area
            module_dead_area = self.module_configuration.module_dead_area
            if module_active_area is not None and module_dead_area is not None:
                self.module_configuration.module_aperture_area = (
                    module_active_area + module_dead_area
                )

        result_data = collectSampleData(archive)

        jv_key = ''
        jv_idx = -1
        jv_eff_val = 0
        for entry in result_data['JVs']:
            # only measurements on the complete device give the device efficiency
            if result_data['JVs'][entry]['subcell_index']:
                continue
            for j, eff in enumerate(result_data['JVs'][entry]['efficiency']):
                if not np.isnan(eff) and eff > jv_eff_val:
                    jv_key = entry
                    jv_idx = j
                    jv_eff_val = eff

        if jv_key:
            if not np.isnan(result_data['JVs'][jv_key]['efficiency'][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.efficiency = (
                    result_data['JVs'][jv_key]['efficiency'][jv_idx]
                )
            if not np.isnan(result_data['JVs'][jv_key]['fill_factor'][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.fill_factor = (
                    result_data['JVs'][jv_key]['fill_factor'][jv_idx]
                )
            if not np.isnan(result_data['JVs'][jv_key]['open_circuit_voltage'][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.open_circuit_voltage = (
                    result_data['JVs'][jv_key]['open_circuit_voltage'][jv_idx]
                    * ureg('V')
                )
            if not np.isnan(result_data['JVs'][jv_key]['light_intensity'][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.illumination_intensity = (
                    result_data['JVs'][jv_key]['light_intensity'][jv_idx]
                    * ureg('mW/cm**2')
                )
            if not np.isnan(
                result_data['JVs'][jv_key]['short_circuit_current_density'][jv_idx]
            ):
                archive.results.properties.optoelectronic.solar_cell.short_circuit_current_density = (
                    result_data['JVs'][jv_key]['short_circuit_current_density'][jv_idx]
                    * ureg('mA/cm**2')
                )
            if not np.isnan(result_data['JVs'][jv_key]['device_area']):
                archive.results.properties.optoelectronic.solar_cell.device_area = (
                    result_data['JVs'][jv_key]['device_area'] * ureg('cm**2')
                )

        subcell_band_gaps = []
        if self.multijunction_configuration is not None:
            subcell_band_gaps = self.normalize_multijunction(
                archive, result_data, has_device_jv=bool(jv_key)
            )

        if subcell_band_gaps:
            add_band_gaps(archive, subcell_band_gaps)
        else:
            eqe_eff_val = 0 * ureg('eV')
            for entry in result_data['EQEs']:
                for bandgap in result_data['EQEs'][entry]['band_gap']:
                    if np.isnan(bandgap) or bandgap * ureg('eV') < eqe_eff_val:
                        continue
                    eqe_eff_val = bandgap * ureg('eV')

            if result_data['EQEs']:
                band_gap = eqe_eff_val
                add_band_gap(archive, band_gap)

        archive.results.properties.optoelectronic.solar_cell.absorber = []
        archive.results.properties.optoelectronic.solar_cell.absorber_fabrication = []
        archive.results.properties.optoelectronic.solar_cell.electron_transport_layer = []
        archive.results.properties.optoelectronic.solar_cell.hole_transport_layer = []
        archive.results.properties.optoelectronic.solar_cell.back_contact = []

        if not archive.results.material:
            archive.results.material = Material()
        archive.results.material.elements = []

        if result_data['EQEs'] or result_data['JVs']:
            archive.results.material.functional_type = ['semiconductor', 'solarcell']

        add_subcell_stacks(archive, result_data['subcells'].values())

        for process in result_data['processes']:
            if process['layer_deposition']:
                addLayerDepositionToStack(archive, process)

            if process['layer_deposition'] and process['elements']:
                archive.results.material.elements.extend(process['elements'])

        archive.results.material.elements = list(set(archive.results.material.elements))

    def normalize_multijunction(self, archive, result_data, has_device_jv):
        """Updates the subcells of a multijunction sample and, for 4 terminals
        without a measurement of the complete device, sets the device efficiency
        to the sum of the subcell efficiencies. Returns the subcell band gaps."""
        multijunction = self.multijunction_configuration
        multijunction.update_subcells(result_data, self.number_of_junctions)
        if self.number_of_junctions is None and multijunction.subcells:
            self.number_of_junctions = len(multijunction.subcells)

        efficiency = multijunction.four_terminal_efficiency(self.number_of_junctions)
        if efficiency is not None and not has_device_jv:
            archive.results.properties.optoelectronic.solar_cell.efficiency = efficiency
        return multijunction.band_gaps()
