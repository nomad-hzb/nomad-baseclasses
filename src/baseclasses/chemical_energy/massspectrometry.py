import numpy as np
import pandas as pd

from nomad.metainfo import MProxy, Quantity, Reference, Section, SubSection, Datetime
from nomad.datamodel.metainfo.basesections import Analysis
from nomad.datamodel.results import Results, Material

from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
import plotly.graph_objects as go

from nomad.datamodel.data import ArchiveSection
from .. import BaseMeasurement


class MassspectrometrySettings(ArchiveSection):

    channel_count = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    accuracy = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    sensitivity = Quantity(
        type=np.dtype(np.float64),
        unit=('A/mbar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='A/mbar'))

    full_scale_reading = Quantity(
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mbar'))

    detector_gain = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    ion_source = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    extractor_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    detector_voltage = Quantity(
        type=np.dtype(np.float64),
        unit=('V'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='V'))

    filament = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))


class MassspectrometrySpectrum(ArchiveSection):
    m_def = Section(label_quantity='chemical_name')

    chemical_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    spectrum_data = Quantity(
        type=np.dtype(np.float64), unit="mbar", shape=["*"])


class Massspectrometry(BaseMeasurement):

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    recipe = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    time = Quantity(
        type=Datetime, shape=["*"])

    settings = SubSection(
        section_def=MassspectrometrySettings)

    data = SubSection(
        section_def=MassspectrometrySpectrum, repeats=True)

    def normalize(self, archive, logger):
        self.method = "Massspectrometry"
        super(Massspectrometry, self).normalize(archive, logger)
