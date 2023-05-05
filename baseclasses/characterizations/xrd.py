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

from nomad.metainfo import (
    Quantity,
    Section,
    SubSection)
from nomad.datamodel.data import ArchiveSection

from .. import MeasurementOnSample


class XRDData(ArchiveSection):
    m_def = Section(
        label_quantity='name', a_plot=[
            {
                'x': 'angle', 'y': 'intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                            "scrollZoom": True, 'staticPlot': False, }}])

    name = Quantity(
        type=str)

    metadata = Quantity(
        type=str, a_browser=dict(adaptor='RawFileAdaptor'))

    angle_type = Quantity(
        type=str)

    angle = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], unit='degree', a_plot=[
            {
                'x': 'angle', 'y': 'intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    intensity = Quantity(
        type=np.dtype(
            np.float64), shape=['*'], a_plot=[
            {
                'x': 'angle', 'y': 'intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])


class XRDShiftedData(XRDData):
    m_def = Section(
        label_quantity='model', a_plot=[
            {
                'x': 'angle', 'y': 'intensity', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                            "scrollZoom": True, 'staticPlot': False, }}])

    model = Quantity(
        type=str, a_eln=dict(component='StringEditQuantity'))

    goniometer_radius = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))

    displacement = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))


class XRD(MeasurementOnSample):
    '''UV vis Measurement'''

    m_def = Section(
        a_eln=dict(hide=['certified_values', 'certification_institute']))

    data_file = Quantity(
        type=str,
        shape=['*'],
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    measurements = SubSection(
        section_def=XRDData, repeats=True)

    shifted_data = SubSection(
        section_def=XRDShiftedData, repeats=True)

    identifier = Quantity(
        type=str)

    def normalize(self, archive, logger):
        super(XRD, self).normalize(archive, logger)
        self.method = "XRD"

        if self.data_file:

            if self.identifier == "FHI_IRIS":
                from nomad.datamodel.metainfo.eln.helper.fhi_archive import get_xrd_data_entry
                measurements, shifted_data = get_xrd_data_entry(
                    archive, self.data_file)

                self.measurements = measurements
                self.shifted_data = shifted_data

            if self.identifier == "HZB_WANNSEE":
                measurements = []
                for data_file in self.data_file:
                    if os.path.splitext(data_file)[-1] == ".xy":
                        with archive.m_context.raw_file(data_file) as f:
                            import pandas as pd
                            data = pd.read_csv(
                                f.name, skiprows=1, sep=" ", header=None)
                            measurements.append(XRDData(
                                angle_type="2Theta",
                                angle=data[0],
                                intensity=data[1]
                            ))

                self.measurements = measurements
