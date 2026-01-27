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
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import MEnum, Quantity, Reference, Section, SubSection

from .. import ReadableIdentifiersCustom
from .cesample import (
    CESample,
    SubstrateProperties,
    build_initial_id,
    create_id,
    export_lab_id,
)


def build_recipe_id_base(archive, recipe_type, element, deposition_method):
    recipe_type_mapping = {'Cathode Recipe (CR)': 'CR', 'Anode Recipe (AR)': 'AR'}
    deposition_method_mapping = {
        'Spray Dep': 'SD',
        'Ultrasonic Nozzle': 'UN',
        'Dropcast': 'DC',
    }
    recipe_id_list = [
        recipe_type_mapping.get(recipe_type),
        element,
        deposition_method_mapping.get(deposition_method),
    ]
    return '_'.join(recipe_id_list)


class CENECCElectrodeRecipeID(ReadableIdentifiersCustom):
    m_def = Section(
        a_eln=dict(
            hide=[
                'institute',
                'owner',
                'datetime',
                'sample_owner',
                'sample_short_name',
                'sample_id',
                'short_name',
            ]
        )
    )

    recipe_type = Quantity(
        type=MEnum(['Cathode Recipe (CR)', 'Anode Recipe (AR)']),
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    element = Quantity(type=str, shape=[], a_eln=dict(component='StringEditQuantity'))

    element_mass = Quantity(
        type=np.dtype(np.float64),
        unit=('mg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg'),
    )

    deposition_method = Quantity(
        type=MEnum('Spray Dep', 'Ultrasonic Nozzle', 'Dropcast'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ),
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if archive.data.lab_id:
            return
        if (
            self.recipe_type is not None
            and self.element is not None
            and self.deposition_method is not None
        ):
            self.lab_id = build_recipe_id_base(
                archive=archive,
                recipe_type=self.recipe_type,
                element=self.element,
                deposition_method=self.deposition_method,
            )
        create_id(archive, self.lab_id)


class Solvent(ArchiveSection):
    type = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['H2O', 'Isopropanol', 'Ethanol']),
        ),
    )

    volume = Quantity(
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'),
    )


class Ionomer(ArchiveSection):
    type = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['Nafion'])),
    )

    mass = Quantity(
        type=np.dtype(np.float64),
        unit=('mg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg'),
    )


class SearchableCESample(CESample):
    entry_dict_hash = Quantity(
        type=str,
        description='Searchable string for easy comparison of '
        'SearchableCESample entries in terms of their similarity.',
        a_display={'visible': False},
    )

    def _normalize_string(self, s: str) -> str:
        import re

        s = s.lower()
        return re.sub(r'[^a-z0-9]', '', s)

    def _normalize_object(self, obj):
        if isinstance(obj, dict):
            return {
                self._normalize_string(k)
                if isinstance(k, str)
                else k: self._normalize_object(v)
                for k, v in obj.items()
                if v is not None and v not in (' ', '', {}, [])
            }

        elif isinstance(obj, list):
            return [self._normalize_object(v) for v in obj]

        elif isinstance(obj, tuple):
            return tuple(self._normalize_object(v) for v in obj)

        elif isinstance(obj, str):
            return self._normalize_string(obj)

        else:
            return obj


class CENECCElectrodeRecipe(SearchableCESample):
    electrode_recipe_id = SubSection(section_def=CENECCElectrodeRecipeID)

    deposition_temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    n2_deposition_pressure = Quantity(
        type=np.dtype(np.float64),
        unit=('bar'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='bar'),
    )

    mass_loading = Quantity(
        type=np.dtype(np.float64),
        unit=('mg/cm^2'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/cm^2'),
    )

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity', label='Remarks'),
    )

    substrate = SubSection(section_def=SubstrateProperties)

    solvent = SubSection(section_def=Solvent, repeats=True)

    ionomer = SubSection(section_def=Ionomer, repeats=True)

    def set_entry_dict_hash(self):
        from nomad.utils import hash

        complete_entry_dict = self.m_to_dict()
        keys_to_remove = {
            'entry_dict_hash',
            'm_def',
            'name',
            'datetime',
            'lab_id',
            'chemical_composition_or_formulas',
            'description',
        }
        for k in keys_to_remove:
            complete_entry_dict.pop(k, None)
        id_keys_to_remove = {'lab_id', 'owner', 'short_name', 'datetime'}
        for k in id_keys_to_remove:
            complete_entry_dict.get('electrode_recipe_id', {}).pop(k, None)
        self.entry_dict_hash = hash(self._normalize_object(complete_entry_dict))

    def normalize(self, archive, logger):
        self.chemical_composition_or_formulas = self.electrode_recipe_id.element
        super().normalize(archive, logger)
        export_lab_id(archive, self.lab_id)
        self.set_entry_dict_hash()


class CENECCElectrodeID(ReadableIdentifiersCustom):
    m_def = Section(
        a_eln=dict(
            hide=['sample_owner', 'sample_short_name', 'sample_id', 'short_name']
        )
    )

    institute = Quantity(
        type=str,
        description='Alias/short name of the home institute of the owner, i.e. *HZB*.',
        default='CE-NECC',
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=['CE-NECC'])),
    )

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
                ]
            ),
        ),
    )

    recipe = Quantity(
        type=Reference(CENECCElectrodeRecipe.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
    )

    def normalize(self, archive, logger):
        author = archive.metadata.main_author
        if author and self.owner is None:
            self.owner = ' '.join([author.first_name, author.last_name])

        super().normalize(archive, logger)

        if archive.data.lab_id:
            return
        if not self.datetime:
            from datetime import date

            self.datetime = date.today()

        if self.institute and self.owner and self.datetime:
            id_base = [
                build_initial_id(self.institute, self.owner, self.datetime),
                self.recipe.lab_id,
            ]
            self.lab_id = '_'.join(id_base)
        create_id(archive, self.lab_id)


class CENECCElectrode(SearchableCESample):
    electrode_id = SubSection(section_def=CENECCElectrodeID)

    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln={'component': 'RichTextEditQuantity', 'label': 'Remarks'},
    )

    measured_mass_loading = Quantity(
        type=np.dtype(np.float64),
        unit='mg/cm^2',
        description='Should correspond to the mass loading specified in the recipe. '
        'The actual mass loading of the electrode is specified here.',
        a_eln={'component': 'NumberEditQuantity'},
        a_display={'unit': 'mg/cm^2'},
    )

    bottle_number = Quantity(
        type=str,
        description='This number can be found on the bottle used during the '
        'manufacture of the electrode in the laboratory.',
        a_eln={'component': 'StringEditQuantity'},
    )

    def set_entry_dict_hash(self):
        from nomad.utils import hash

        complete_entry_dict = self.m_to_dict()
        basic_dict = {
            'owner': complete_entry_dict.get('electrode_id', {}).get('owner'),
            'institute': complete_entry_dict.get('electrode_id', {}).get('institute'),
            'date': complete_entry_dict.get('electrode_id', {}).get('datetime'),
            'recipe': complete_entry_dict.get('electrode_id', {}).get('recipe'),
            'mass_loading': complete_entry_dict.get('measured_mass_loading'),
            'bottle': complete_entry_dict.get('bottle_number'),
        }
        self.entry_dict_hash = hash(self._normalize_object(basic_dict))

    def normalize(self, archive, logger):
        self.chemical_composition_or_formulas = (
            self.electrode_id.recipe.electrode_recipe_id.element
        )
        super().normalize(archive, logger)
        export_lab_id(archive, self.lab_id)
        if archive.data == self and self.name:
            archive.metadata.entry_name = self.name
        self.set_entry_dict_hash()
