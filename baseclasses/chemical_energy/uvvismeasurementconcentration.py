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
from scipy import signal

from nomad.metainfo import Quantity, Reference, Section, SubSection, Datetime
from nomad.datamodel.metainfo.basesections import Analysis

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objects as go

from baseclasses.solar_energy import UVvisData
from ..helper.utilities import get_reference

class UVvisDataConcentration(UVvisData, PlotSection):

    m_def = Section(a_eln=dict(overview=True))

    concentration = Quantity(
        type=np.dtype(np.float64),
        unit=('ug/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ug/ml'))

    peak_value = Quantity(
        type=np.dtype(np.float64),
        description='The peak value of the wavelength-intensity graph. '
                    'It can be set or it gets automatically computed when saving. '
                    'To recompute it, remove the current value.',
        a_eln=dict(component='NumberEditQuantity'))

    peak_x_value = Quantity(
        type=np.dtype(np.float64),
        unit='nm',
        default=0,
        description='The wavelength value of the automatically computed peak.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    chemical_composition_or_formulas = Quantity(
        type=str,
        description='A list of the elements involved',
        a_eln=dict(component='StringEditQuantity', label='Material'))

    estimated_peak_center = Quantity(
        type=np.dtype(np.float64),
        unit='nm',
        description='The wavelength value where the peak is estimated. This value is usually based on the material.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    peak_search_range = Quantity(
        type=np.dtype(np.float64),
        unit='nm',
        description='This value sets the range where to search for the peak around the estimated peak center.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    reference = Quantity(
        type=Reference(Analysis.m_def),
        description=('References the calibration that was used to calculate the concentration.'),
        a_eln=dict(component='ReferenceEditQuantity', label='Concentration Detection'))

    def normalize(self, archive, logger):
        super(UVvisDataConcentration, self).normalize(archive, logger)

        if self.chemical_composition_or_formulas == 'NH3':
            self.estimated_peak_center = 650
            self.peak_search_range = 20

        if self.intensity is not None and self.wavelength is not None:
            if self.chemical_composition_or_formulas is not None and self.peak_value is None:
                if self.estimated_peak_center is not None and self.peak_search_range is not None:
                    search_area_start = (self.estimated_peak_center - self.peak_search_range)
                    search_area_end = (self.estimated_peak_center + self.peak_search_range)
                else:
                    search_area_start = min(self.wavelength)
                    search_area_end = max(self.wavelength)
                peak_area_df = pd.DataFrame({'intensity': self.intensity, 'wavelength': self.wavelength})
                peak_area_df = peak_area_df.loc[(peak_area_df['wavelength'] >= search_area_start.magnitude) & (peak_area_df['wavelength'] <= search_area_end.magnitude)]
                # sort data to search peak (not sure if uvvis data is always sorted by wavelength)
                peak_area_df = peak_area_df.sort_values('wavelength')

                peak_indices, _ = signal.find_peaks(peak_area_df['intensity'])
                if len(peak_indices) == 1:
                    peak = peak_area_df.iloc[peak_indices[0]]
                elif len(peak_indices) > 1:
                    # if multiple peaks exist, use the highest
                    max_peak_index = peak_indices[np.argmax(peak_area_df['intensity'].iloc[peak_indices])]
                    peak = peak_area_df.iloc[max_peak_index]
                else:
                    peak = {'intensity': None, 'wavelength': 0}
                    logger.error('Could not find peak in given search range.')

                self.peak_value = peak['intensity']
                self.peak_x_value = peak['wavelength']

            fig = go.Figure(
                data=[go.Scatter(name='Calibration Curve', x=self.wavelength, y=self.intensity, mode='lines')])
            fig.update_layout(xaxis_title='Wavelength',
                              yaxis_title='Intensity',
                              title_text='UVvis')
            if self.peak_value is not None and self.peak_x_value is not None:
                fig.add_traces(go.Scatter(x=[self.peak_x_value.magnitude], y=[self.peak_value], mode='markers'))
            self.figures = [PlotlyFigure(label='figure 1', figure=fig.to_plotly_json())]

        if self.concentration is None:
            self.concentration, self.reference = getConcentrationData(archive, logger,
                                                                      self.chemical_composition_or_formulas,
                                                                      self.peak_value)


def getConcentrationData(data_archive, logger, material, peak_value):
    # This function gets all UVvisConcentrationDetection archives.
    # Iterates over them and selects suitable UVvisConcentrationDetection based on material and min/max peak_values.
    # Computes the concentration of the given UVvisMeasurement based on slope and intercept of suitable UVvisConcentrationDetection.
    # Returns a concentration.

    from nomad.search import search, update_by_query
    from nomad.app.v1.models import MetadataPagination
    from nomad import files

    # search for all UVvisConcentrationDetection archives
    query = {
        'entry_type': 'CE_NOME_UVvisConcentrationDetection',
    }
    pagination = MetadataPagination()
    pagination.page_size = 100
    search_result = search(owner='all', query=query, pagination=pagination,
                           user_id=data_archive.metadata.main_author.user_id)

    matching_calibrations = []

    for res in search_result.data:
        try:
            # Open Archives
            with files.UploadFiles.get(upload_id=res["upload_id"]).read_archive(entry_id=res["entry_id"]) as archive:
                entry_id = res["entry_id"]
                entry_data = archive[entry_id]["data"]
                entry = {}
                try:
                    entry['entry_id'] = entry_id
                    entry['upload_id'] = res['upload_id']
                    entry['material_name'] = entry_data['material_name']
                    entry['minimum_peak_value'] = entry_data['minimum_peak_value']
                    entry['maximum_peak_value'] = entry_data['maximum_peak_value']
                    entry['slope'] = entry_data['slope']
                    entry['intercept'] = entry_data['intercept']
                except BaseException:
                    entry['material_name'] = None

                if entry['material_name'] == material:
                    if entry['minimum_peak_value'] <= peak_value <= entry['maximum_peak_value']:
                        matching_calibrations.append(entry)

        except Exception as e:
            logger.error("Error in processing data: ", e)

    concentration = None
    calibration_reference = None
    if len(matching_calibrations) > 0:
        calibration_entry = matching_calibrations[0]
        # compute concentration
        concentration = calibration_entry['slope'] * peak_value + calibration_entry['intercept']
        # reference used UVvisConcentrationDetection
        calibration_reference = get_reference(calibration_entry['upload_id'], calibration_entry['entry_id'])
    else:
        logger.error('For the chosen material and peak value no calibration exists yet.')

    if len(matching_calibrations) > 1:
        logger.warning('For the chosen material and peak value multiple UVvisConcentrationDetections exist.'
                       'The computation of the concentration is based on the calibration linked in '
                       'the \'Concentration Detection\' reference section.')

    return concentration, calibration_reference
