import numpy as np

from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Datetime, Quantity, Section

class ProductInfo(ArchiveSection):
    """
    A section for tracking product information and chemical identifiers
    """
    m_def = Section(label_quantity='product_number')
    
    product_number = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='Product Number, as defined by materials sent by the suppliers',
    )

    lot_number = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='LOT, Experiment or Batch Number, as defined by suppliers',
    )

    product_volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
        description='Delivered Product Volume'
    )

    product_weight = Quantity(
        type=np.dtype(np.float64),
        unit=('g'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='g'),
        description='Delivered Product Weight'
    )

    shipping_date = Quantity(
        type=Datetime, 
        a_eln=dict(component='DateTimeEditQuantity'),
        description='Date when product was shipped'
    )

    opening_date = Quantity(
        type=Datetime, 
        a_eln=dict(component='DateTimeEditQuantity'),
        description='Date when product was opened'
    )

    supplier = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='Partner/Company that supplies the product to the end user'
    )
    
    product_description = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'),
        description='Product description'
    )

    cost = Quantity(
        type=np.dtype(np.float64),
        description='Cost of product (in EUR).',
        a_eln=dict(component='NumberEditQuantity'),
    )