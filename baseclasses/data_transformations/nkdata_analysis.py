import numpy as np
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    Entity, AnalysisResult, SectionReference
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


class NKDataResult(AnalysisResult):
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


class NKData(Entity):
    chemical_composition_or_formulas = Quantity(
        type=str,
        description=(
            'A list of the elements involved'),
        a_eln=dict(component='StringEditQuantity'))

    data_file = Quantity(
        type=str,
        description='The Data file providing the input data.',
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor')
    )

    data_reference = Quantity(
        type=str,
        description='A link/URL to the reference of the data file in literature.',
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


    data = SubSection(
        section_def=NKDataResult,
        description='The data.',
    )

    def normalize(self, archive, logger):
        if not archive.results:
            archive.results = Results()
        if not archive.results.material:
            archive.results.material = Material()

        if self.chemical_composition_or_formulas:
            from baseclasses.helper.utilities import get_elements_from_formula
            formula_split = self.chemical_composition_or_formulas.split(',')
            elements_final = []
            for formula in formula_split:
                try:
                    elements = get_elements_from_formula(formula.strip())
                    elements_final.extend(elements)
                except Exception as e:
                    logger.warn(f'could not analyse layer material {formula}', exc_info=e)
            archive.results.material.elements = elements_final

        self.data.normalize(archive, logger)
        super(NKData, self).normalize(archive, logger)
