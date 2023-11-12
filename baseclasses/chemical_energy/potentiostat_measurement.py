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
import os
import pandas as pd

from nomad.metainfo import (
    Quantity, Reference, SubSection, SectionProxy)

from .. import BaseMeasurement
from .cesample import Environment, ElectroChemicalSetup

from nomad.datamodel.data import ArchiveSection


class PotentiostatProperties(ArchiveSection):

    sample_area = Quantity(
        type=np.dtype(np.float64),
        unit=('cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm^2'))


class VoltammetryCycle(ArchiveSection):

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='s')

    current = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='mA', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'current', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    voltage = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='V', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    control = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='V', a_plot=[
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

    export_this_cycle_to_csv = Quantity(
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
        if self.export_this_cycle_to_csv:
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
            if self.voltage_rhe_uncompensated is not None:
                df["voltage_rhe_uncompensated"] = self.voltage_rhe_uncompensated
            if self.voltage_ref_compensated is not None:
                df["voltage_ref_compensated"] = self.voltage_ref_compensated
            if self.voltage_rhe_compensated is not None:
                df["voltage_rhe_compensated"] = self.voltage_rhe_compensated
            name = name.replace("#", "")
            export_name = f"{name}.csv"
            with archive.m_context.raw_file(export_name, 'w') as outfile:
                df.to_csv(outfile.name)
            self.export_file = export_name


class PotentiostatSetup(ArchiveSection):

    flow_cell_pump_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('mL/minute'),
        a_eln=dict(component='NumberEditQuantity',
                   defaultDisplayUnit='mL/minute'))

    flow_cell_pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='bar'))

    rotation_speed = Quantity(
        type=np.dtype(np.float64),
        unit=('rpm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='rpm'))


class PotentiostatMeasurement(BaseMeasurement):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    station = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    environment = Quantity(
        type=Reference(Environment.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    setup = Quantity(
        type=Reference(ElectroChemicalSetup.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    connected_experiments = Quantity(
        type=Reference(SectionProxy("PotentiostatMeasurement")),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    pretreatment = SubSection(
        section_def=VoltammetryCycle)

    setup_parameters = SubSection(
        section_def=PotentiostatSetup)

    properties = SubSection(
        section_def=PotentiostatProperties)

    def normalize(self, archive, logger):
        super(PotentiostatMeasurement, self).normalize(archive, logger)

        if self.pretreatment is not None:
            self.pretreatment.export_cycle(
                archive, os.path.splitext(self.data_file)[0] + "_pretreatment")
