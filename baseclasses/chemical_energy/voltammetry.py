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
from datetime import datetime
import os

from nomad.units import ureg

from nomad.metainfo import (Quantity, SubSection, Section)
from nomad.datamodel.data import ArchiveSection

from .potentiostat_measurement import PotentiostatMeasurement, VoltammetryCycle

encoding = "iso-8859-1"


def headeranddelimiter(file):
    header = 0
    header_found = False
    decimal = "."
    with open(file, "br") as f:
        for i, line in enumerate(f):
            line = line.decode(encoding)
            if line.startswith("mode"):
                header = i
                header_found = True
            if header_found:
                if "," in line and "." not in line:
                    decimal = ","
                if "." in line and decimal == ",":
                    raise Exception("decimal delimiter . and , found")

    return header, decimal


class VoltammetryCycleWithPlot(VoltammetryCycle):
    m_def = Section(
        a_plot=[{
            'label': 'Current density over RHE',
            'x': 'voltage_rhe',
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

        self.export_this_cycle_to_csv = False
        df = pd.DataFrame()
        if self.time is not None:
            df["time"] = self.time
        if self.current is not None:
            df["current"] = self.current
        if self.voltage is not None:
            df["voltage"] = self.voltage
        if self.control is not None:
            df["control"] = self.control
        if self.charge is not None:
            df["charge"] = self.charge
        if self.current_density is not None:
            df["current_density"] = self.current_density
        if self.charge_density is not None:
            df["charge_density"] = self.charge_density
        if self.voltage_rhe_uncompensated is not None:
            df["voltage_rhe_uncompensated"] = self.voltage_rhe_uncompensated
        if self.voltage_ref_compensated is not None:
            df["voltage_ref_compensated"] = self.voltage_ref_compensated
        if self.voltage_rhe_compensated is not None:
            df["voltage_rhe_compensated"] = self.voltage_rhe_compensated

        export_name = f"{name}.csv"
        with archive.m_context.raw_file(export_name, 'w') as outfile:
            df.to_csv(outfile.name)
        self.export_file = export_name

    def derive_n_values(self):
        if self.current or self.voltage:
            return max(len(self.current), len(self.voltage))
        return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def normalize(self, archive, logger):
        super(Voltammetry, self).normalize(archive, logger)
        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:

                    if os.path.splitext(self.data_file)[-1] == ".mpt":
                        from ..helper.mps_file_parser import read_mpt_file
                        from ..helper.mpt_get_archive import get_voltammetry_data

                        metadata, data, _ = read_mpt_file(f.name)
                        get_voltammetry_data(data, self)

                    if os.path.splitext(self.data_file)[-1] == ".cor":
                        from ..helper.corr_ware_parser import get_header_data_corrware
                        metadata, data, _ = get_header_data_corrware(
                            filename=f.name)
                        if "curve" in data.index.name:
                            if self.cycles is None:
                                c = 0
                                self.cycles = []
                                while (c in data.index):
                                    curve = data.loc[c]
                                    cycle = VoltammetryCycleWithPlot()
                                    cycle.voltage = curve["E(Volts)"]
                                    cycle.current_density = curve["I(A/cm2)"] * \
                                        ureg("A/cm**2")
                                    cycle.current = curve["I(A/cm2)"] * \
                                        ureg("A")
                                    cycle.time = curve["T(Seconds)"]
                                    self.cycles.append(cycle)
                                    c += 1
                        else:
                            self.voltage = data["E(Volts)"]
                            self.current_density = data["I(A/cm2)"] * \
                                ureg("A/cm**2")
                            self.time = data["T(Seconds)"]

                        datetime_str = metadata["Datetime"]
                        datetime_object = datetime.strptime(
                            datetime_str, '%m-%d-%Y %H:%M:%S')
                        self.datetime = datetime_object.strftime(
                            "%Y-%m-%d %H:%M:%S.%f")

                    if os.path.splitext(self.data_file)[-1] == ".DTA" and self.cycles is None:
                        from ..helper.gamry_parser import get_header_and_data
                        from ..helper.gamry_archive import get_voltammetry_data, get_meta_data
                        metadata, data = get_header_and_data(filename=f.name)

                        if len(data) > 1:
                            if self.cycles is None:
                                self.cycles = []
                                for curve in data:
                                    cycle = VoltammetryCycleWithPlot()
                                    get_voltammetry_data(
                                        curve, cycle)
                                    self.cycles.append(cycle)

                        if len(data) == 1:
                            get_voltammetry_data(
                                data[0], self)

                        get_meta_data(metadata, self)

            except Exception as e:
                logger.error(e)

        if self.metadata_file:
            try:
                with archive.m_context.raw_file(self.metadata_file) as f:
                    if os.path.splitext(self.data_file)[-1] == ".mps":
                        from ..helper.mps_file_parser import read_mps_file
                        self.metadata = read_mps_file(f.name)

            except Exception as e:
                logger.error(e)

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
