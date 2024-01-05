import numpy as np
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    Analysis, AnalysisResult, SectionReference
)
from nomad.datamodel.results import (
    Results,
    Material,
)
from nomad.metainfo import (
    Quantity,
    SubSection, Section)

from .data_baseclasses import DataWithStatistics
from .. import BaseMeasurement


class InputData(SectionReference):
    data_file = Quantity(
        type=str,
        description='The Data file providing the input data.',
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor')
    )

    data_reference = Quantity(
        type=str,
        description='A lin/URL to the reference of the data file in literature.',
        a_eln=ELNAnnotation(
            component='URLEditQuantity',
        )
    )

    reference = Quantity(
        type=BaseMeasurement,
        description='A reference to a measurement.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='Measurement Reference',
        ),
    )


class nkDataAnalysisResult(AnalysisResult):
    n_data = SubSection(
        section_def=DataWithStatistics,
        description='The n data.',
    )

    k_data = SubSection(
        section_def=DataWithStatistics,
        description='The k data.',
    )

    wavelength = Quantity(
        type=np.dtype(np.float64),
        unit=('nm'),
        shape=['*'])

    m_def = Section(
        a_plot=[{
            'label': 'n data over wavelength',
            'x': 'wavelength',
            'y': 'n_data/data',
            'layout': {
                'yaxis': {
                    "fixedrange": False},
                'xaxis': {
                    "fixedrange": False}},
        },
            {
                'label': 'k data over wavelength',
                'x': 'wavelength',
                'y': 'k_data/data',
                'layout': {
                    'yaxis': {
                        "fixedrange": False},
                    'xaxis': {
                        "fixedrange": False}},
            }
        ])

    def normalize(self, archive, logger):
        self.n_data.normalize(archive, logger)
        self.k_data.normalize(archive, logger)


class nkDataAnalysis(Analysis):
    chemical_composition_or_formulas = Quantity(
        type=str,
        description=(
            'A list of the elements involved'),
        a_eln=dict(component='StringEditQuantity'))

    inputs = SubSection(
        section_def=InputData,
        description='The reference for the input data.',
        repeats=True
    )

    outputs = SubSection(
        section_def=nkDataAnalysisResult,
        description='The output data.',
        repeats=True
    )

    def normalize(self, archive, logger):
        self.method = 'nk data analysis'

        if not archive.results:
            archive.results = Results()
        if not archive.results.material:
            archive.results.material = Material()

        if self.chemical_composition_or_formulas:
            from nomad.atomutils import Formula
            try:
                formula = Formula(self.chemical_composition_or_formulas)
                formula.populate(section=archive.results.material)
            except Exception as e:
                logger.warn('could not analyse layer material', exc_info=e)

        for output in self.outputs:
            output.normalize(archive, logger)
