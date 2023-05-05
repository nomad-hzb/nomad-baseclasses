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
from datetime import datetime

from .. import MeasurementOnSample
from nomad.metainfo import (Quantity)


def getHeader(file):
    header = 0
    date_line_found = False
    date_line = None
    with open(file, "r") as f:
        for i, line in enumerate(f):
            if line.startswith("#D") and not date_line_found:
                date_line_found = True
                date_line = line
            if line.startswith("#"):
                continue
            header = i - 1
            break
    return header, date_line.strip()


class XAS(MeasurementOnSample):
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
        self.method = "XAS"

        if self.data_file:

            if os.path.splitext(self.data_file)[-1] == ".dat":
                with archive.m_context.raw_file(self.data_file) as f:
                    import pandas as pd
                    header, dateline = getHeader(f.name)
                    data = pd.read_csv(f.name, header=header, sep="\t")

                if dateline is not None:
                    datetime_object = datetime.strptime(
                        dateline, '#D\t%a %b %d\t%H:%M:%S\t%Y')
                    self.datetime = datetime_object.strftime(
                        "%Y-%m-%d %H:%M:%S.%f")

                self.energy = data["#monoE"]
                self.seconds = data["Seconds"]
                self.k0 = data["K0"]
                self.k1 = data["K1"]
                self.k3 = data["K3"]


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
        super(XASFluorescence, self).normalize(archive, logger)
        self.method = "XAS Fluoresence"

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_reference = -np.log(self.k1/self.k0)

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
        super(XASTransmission, self).normalize(archive, logger)
        self.method = "XAS Transmission"

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_sample = -np.log(self.k1/self.k0)

        if self.k1 is not None and self.k0 is not None:
            self.absorbance_of_the_reference = -np.log(self.k3 / self.k1)
