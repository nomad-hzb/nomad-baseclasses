#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 18:20:02 2023

@author: a2853
"""

import numpy as np

from nomad.metainfo import Quantity, Datetime, Section
from nomad.datamodel.data import ArchiveSection


class Atmosphere(ArchiveSection):

    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001012']
    )

    datetime = Quantity(
        type=Datetime,
        a_eln=dict(component='DateTimeEditQuantity'))

    temperature = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000146',
               'https://purl.archive.org/tfsco/TFSCO_00002111'],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    ambient_pressure = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0001025',
               'https://purl.archive.org/tfsco/TFSCO_00005040'],
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(
                minValue=0)))

    relative_humidity = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0015009'],
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))
