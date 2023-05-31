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
import pandas as pd

from nomad.metainfo import (Quantity, SubSection, MEnum, Reference)
from nomad.datamodel.data import ArchiveSection
from .. import MeasurementOnSample
from .potentiostat_measurement import PotentiostatMeasurement
from .cesample import Environment, ElectroChemicalSetup


class PumpRateMeasurement(MeasurementOnSample):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    electro_chemistry_measurement = Quantity(
        type=Reference(PotentiostatMeasurement.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    environment = Quantity(
        type=Reference(Environment.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    setup = Quantity(
        type=Reference(ElectroChemicalSetup.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    time = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='s')

    flow_rate_set = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='uL/minute', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'flow_rate_set', 'layout': {
                    'yaxis': {
                         "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    flow_rate_measured = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='uL/minute', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'flow_rate_set', 'layout': {
                    'yaxis': {
                         "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    pressure = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='hPa', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'pressure', 'layout': {
                    'yaxis': {
                         "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    def normalize(self, archive, logger):
        super(PumpRateMeasurement, self).normalize(archive, logger)
        self.method = "Pump Rate Measurement"
        if self.data_file:
            try:
                with archive.m_context.raw_file(self.data_file) as f:
                    if os.path.splitext(self.data_file)[-1] == ".csv":
                        data = pd.read_csv(f.name, sep=";",
                                           header=0, skip_blank_lines=False)

                        from baseclasses.helper.utilities import lookup
                        data['time'] = lookup(
                            data.iloc[:, 0], format='%Y-%m-%d %H:%M:%S.%f')
                        data["duration"] = (data.time - data.time.iloc[0])
                        data["duration_s"] = data.duration.dt.total_seconds()
                        self.time = data["duration_s"]
                        self.flow_rate_set = data.iloc[:, 2]
                        self.flow_rate_measured = data.iloc[:, 3]
                        self.pressure = data.iloc[:, 1]
                        self.datetime = data.iloc[0, 0]

            except Exception as e:
                logger.error(e)
