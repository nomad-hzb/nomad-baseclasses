import numpy as np
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Quantity, Section, SubSection

from baseclasses import LayerProperties


class CarbonPasteLayerProperties(LayerProperties):
    """
    A special class to track additional information for when the Layer is based on carbon paste.
    """

    supplier = Quantity(
        type=str,
        description='Supplier of the carbon paste material.',
        a_eln=dict(component='StringEditQuantity'),
    )

    batch = Quantity(
        type=str,
        description='Batch number of the carbon paste material.',
        a_eln=dict(component='StringEditQuantity'),
    )

    drying_time = Quantity(
        type=np.dtype(np.float64),
        unit='s',
        description='Drying time for the carbon paste layer.',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
    )

    cost = Quantity(
        type=np.dtype(np.float64),
        description='Cost of the carbon paste material (in EUR).',
        a_eln=dict(component='NumberEditQuantity'),
    )
