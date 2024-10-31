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
from nomad.metainfo import Quantity, Reference

from .. import BaseMeasurement
from .cesample import ElectroChemicalSetup, Environment
from .potentiostat_measurement import PotentiostatMeasurement


class PumpRateMeasurement(BaseMeasurement):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    electro_chemistry_measurement = Quantity(
        type=Reference(PotentiostatMeasurement.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    environment = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007223'],
        type=Reference(Environment.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    setup = Quantity(
        links=['https://w3id.org/nfdi4cat/voc4cat_0007230'],
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
        self.method = "Pump Rate Measurement"
        super(PumpRateMeasurement, self).normalize(archive, logger)
