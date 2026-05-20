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

layer_type_aliases = {
    'electrode': 'Electron Transport Layer',
    'electron transport layer': 'Electron Transport Layer',
    'electrontransportlayer': 'Electron Transport Layer',
    'etl': 'Electron Transport Layer',
    'absorber': 'Absorber',
    'Absorber Layer': 'Absorber',
    'Back contact': 'Back Contact',
    'Buffer': 'Buffer Layer',
    'buffer': 'Buffer Layer',
    'buffer layer': 'Buffer Layer',
    'contact': 'Contact',

}

layer_material_name = {}

solvent_aliases = {
    'DMSO':'Dimethylsulfoxide',
    'dimethylsulfoxide': 'Dimethylsulfoxide',
    'EtOH': 'Ethanol',
    'ethanol': 'Ethanol',
    'Ethonal': 'Ethanol',
    'ETOH': 'Ethanol',
    'EtoH': 'Ethanol',
}

solute = {}
additive = {}



class NamingNormalizer:
    def __init__(self, normalization_dict: dict):
        """
        Args:
            normalization_dict: dict mapping alias strings to their canonical names.
                Keys are matched case-insensitively (spaces are preserved for matching).
        """
        self.normalization_dict = {k.lower(): v for k, v in normalization_dict.items()}

    def normalize(self, input_value: str):
        """Return the canonical name for input_value, or input_value unchanged if not found.

        Args:
            input_value: The raw string to normalise.

        Returns:
            The canonical name when a match is found, otherwise the original value.
            Returns None when input_value is None.
        """
        if input_value is None:
            return None
        key = input_value.strip().lower()
        return self.normalization_dict.get(key, input_value)


layer_type_normalizer = NamingNormalizer(layer_type_aliases)
solvent_normalizer = NamingNormalizer(solvent_aliases)