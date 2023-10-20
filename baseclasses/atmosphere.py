#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 18:20:02 2023

@author: a2853
"""

import numpy as np

from nomad.metainfo import Quantity
from nomad.datamodel.data import ArchiveSection


class Atmosphere(ArchiveSection):

    datetime = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))

    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='°C'))

    ambient_pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='bar',
            props=dict(
                minValue=0)))

    relative_humidity = Quantity(
        type=np.dtype(np.float64),
        a_eln=dict(component='NumberEditQuantity'))
