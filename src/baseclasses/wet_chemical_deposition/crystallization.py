#!/usr/bin/env python3
"""
Created on Wed Sep  6 16:09:39 2023

@author: a2853
"""
from .wet_chemical_deposition import WetChemicalDeposition


class Crystallization(WetChemicalDeposition):
    '''Base class for Crystallization of a Crystal'''

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        self.method = "Crystallization"
