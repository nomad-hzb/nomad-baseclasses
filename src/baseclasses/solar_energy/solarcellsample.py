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

from nomad.metainfo import (Quantity, Reference, SubSection)
from nomad.units import ureg

from .substrate import Substrate
from ..helper.add_solar_cell import add_solar_cell, add_band_gap
from nomad.datamodel.results import Material  # BandGapOptical, Material
from .. import ReadableIdentifiersCustom

from nomad.datamodel.metainfo.basesections import CompositeSystem


def collectBaseProcesses(entry, entry_id, entry_data):
    # read out information
    if "positon_in_experimental_plan" in entry_data:
        entry[entry_id].update(
            {"positon_in_experimental_plan": entry_data["positon_in_experimental_plan"]})
    # Check if it is a layer deposition
    import inspect
    import baseclasses

    entry[entry_id].update({"layer_deposition": False})
    module = entry_data['m_def'].split(".")[0]
    eval(f"exec('import {module}')")
    if baseclasses.LayerDeposition in inspect.getmro(
            eval(entry_data["m_def"])):
        entry[entry_id].update({"layer_deposition": True})

    if "method" in entry_data:
        entry[entry_id].update(
            {"method": entry_data["method"]})

    entry[entry_id].update({"name": entry_data["method"]})
    if "name" in entry_data:
        entry[entry_id].update({"name": entry_data["name"]})

    if "datetime" in entry_data:
        entry[entry_id].update(
            {"datetime": entry_data["datetime"]})

    entry[entry_id].update({"layer_material": ''})
    if "layer" in entry_data:
        entry[entry_id].update({"layer": [layer for layer in entry_data["layer"]]})


def collectJVMeasurement(entry, entry_id, entry_data):
    efficiency = [curve["efficiency"]
                  if "efficiency" in curve else np.nan for curve in entry_data["jv_curve"]]
    fill_factor = [curve["fill_factor"]
                   if "fill_factor" in curve else np.nan for curve in entry_data["jv_curve"]]
    open_circuit_voltage = [curve["open_circuit_voltage"]
                            if "open_circuit_voltage" in curve else np.nan for curve in entry_data["jv_curve"]]
    short_circuit_current_density = [curve["short_circuit_current_density"]
                                     if "short_circuit_current_density" in curve else np.nan for curve in entry_data["jv_curve"]]
    light_intensity = [curve["light_intensity"]
                       if "light_intensity" in curve else np.nan for curve in entry_data["jv_curve"]]
    device_area = entry_data["active_area"] if "active_area" in entry_data else np.nan

    entry[entry_id].update({
        "efficiency": efficiency,
        "fill_factor": fill_factor,
        "open_circuit_voltage": open_circuit_voltage,
        "short_circuit_current_density": short_circuit_current_density,
        "light_intensity": light_intensity,
        "device_area": device_area
    })


def collectEQEMeasurement(entry, entry_id, entry_data):
    band_gap = []
    if "eqe_data" in entry_data:
        band_gap = [eqe["bandgap_eqe"]
                    if "bandgap_eqe" in eqe else np.nan for eqe in entry_data["eqe_data"]]
    if "data" in entry_data and "bandgap_eqe" in entry_data["data"]:
        band_gap.append(entry_data["data"]["bandgap_eqe"])
    entry[entry_id].update({
        "band_gap": band_gap
    })


def sortProcesses(processes):
    processes_working = [p for key, p in processes.items()]
    process_positions = [p["positon_in_experimental_plan"]
                         if "positon_in_experimental_plan" in p else -1 for p in processes_working]
    return [x for _, x in sorted(zip(process_positions, processes_working), key=lambda pair: pair[0])]


def collectSampleData(archive):
    # This function gets all archives whcih reference this archive.
    # Iterates over them and selects relevant data for the result section of the solarcellsample
    # At the end the synthesis steps are ordered
    # returns a dictionary containing synthesis process, JV and EQE information

    from nomad.search import search
    from nomad.app.v1.models import MetadataPagination
    from nomad import files
    import baseclasses
    import inspect

    # search for all archives referencing this archive
    query = {
        'entry_references.target_entry_id': archive.metadata.entry_id,
    }
    pagination = MetadataPagination()
    pagination.page_size = 100
    search_result = search(owner='all', query=query, pagination=pagination,
                           user_id=archive.metadata.main_author.user_id)

    # filter the result by synthesis processes, and JV and EQE Measurement
    result = {"processes": {}, "JVs": {}, "EQEs": {}}

    for res in search_result.data:
        try:
            # Open Archives
            with files.UploadFiles.get(upload_id=res["upload_id"]).read_archive(entry_id=res["entry_id"]) as archive:
                entry_id = res["entry_id"]
                entry_data = archive[entry_id]["data"]
                entry = {entry_id: {}}
                try:
                    entry[entry_id]["elements"] = archive[entry_id]["results"]["material"]["elements"]
                except BaseException:
                    entry[entry_id]["elements"] = []
                # Check if it is a BaseProcess
                module = entry_data['m_def'].split(".")[0]
                eval(f"exec('import {module}')")
                if baseclasses.BaseProcess in inspect.getmro(
                        eval(entry_data["m_def"])):
                    collectBaseProcesses(entry, entry_id, entry_data)
                    result["processes"].update(entry)

                # check if it is a JV measurement
                if baseclasses.solar_energy.jvmeasurement.JVMeasurement in inspect.getmro(
                        eval(entry_data["m_def"])):
                    collectJVMeasurement(entry, entry_id, entry_data)
                    result["JVs"].update(entry)

                # check if EQ Measurement
                if baseclasses.solar_energy.eqemeasurement.EQEMeasurement in inspect.getmro(
                        eval(entry_data["m_def"])):
                    collectEQEMeasurement(entry, entry_id, entry_data)
                    result["EQEs"].update(entry)
        except Exception as e:
            print("Error in processing data: ", e)

    # sort processes by the filled previous process
    result["processes"] = sortProcesses(result["processes"])
    return result


def getLayerForStack(layer):
    if 'layer_material_name' in layer \
            and layer["layer_material_name"] is not None \
            and layer["layer_material_name"].strip():
        return layer["layer_material_name"].strip()
    return layer.get('layer_material')


def addLayerDepositionToStack(archive, process):
    for layer in process.get("layer", []):
        layer_name = getLayerForStack(layer)
        archive.results.properties.optoelectronic.solar_cell.device_stack.append(layer_name)

        if "absorber" in layer["layer_type"].lower():
            archive.results.properties.optoelectronic.solar_cell.absorber.append(layer_name)
            archive.results.properties.optoelectronic.solar_cell.absorber_fabrication = [f"{process['method']}"]

        if "etl" in layer["layer_type"].lower() or "electron" in layer["layer_type"].lower():
            archive.results.properties.optoelectronic.solar_cell.electron_transport_layer.append(layer_name)

        if "htl" in layer["layer_type"].lower() or "hole" in layer["layer_type"].lower():
            archive.results.properties.optoelectronic.solar_cell.hole_transport_layer.append(layer_name)

        if "back" in layer["layer_type"].lower():
            archive.results.properties.optoelectronic.solar_cell.back_contact.append(layer_name)


class BasicSampleWithID(CompositeSystem):

    sample_id = SubSection(
        section_def=ReadableIdentifiersCustom)


class SolcarCellSample(CompositeSystem):

    substrate = Quantity(
        type=Reference(Substrate.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    architecture = Quantity(
        type=str,
        shape=[],
        description="""
            The cell architecture with respect to the direction of current flow and
            the order in which layers are deposited.
            The two most common are nip (also referred to as normal) and pin (also referred to as inverted)
            but there are also a few others, e.g. Back contacted.
            - *nip* architecture means that the electrons are collected at the substrate side.
            The typical example is in perovskite solar cells when a TiO2 electron selective contact is deposited
            between the perovskite and the substrate (e.g. SLG | FTO | TiO2-c | Perovskite | …)
            - *pin* architecture means that it instead is the holes that are collected at the substrate side. The typical example is when a PEDOT:PSS hole selective contact is deposited between the perovskite and the substrate (e.g. SLG | FTO | PEDOT:PSS |Perovskite | …)
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
                    'Schottky'])))

    sample_id = SubSection(
        section_def=ReadableIdentifiersCustom)

    def normalize(self, archive, logger):
        super(
            SolcarCellSample,
            self).normalize(
            archive,
            logger)

        add_solar_cell(archive)
        archive.results.properties.optoelectronic.solar_cell.device_stack = []
        archive.results.properties.optoelectronic.solar_cell.substrate = []
        if self.substrate is not None:
            if self.substrate.substrate is not None:
                archive.results.properties.optoelectronic.solar_cell.substrate = [
                    self.substrate.substrate]
                archive.results.properties.optoelectronic.solar_cell.device_stack.append(
                    self.substrate.substrate)
            if self.substrate.conducting_material is not None:
                archive.results.properties.optoelectronic.solar_cell.substrate.extend(
                    self.substrate.conducting_material)
                archive.results.properties.optoelectronic.solar_cell.device_stack.extend(
                    self.substrate.conducting_material)

        if self.architecture:
            archive.results.properties.optoelectronic.solar_cell.device_architecture = self.architecture

        if self.substrate:
            if self.substrate.pixel_area:
                archive.results.properties.optoelectronic.solar_cell.device_area = self.substrate.pixel_area

        result_data = collectSampleData(archive)

        jv_key = ''
        jv_idx = -1
        jv_eff_val = 0
        for entry in result_data["JVs"]:
            for j, eff in enumerate(result_data["JVs"][entry]["efficiency"]):
                if not np.isnan(eff) and eff > jv_eff_val:
                    jv_key = entry
                    jv_idx = j
                    jv_eff_val = eff

        if jv_key:
            if not np.isnan(result_data["JVs"][jv_key]["efficiency"][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.efficiency = result_data[
                    "JVs"][jv_key]["efficiency"][jv_idx]
            if not np.isnan(result_data["JVs"][jv_key]["fill_factor"][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.fill_factor = result_data[
                    "JVs"][jv_key]["fill_factor"][jv_idx]
            if not np.isnan(result_data["JVs"][jv_key]["open_circuit_voltage"][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.open_circuit_voltage = result_data[
                    "JVs"][jv_key]["open_circuit_voltage"][jv_idx] * ureg('V')
            if not np.isnan(result_data["JVs"][jv_key]["light_intensity"][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.illumination_intensity = result_data[
                    "JVs"][jv_key]["light_intensity"][jv_idx] * ureg('mW/cm**2')
            if not np.isnan(result_data["JVs"][jv_key]["short_circuit_current_density"][jv_idx]):
                archive.results.properties.optoelectronic.solar_cell.short_circuit_current_density = result_data[
                    "JVs"][jv_key]["short_circuit_current_density"][jv_idx] * ureg('mA/cm**2')
            if not np.isnan(result_data["JVs"][jv_key]["device_area"]):
                archive.results.properties.optoelectronic.solar_cell.device_area = result_data[
                    "JVs"][jv_key]["device_area"] * ureg('cm**2')

        eqe_eff_val = 0 * ureg("eV")
        for entry in result_data["EQEs"]:
            for bandgap in result_data["EQEs"][entry]["band_gap"]:
                if np.isnan(bandgap) or bandgap * ureg("eV") < eqe_eff_val:
                    continue
                eqe_eff_val = bandgap * ureg("eV")

        if result_data["EQEs"]:
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

        if result_data["EQEs"] or result_data["JVs"]:
            archive.results.material.functional_type = ["semiconductor", "solarcell"]

        for process in result_data["processes"]:
            if process["layer_deposition"]:
                addLayerDepositionToStack(archive, process)

            if process["layer_deposition"] and process['elements']:
                archive.results.material.elements.extend(process['elements'])

        archive.results.material.elements = list(
            set(archive.results.material.elements))
