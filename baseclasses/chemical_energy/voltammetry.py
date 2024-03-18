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
import pandas as pd
import os

from nomad.metainfo import (Quantity, SubSection, Section)
from .potentiostat_measurement import PotentiostatMeasurement, VoltammetryCycle
from nomad.datamodel.data import ArchiveSection

# encoding = "iso-8859-1"


# def headeranddelimiter(file):
#     header = 0
#     header_found = False
#     decimal = "."
#     with open(file, "br") as f:
#         for i, line in enumerate(f):
#             line = line.decode(encoding)
#             if line.startswith("mode"):
#                 header = i
#                 header_found = True
#             if header_found:
#                 if "," in line and "." not in line:
#                     decimal = ","
#                 if "." in line and decimal == ",":
#                     raise Exception("decimal delimiter . and , found")

#     return header, decimal

class VoltammetryCycleWithPlot(VoltammetryCycle):
    m_def = Section(
        a_plot=[{
            'label': 'Current density over RHE',
            'x': 'voltage_rhe_compensated',
            'y': 'current_density',
            'layout': {
                'yaxis': {
                    "fixedrange": False},
                'xaxis': {
                    "fixedrange": False}},
        },
            {
                'label': 'Current',
                'x': 'voltage',
                'y': 'current',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
        }])


class Voltammetry(PotentiostatMeasurement):

    metadata_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    voltage_shift = Quantity(
        type=np.dtype(np.float64), default=0,
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    resistance = Quantity(
        type=np.dtype(np.float64), default=0,
        unit=('ohm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ohm'))

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='s')

    current = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='mA', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'current', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    voltage = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='V', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    control = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='V', a_plot=[
            {
                "label": "Control", 'x': 'time', 'y': 'control', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    charge = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='mC', a_plot=[
            {
                "label": "Charge", 'x': 'time', 'y': 'charge', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    current_density = Quantity(
        type=np.dtype(
            np.float64),
        shape=['n_values'],
        unit='mA/cm^2',
        a_plot=[
            {
                "label": "Current Density",
                'x': 'time',
                'y': 'current_density',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
                "config": {
                    "editable": True,
                    "scrollZoom": True}}])

    charge_density = Quantity(
        type=np.dtype(
            np.float64),
        shape=['n_values'],
        unit='mC/cm^2',
        a_plot=[
            {
                "label": "Charge Density",
                'x': 'time',
                'y': 'charge_density',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
                "config": {
                    "editable": True,
                    "scrollZoom": True}}])

    voltage_rhe_uncompensated = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='V', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage_rhe_uncompensated', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    voltage_ref_compensated = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='V', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage_ref_compensated', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    voltage_rhe_compensated = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='V', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage_rhe_compensated', 'layout': {
                    'yaxis': {
                         "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    cycles = SubSection(
        section_def=VoltammetryCycleWithPlot, repeats=True)

    export_data_to_csv = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    export_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor')
    )

    def export_cycle(self, archive,  name):
        cycles = [self]
        if getattr(self, "cycles"):
            cycles = self.cycles
        self.export_data_to_csv = False
        df_list = []
        for idx, cycle in enumerate(cycles):
            df = pd.DataFrame()
            if cycle.time is not None:
                df["time"] = cycle.time
            if cycle.current is not None:
                df["current"] = cycle.current
            if cycle.voltage is not None:
                df["voltage"] = cycle.voltage
            if cycle.control is not None:
                df["control"] = cycle.control
            if cycle.charge is not None:
                df["charge"] = cycle.charge
            if cycle.current_density is not None:
                df["current_density"] = cycle.current_density
            if getattr(cycle, "charge_density", None) is not None:
                df["charge_density"] = cycle.charge_density
            if cycle.voltage_rhe_uncompensated is not None:
                df["voltage_rhe_uncompensated"] = cycle.voltage_rhe_uncompensated
            if cycle.voltage_ref_compensated is not None:
                df["voltage_ref_compensated"] = cycle.voltage_ref_compensated
            if cycle.voltage_rhe_compensated is not None:
                df["voltage_rhe_compensated"] = cycle.voltage_rhe_compensated
            df_list.append(df)

        df_final = pd.concat(df_list, keys=[idx for idx in range(len(cycles))])
        name = name.replace("#", "")
        export_name = f"{name}.csv"
        with archive.m_context.raw_file(export_name, 'w') as outfile:
            df_final.to_csv(outfile.name)
        self.export_file = export_name

    def derive_n_values(self):
        if self.current or self.voltage:
            return max(len(self.current), len(self.voltage))
        return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def normalize(self, archive, logger):
        super(Voltammetry, self).normalize(archive, logger)

        # if self.metadata_file:
        #     try:
        #         with archive.m_context.raw_file(self.metadata_file) as f:
        #             if os.path.splitext(self.data_file)[-1] == ".mps":
        #                 from ..helper.mps_file_parser import read_mps_file
        #                 self.metadata = read_mps_file(f.name)

        #     except Exception as e:
        #         logger.error(e)

        if self.cycles is not None:
            for i, cycle in enumerate(self.cycles):
                name = f"{os.path.splitext(self.data_file)[0]}_cycle_{i}"
                cycle.export_cycle(archive, name)

        if self.export_data_to_csv:
            self.export_cycle(archive, os.path.splitext(
                self.data_file)[0] + "_data")

        if self.resistance is not None and self.voltage_shift is not None:
            resistance = np.array(self.resistance)
            shift = np.array(self.voltage_shift)
            if self.voltage is not None and self.current is not None:
                volts = np.array(self.voltage)
                current = np.array(self.current)/1000
                self.voltage_rhe_compensated = (
                    volts + shift) - (current*resistance)
                self.voltage_ref_compensated = (
                    volts) - (current*resistance)
                self.voltage_rhe_uncompensated = volts + shift

            if self.cycles is not None:
                for cycle in self.cycles:
                    if cycle.voltage is not None and cycle.current is not None:
                        volts = np.array(cycle.voltage)
                        current = np.array(cycle.current)/1000
                        cycle.voltage_rhe_compensated = (
                            volts + shift) - (current*resistance)
                        cycle.voltage_ref_compensated = (
                            volts) - (current*resistance)
                        cycle.voltage_rhe_uncompensated = volts + shift

            area = None
            try:
                if self.properties is not None and getattr(self.properties, "sample_area", False):
                    area = self.properties.sample_area
            except:
                pass
            if self.samples and len(self.samples) == 1 and self.samples[0]["reference"] \
                    and getattr(self.samples[0]["reference"], "active_area", None):
                area = self.samples[0]["reference"].active_area
                self.properties.sample_area = area

            if self.properties is not None and area is not None:
                if self.current is not None:
                    self.current_density = self.current / area
                if self.charge is not None:
                    self.charge_density = self.charge / area

                if self.cycles is not None:
                    for cycle in self.cycles:
                        if cycle.current is not None:
                            cycle.current_density = cycle.current / area
