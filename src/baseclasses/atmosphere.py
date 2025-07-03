#!/usr/bin/env python3
"""
Created on Fri Oct 20 18:20:02 2023

@author: a2853
"""

import numpy as np
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Datetime, Quantity, Section


class Atmosphere(ArchiveSection):
    m_def = Section(links=['https://purl.archive.org/tfsco/TFSCO_00001012'])

    datetime = Quantity(type=Datetime, a_eln=dict(component='DateTimeEditQuantity'))

    temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    ambient_pressure = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001025',
            'https://purl.archive.org/tfsco/TFSCO_00002027',
        ],
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(minValue=0),
        ),
    )

    relative_humidity = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0015009'],
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'),
    )

    # adding oxygen_level so that Atmosphere can be also used for tracking Glovebox conditions
    oxygen_level_ppm = Quantity(
        # links=[''],
        type=np.dtype(np.float64),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ppm',
        ),
    )
