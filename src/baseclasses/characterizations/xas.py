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
from nomad.metainfo import Quantity

from .. import BaseMeasurement


class XAS(BaseMeasurement):
    '''XAS Measurement'''

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    energy = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='keV')

    seconds = Quantity(
        type=np.dtype(np.float64),
        unit='s',
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'seconds',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    k0 = Quantity(
        type=np.dtype(np.float64),
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'k0',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    k1 = Quantity(
        type=np.dtype(np.float64),
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'k1',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    k3 = Quantity(
        type=np.dtype(np.float64),
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'k3',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        super(XAS, self).normalize(archive, logger)


class XASFluorescence(XAS):

    absorbance_of_the_reference = Quantity(
        type=np.dtype(np.float64),
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'absorbance_of_the_reference',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    fluorescence_yield = Quantity(
        type=np.dtype(np.float64),
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'fluorescence_yield',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        self.method = "XAS Fluoresence"
        super(XASFluorescence, self).normalize(archive, logger)

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_reference = -np.log(self.k1 / self.k0)

        if self.k3 is not None and self.k0 is not None:
            self.fluorescence_yield = self.k3 / self.k0


class XASTransmission(XAS):

    absorbance_of_the_reference = Quantity(
        type=np.dtype(np.float64),
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'absorbance_of_the_reference',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    absorbance_of_the_sample = Quantity(
        type=np.dtype(np.float64),
        shape=['*'], a_plot=[
            {
                'x': 'energy',
                'y': 'absorbance_of_the_sample',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }])

    def normalize(self, archive, logger):
        self.method = "XAS Transmission"
        super(XASTransmission, self).normalize(archive, logger)

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_sample = -np.log(self.k1 / self.k0)

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_reference = -np.log(self.k3 / self.k1)
