#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numpy as np

from nomad.metainfo import (Quantity, Reference, SubSection, Section, Datetime, MEnum)

from .. import ReadableIdentifiersCustom

from .cesample import (build_initial_id, create_id, export_lab_id, CESample,
                       SubstrateProperties, CatalystSynthesis)

def build_recipe_id_base(archive, recipe_type, element, deposition_method):
    recipe_type_mapping = {
        'Cathode Recipe (CR)': 'CR',
        'Anode Recipe (AR)': 'AR'
    }
    deposition_method_mapping = {
        'Spray Dep': 'SD',
        'Ultrasonic Nozzle': 'UN',
        'Dropcast': 'DC'
    }
    recipe_id_list = [
        recipe_type_mapping.get(recipe_type),
        element,
        deposition_method_mapping.get(deposition_method)]
    return '_'.join(recipe_id_list)


class CENECCElectrodeRecipeID(ReadableIdentifiersCustom):

    m_def = Section(
        a_eln=dict(
            hide=["institute", "owner", "datetime", "sample_owner", "sample_short_name", "sample_id", "short_name"]
        ))

    recipe_type = Quantity(
        type=MEnum(['Cathode Recipe (CR)', 'Anode Recipe (AR)']),
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    element = Quantity(
        type=str,
        shape=[],
        a_eln=dict(component='StringEditQuantity'))

    deposition_method = Quantity(
        type=MEnum('Spray Dep', 'Ultrasonic Nozzle', 'Dropcast'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    def normalize(self, archive, logger):
        super(CENECCElectrodeRecipeID, self).normalize(archive, logger)

        if archive.data.lab_id:
            return
        if self.recipe_type is not None and self.element is not None and self.deposition_method is not None:
            self.lab_id = build_recipe_id_base(
                archive=archive,
                recipe_type=self.recipe_type,
                element=self.element,
                deposition_method=self.deposition_method)
        create_id(archive, self.lab_id)


class CENECCElectrodeRecipe(CESample):

    electrode_recipe_id = SubSection(section_def=CENECCElectrodeRecipeID)

    deposition_temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'))

    n2_deposition_pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='bar'))

    mass_loading = Quantity(
        type=np.dtype(np.float64),
        unit=('mg/cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/cm^2'))

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(
            component='RichTextEditQuantity',
            label='Remarks'))

    substrate = SubSection(
        section_def=SubstrateProperties)

    solvents_and_ionomer = SubSection(
        section_def=CatalystSynthesis, repeats=True)

    def normalize(self, archive, logger):
        self.chemical_composition_or_formulas = self.electrode_recipe_id.element
        super(CENECCElectrodeRecipe, self).normalize(archive, logger)
        export_lab_id(archive, self.lab_id)


class CENECCElectrodeID(ReadableIdentifiersCustom):

    m_def = Section(
        a_eln=dict(
            hide=["sample_owner", "sample_short_name", "sample_id", "short_name"]
        ))

    institute = Quantity(
        type=str,
        description='Alias/short name of the home institute of the owner, i.e. *HZB*.',
        default='CE-NECC',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'CE-NECC'])))

    owner = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=[
                    'Matthew Mayer',
                    'Siddharth Gupta',
                    'Christina Roukounaki',
                    'Gumaa El-Nagar',
                    'Uttam Gupta',
                ])))

    recipe = Quantity(
        type=Reference(CENECCElectrodeRecipe.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):

        author = archive.metadata.main_author
        if author and self.owner is None:
            self.owner = ' '.join([author.first_name, author.last_name])

        super(CENECCElectrodeID, self).normalize(archive, logger)

        if archive.data.lab_id:
            return
        if not self.datetime:
            from datetime import date
            self.datetime = date.today()

        if self.institute and self.owner and self.datetime:
            id_base = [build_initial_id(self.institute, self.owner, self.datetime),
                       self.recipe.lab_id]
            self.lab_id = '_'.join(id_base)
        create_id(archive, self.lab_id)

class CENECCElectrode(CESample):

    electrode_id = SubSection(section_def=CENECCElectrodeID)

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(
            component='RichTextEditQuantity',
            label='Remarks'))

    def normalize(self, archive, logger):
        self.chemical_composition_or_formulas = self.electrode_id.recipe.electrode_recipe_id.element
        super(CENECCElectrode, self).normalize(archive, logger)
        export_lab_id(archive, self.lab_id)
        if archive.data == self and self.name:
            archive.metadata.entry_name = self.name
