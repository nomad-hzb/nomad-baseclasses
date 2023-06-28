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
from nomad.units import ureg
from .potentiostat_measurement import PotentiostatMeasurement
from .cesample import Environment, ElectroChemicalSetup


class PhaseFluorometryOxygen(MeasurementOnSample):

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
        unit='minute')

    oxygen = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='umol/L', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'oxygen', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    temperature = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='°C', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'temperature', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    phase = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], unit='degree', a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'phase', 'layout': {
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

    amplitude = Quantity(
        type=np.dtype(
            np.float64), shape=['n_values'], a_plot=[
            {
                "label": "Current", 'x': 'time', 'y': 'amplitude', 'layout': {
                    'yaxis': {
                         "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    def normalize(self, archive, logger):
        self.method = "Phase Fluorometry"
        super(PhaseFluorometryOxygen, self).normalize(archive, logger)
