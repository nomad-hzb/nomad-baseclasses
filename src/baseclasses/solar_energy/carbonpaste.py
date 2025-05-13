import numpy as np
from nomad.metainfo import Quantity, SubSection
from baseclasses import LayerProperties

class CarbonPasteLayer(LayerProperties):
    supplier = Quantity(
        type=str,
        description="Supplier of the carbon paste material.",
        a_eln=dict(component='StringEditQuantity'),
    )

    batch = Quantity(
        type=str,
        description="Batch number of the carbon paste material.",
        a_eln=dict(component='StringEditQuantity'),
    )

    # deposition_method = Quantity(
    #     type=str,
    #     description="Method used for depositing the carbon paste.",
    #     a_eln=dict(
    #         component='EnumEditQuantity',
    #         props=dict(suggestions=['Screen Printing', 'Doctor Blade', 'Drop Casting']),
    #     ),
    # )

    drying_time = Quantity(
        type=np.dtype(np.float64),
        unit='s',
        description="Drying time for the carbon paste layer.",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
    )

    cost = Quantity(
        type=np.dtype(np.float64),
        unit='EUR',
        description="Cost of the carbon paste material.",
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='EUR'),
    )

    properties = Quantity(
        type=str,
        description="Additional properties of the carbon paste layer.",
        a_eln=dict(component='StringEditQuantity'),
    )