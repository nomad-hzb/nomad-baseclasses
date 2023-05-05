import numpy as np

from nomad.metainfo import (
    Quantity,
    Reference,
    Section,
    SectionProxy,
    SubSection, Datetime)

from nomad.datamodel.metainfo.eln import (
    Process,
    Entity,
    SampleID,
    Measurement,
    ElnWithFormulaBaseSection)

from nomad.datamodel.results import Results, Material
from nomad.datamodel.data import ArchiveSection




class State(ArchiveSection):
    disposed_of = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    disposal_date = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))

    storage = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    damage = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))

    comment = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))
    
    
class SampleProperties(ArchiveSection):
    
    length = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm'))
    
    width = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm'))
    
    height_thickness = Quantity(
        type=np.dtype(np.float64),
        unit=('mm'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm'))


class Sample(Entity):

    alternative_id = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))
    
    state = SubSection(
        section_def=State)
    
    properties = SubSection(
        section_def=SampleProperties)

    def normalize(self, archive, logger):
        super(Sample, self).normalize(archive, logger)
