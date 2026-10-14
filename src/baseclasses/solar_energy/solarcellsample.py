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
from .module import ModuleConfiguration
from .multijunction import MultijunctionConfiguration
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
    subcell_index = entry_data['subcell_index'] if 'subcell_index' in entry_data else 0

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
    measurement_subcell = (
        entry_data['subcell_index'] if 'subcell_index' in entry_data else 0
    )
    spectra = []
    if 'eqe_data' in entry_data:
        spectra.extend(entry_data['eqe_data'])
    if 'data' in entry_data:
        spectra.append(entry_data['data'])

    band_gap = []
    subcell_spectra = []
    for eqe in spectra:
        band_gap.append(eqe['bandgap_eqe'] if 'bandgap_eqe' in eqe else np.nan)
        subcell_spectra.append(
            {
                'subcell_index': eqe['subcell_index']
                if 'subcell_index' in eqe
                else measurement_subcell,
                'band_gap': eqe['bandgap_eqe'] if 'bandgap_eqe' in eqe else np.nan,
                'integrated_jsc': eqe['integrated_jsc']
                if 'integrated_jsc' in eqe
                else np.nan,
            }
        )
    entry[entry_id].update({'band_gap': band_gap, 'spectra': subcell_spectra})


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

    # filter the result by synthesis processes, and JV and EQE Measurement
    result = {'processes': {}, 'JVs': {}, 'EQEs': {}}

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

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        multijunction = self.multijunction_configuration
        if multijunction is not None:
            if multijunction.number_of_junctions is None:
                multijunction.number_of_junctions = self.number_of_junctions
            if multijunction.number_of_junctions is not None:
                self.number_of_junctions = multijunction.number_of_junctions

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
            if result_data['JVs'][entry].get('subcell_index', 0) not in (0, None):
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

        subcell_band_gaps_added = False
        if multijunction is not None:
            subcell_band_gaps_added = self.normalize_multijunction(
                archive, result_data, has_device_jv=bool(jv_key)
            )

        if not subcell_band_gaps_added:
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

        for process in result_data['processes']:
            if process['layer_deposition']:
                addLayerDepositionToStack(archive, process)

            if process['layer_deposition'] and process['elements']:
                archive.results.material.elements.extend(process['elements'])

        archive.results.material.elements = list(set(archive.results.material.elements))

    def normalize_multijunction(self, archive, result_data, has_device_jv):
        """Fills the subcells from measurements tagged with a subcell_index:
        band gap and integrated Jsc from EQE, the combined efficiency of
        independently contacted subcells from JV, and one band gap per subcell
        in the results. Returns True if subcell band gaps were added."""
        multijunction = self.multijunction_configuration

        # Highest band gap and integrated Jsc per subcell from the EQE spectra
        eqe_by_subcell = {}
        for entry in result_data['EQEs'].values():
            for spectrum in entry.get('spectra', []):
                index = spectrum['subcell_index']
                if not index:
                    continue
                values = eqe_by_subcell.setdefault(index, {})
                for key in ('band_gap', 'integrated_jsc'):
                    value = spectrum[key]
                    if value is None or np.isnan(value):
                        continue
                    if key not in values or value > values[key]:
                        values[key] = value

        for index, values in eqe_by_subcell.items():
            subcell = multijunction.get_subcell(index)
            if subcell is None:
                continue
            if subcell.band_gap is None and 'band_gap' in values:
                subcell.band_gap = values['band_gap'] * ureg('eV')
            if 'integrated_jsc' in values:
                subcell.integrated_jsc = values['integrated_jsc'] * ureg('mA/cm**2')

        # Best efficiency per subcell from the JV measurements
        best_subcell_efficiency = {}
        for entry in result_data['JVs'].values():
            index = entry.get('subcell_index', 0)
            if not index:
                continue
            for eff in entry['efficiency']:
                if np.isnan(eff):
                    continue
                if eff > best_subcell_efficiency.get(index, -1):
                    best_subcell_efficiency[index] = eff

        multijunction.combined_efficiency = None
        n_subcells = multijunction.number_of_junctions or len(multijunction.subcells)
        if (
            multijunction.number_of_terminals == 4
            and n_subcells
            and len(best_subcell_efficiency) == n_subcells
        ):
            multijunction.combined_efficiency = sum(best_subcell_efficiency.values())
            if not has_device_jv:
                archive.results.properties.optoelectronic.solar_cell.efficiency = (
                    multijunction.combined_efficiency
                )

        multijunction.derive_quantities()

        # One band gap per subcell in the results
        band_gaps = []
        for subcell in multijunction.sorted_subcells():
            if subcell.band_gap is None:
                continue
            label = f'subcell {subcell.subcell_index}'
            if subcell.absorber_technology:
                label += f' - {subcell.absorber_technology}'
            band_gaps.append((subcell.band_gap.to('eV').magnitude, label))
        for index, values in sorted(eqe_by_subcell.items()):
            if multijunction.get_subcell(index) is None and 'band_gap' in values:
                band_gaps.append((values['band_gap'], f'subcell {index}'))
        add_band_gaps(archive, band_gaps)
        return bool(band_gaps)
