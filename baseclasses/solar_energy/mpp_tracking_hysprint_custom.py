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

from nomad.metainfo import (
    Quantity,
    SubSection,
    Section,
    Reference)

from baseclasses import BasicSample, MeasurementOnBatch
from nomad.datamodel.data import ArchiveSection


class ProcessedEfficiency(ArchiveSection):

    m_def = Section(label_quantity='name', a_plot=[
        {
            "label": "PCE", 'x': 'time', 'y': 'efficiency', 'layout': {
                'yaxis': {
                    "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                "editable": True, "scrollZoom": True}}])

    name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity')
    )

    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the MPP tracking measurement',
        shape=['*'],
        unit='hour')

    efficiency = Quantity(
        type=np.dtype(
            np.float64),
        description='Efficiency array of the MPP tracking measurement',
        shape=['*'])


class PixelData(ProcessedEfficiency):

    include_for_average = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity')
    )

    best_pixel = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    voltage = Quantity(
        type=np.dtype(
            np.float64),
        description='Voltage array of the MPP tracking measurement',
        shape=['*'], unit='V', a_plot=[
            {
                "label": "Voltage", 'x': 'time', 'y': 'voltage', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    current_density = Quantity(
        type=np.dtype(
            np.float64),
        description='Current density array of the MPP tracking measurement',
        shape=['*'],
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


class SampleData(ArchiveSection):
    m_def = Section(label_quantity='name',
                    a_plot=[
                        {
                            'x': 'pixels/:/time',
                            'y': 'pixels/:/efficiency',
                            'layout': {
                                "showlegend": True,
                                'yaxis': {
                                    "fixedrange": False},
                                'xaxis': {
                                    "fixedrange": False}},
                        }])

    name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity')
    )

    parameter = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity')
    )

    solar_cell_area = Quantity(
        type=np.dtype(np.float64),
        unit='cm**2',
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity'))

    samples = Quantity(
        type=Reference(BasicSample.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the MPP tracking measurement',
        shape=['*'],
        unit='hour')

    temperature = Quantity(
        type=np.dtype(
            np.float64),
        description='Temperature of sample during measurement',
        shape=['*'], unit='°C', a_plot=[
            {
                "label": "Temperature", 'x': 'time', 'y': 'temperature', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                            "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    radiation = Quantity(
        type=np.dtype(
            np.float64),
        description='Radiation of sample during measurement',
        shape=['*'], a_plot=[
            {
                "label": "Radiation", 'x': 'time', 'y': 'radiation', 'layout': {
                    'yaxis': {
                        "fixedrange": False}, 'xaxis': {
                        "fixedrange": False}}, "config": {
                    "editable": True, "scrollZoom": True}}])

    pixels = SubSection(
        section_def=PixelData, repeats=True)


class MPPTrackingHsprintCustom(MeasurementOnBatch):
    '''
    MPP tracking measurement
    '''

    m_def = Section(label_quantity='data_file', validate=False)

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    load_data_from_file = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity')
    )

    averaging_grouping_minutes = Quantity(
        type=np.dtype(np.int64),
        default=15,
        a_eln=dict(
            component='NumberEditQuantity'))

    samples = SubSection(
        section_def=SampleData, repeats=True)

    averages = SubSection(
        section_def=ProcessedEfficiency, repeats=True)

    best_pixels = SubSection(
        section_def=ProcessedEfficiency, repeats=True)

    def normalize(self, archive, logger):
        super(MPPTrackingHsprintCustom, self).normalize(archive, logger)
        self.method = "MPP Tracking"

        if self.data_file and self.load_data_from_file:
            self.load_data_from_file = False
            # todo detect file format
            with archive.m_context.raw_file(self.data_file, "br") as f:
                import chardet
                encoding = chardet.detect(f.read())["encoding"]

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                if os.path.splitext(f.name)[-1] != ".csv":
                    return

                from baseclasses.helper.load_mpp_hysprint import load_mpp_file
                data = load_mpp_file(f.name)  # , encoding)

            samples = []
            for sample in data["samples"]:
                df = sample["data"]
                sample_entry = SampleData(
                    name=f"Sample {sample['id']} (in Box)",
                    time=df.groupby(pd.Grouper(key="Timestamp", freq=f"{self.averaging_grouping_minutes}Min"))[
                        "Duration_h"].mean(),
                    temperature=df.groupby(pd.Grouper(
                        key="Timestamp", freq=f"{self.averaging_grouping_minutes}Min"))["InTemperatur"].mean(),
                    radiation=df.groupby(pd.Grouper(
                        key="Timestamp", freq=f"{self.averaging_grouping_minutes}Min"))["InEinstrahlung"].mean()
                )
                pixels = []
                for pixel in sample["pixels"]:
                    df = pixel["data"]
                    pixel_entry = PixelData(
                        name=f"Pixel {pixel['id']}",
                        time=df.groupby(pd.Grouper(key="Timestamp", freq=f"{self.averaging_grouping_minutes}Min"))[
                            "Duration_h"].mean(),
                        voltage=df.groupby(pd.Grouper(key="Timestamp", freq=f"{self.averaging_grouping_minutes}Min"))[
                            "MPPT_V"].mean(),
                        efficiency=df.groupby(pd.Grouper(key="Timestamp", freq=f"{self.averaging_grouping_minutes}Min"))[
                            "MPPT_EFF"].mean(),
                        current_density=df.groupby(pd.Grouper(key="Timestamp", freq=f"{self.averaging_grouping_minutes}Min"))[
                            "MPPT_J"].mean()
                    )
                    pixels.append(pixel_entry)
                sample_entry.pixels = pixels
                samples.append(sample_entry)

            self.samples = samples

        # calculate averages and best pixels
        best_pixels = []
        averages = {}
        for sample in self.samples:
            for pixel in sample.pixels:

                if pixel.best_pixel:
                    pixel_entry = PixelData(
                        name=f"{sample.name} {pixel.name}",
                        time=pixel.time,
                        efficiency=pixel.efficiency
                    )
                    best_pixels.append(pixel_entry)

            if sample.parameter is None:
                continue
            parameter = sample.parameter

            for pixel in sample.pixels:

                if pixel.include_for_average:
                    df = pd.DataFrame()
                    df["time"] = np.floor(
                        pixel.time*self.averaging_grouping_minutes)/4
                    df["efficiency"] = pixel.efficiency
                    df.set_index("time")
                    if parameter in averages:
                        averages[parameter] = averages[parameter].merge(
                            df, on="time")
                    else:
                        averages.update({parameter: df})
        self.best_pixels = best_pixels

        avgs = []
        for parameter, avg_data in averages.items():

            avg_data["eff_mean"] = avg_data[[
                c for c in avg_data.columns if c != "time"]].mean(axis=1)

            avg = ProcessedEfficiency(
                name=parameter,
                time=avg_data.time,
                efficiency=avg_data.eff_mean
            )
            avgs.append(avg)
        self.averages = avgs
