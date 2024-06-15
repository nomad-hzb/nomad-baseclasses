import numpy as np

from nomad.metainfo import (
    Quantity,
    SubSection,
    Section,
    Reference,
    MEnum, SectionProxy)

from nomad.datamodel.metainfo.basesections import Activity


from baseclasses.wet_chemical_deposition import PrecursorSolution


class SolutionManufacturing(Activity):
    m_def = Section(a_eln=dict(
        hide=["ending_time", "batch", "lab_id", "steps", "instruments"]))

    solutions = Quantity(
        links=['http://purl.obolibrary.org/obo/CHEBI_75958'],
        type=Reference(PrecursorSolution.m_def),
        shape=['*'],
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(SolutionManufacturing, self).normalize(archive, logger)
        self.method = "Solutin Manufacturing"
