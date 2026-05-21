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

import re

# All dictionary keys are matched case-insensitively by NamingNormalizer, which
# lowercases them at construction time.  Write keys in lowercase in the source
# dict to make duplicate detection obvious and avoid silent collisions.

# ════════════════════════════════════════════════════════════════
# LAYER TYPE  (canonical names from LayerProperties.layer_type enum)
# ════════════════════════════════════════════════════════════════

layer_type_aliases = {
    # Electron Transport Layer
    'electrode': 'Electron Transport Layer',
    'etl': 'Electron Transport Layer',
    'electron transport layer': 'Electron Transport Layer',
    'electrontransportlayer': 'Electron Transport Layer',
    # Absorber
    'absorber': 'Absorber',
    'absorber layer': 'Absorber',
    'perovskite': 'Absorber',
    # Buffer Layer
    'buffer': 'Buffer',
    'buffer layer': 'Buffer',
    'blockinglayer': 'Buffer',
    # Passivation
    'passivation': 'Passivation',
    'passivation layer': 'Passivation',
    'passivation_layer': 'Passivation',
    # Hole Transport Layer
    'hole transport': 'Hole Transport Layer',
    'hole transport layer': 'Hole Transport Layer',
    'htl': 'Hole Transport Layer',
    # Electron Transport Layer (short form)
    'electron transport': 'Electron Transport Layer',
}

"""
What do we do with Contact, Back Contact, Top Contact, Top Electrode ? 
    # A.R.C.
    'anti reflective coating': 'A.R.C.',
    'anti-reflective coating': 'A.R.C.',
    'arc': 'A.R.C.',
    # Back Contact
    'back contact': 'Back Contact',
    'metal contact': 'Back Contact',
    'top contact': 'Back Contact',
    'top electrode': 'Back Contact',
    'top_electrode': 'Back Contact',
    'topcontact': 'Back Contact',

    # Substrate Conductive Layer
    'substrate conductive layer': 'Substrate Conductive Layer',
    'tco': 'Substrate Conductive Layer',
"""

# ════════════════════════════════════════════════════════════════
# LAYER MATERIAL NAME  (chemical abbreviations / common names)
# ════════════════════════════════════════════════════════════════

layer_material_name_aliases = {
    # Metals
    'silver': 'Ag',
    'copper': 'Cu',
    'cu': 'Cu',                     # upper-case "CU" → standard "Cu"
    # Lithium fluoride
    'lif': 'LiF',                   # upper-case "LIF" → "LiF"
    # Fullerenes
    'buckminsterfullerene': 'C60',
    # BCP (Bathocuproine)
    'bathocuproine': 'BCP',
    '2,9-dimethyl-4,7-diphenyl-1,10-phenanthroline': 'BCP',
    # HTL materials
    'ptaa': 'PTAA',
    'poly[bis(4-phenyl)(2,4,6-trimethylphenyl)amine': 'PTAA',
    'spiro-ometad': 'Spiro-OMeTAD',
    "2,2',7,7'-tetrakis(n,n-di-p-methoxyphenylamine)"
    "-9,9'-spirobifluorene": 'Spiro-OMeTAD',
    'p3ht': 'P3HT',
    'poly(3-hexylthiophene-2,5-diyl)': 'P3HT',
    # ETL materials
    'pcbm': 'PCBM',
    '[6,6]-phenyl-c61-butyric acid methyl ester': 'PCBM',
    # Passivation materials
    'peai': 'PEAI',
    'phenethylammonium iodide': 'PEAI',
}

"""
    # Trailing-punctuation / typo corrections
    'edai2?': 'EDAI2',
    'guai?': 'GUAI',
"""

# ════════════════════════════════════════════════════════════════
# SOLVENTS
# ════════════════════════════════════════════════════════════════

solvent_aliases = {
    # Dimethyl sulfoxide  (DMSO / dimethylsulfoxide)
    'dmso': 'Dimethylsulfoxide',
    'dimethylsulfoxide': 'Dimethylsulfoxide',
    # Ethanol  (EtOH / ETOH / EtoH all lowercase to "etoh")
    'etoh': 'Ethanol',
    'etoh (dry)': 'Ethanol',
    'ethanol': 'Ethanol',
    'ethonal': 'Ethanol',           # typo
    'absolute ethanol': 'Ethanol',
    'anhydrous ethanol': 'Ethanol',
    # Isopropanol  (IPA / iso-propanol / Iso-proponal)
    'ipa': 'Isopropanol',
    'iso-propanol': 'Isopropanol',
    'iso-proponal': 'Isopropanol',  # typo
    'isopropanol': 'Isopropanol',
    # Chlorobenzene  (CB / cb)
    'cb': 'Chlorobenzene',
    'chlorobenzene': 'Chlorobenzene',
    # Dimethylformamide  (DMF / dmf)
    'dmf': 'DMF',
    'dimethylformamide': 'DMF',
    # Acetonitrile  (ACN)
    'acn': 'Acetonitrile',
    'acetonitrile': 'Acetonitrile',
    # Water
    'h2o': 'Water',
    # DI Water  (DI water / DI WATER / DI-water / Diwater)
    'di water': 'DI Water',
    'di-water': 'DI Water',
    'diwater': 'DI Water',
    # 2-MeTHF  (2MeTHF)
    '2methf': '2-MeTHF',
}

# ════════════════════════════════════════════════════════════════
# SOLUTES
# ════════════════════════════════════════════════════════════════

solute_aliases = {
    # Methylammonium chloride  (MaCl / Macl → MACl)
    'macl': 'MACl',
    # Methylammonium iodide  (MAI)
    'mai': 'MAI',
    'methylammonium iodide': 'MAI',
    # Formamidinium iodide  (FAI)
    'fai': 'FAI',
    'formamidinium iodide': 'FAI',
}

additive_aliases = {
    # tBP  (4-tert-butylpyridine)
    'tbp': 'tBP',
    '4-tert-butylpyridine': 'tBP',
    # Li-TFSI  (Bis(trifluoromethane)sulfonimide lithium salt)
    'li-tfsi': 'Li-TFSI',
    'bis(trifluoromethane)sulfonimide lithium salt': 'Li-TFSI',
}

# ════════════════════════════════════════════════════════════════
# ATMOSPHERE  (annealing / process atmosphere)
# ════════════════════════════════════════════════════════════════

atmosphere_aliases = {
    # Air / ambient
    'air': 'Air',
    'ambient': 'Air',
    'atmosphere': 'Air',
    # Dry air kept distinct from ordinary air
    'dry air': 'Dry Air',
    # Nitrogen  (N2)
    'n2': 'Nitrogen',
    # Glovebox  (GB)
    'gb': 'Glovebox',
    'glovebox': 'Glovebox',
    # Fume hood
    'fume hood': 'Fume Hood',
}

# ════════════════════════════════════════════════════════════════
# ANTI-SOLVENTS
# ════════════════════════════════════════════════════════════════

anti_solvent_aliases = {
    # Anisole  (Anisol / Ansiole)
    'anisol': 'Anisole',
    'ansiole': 'Anisole',
    'anisole': 'Anisole',
    # Chlorobenzene  (CB)
    'cb': 'Chlorobenzene',
    # Ethyl Acetate  (EA / ethylacetate)
    'ea': 'Ethyl Acetate',
    'ethyl acetate': 'Ethyl Acetate',
    'ethylacetate': 'Ethyl Acetate',
    # Methyl Acetate  (methylacetate)
    'methyl acetate': 'Methyl Acetate',
    'methylacetate': 'Methyl Acetate',
}

# ════════════════════════════════════════════════════════════════
# SUBSTRATE TYPE
# ════════════════════════════════════════════════════════════════

substrate_aliases = {
    # Glass
    'glass': 'Glass',
    'glass-ar': 'AR Glass',
    # Soda Lime Glass  (SLG)
    'slg': 'Soda Lime Glass',
    'soda lime glass': 'Soda Lime Glass',
    # Other
    'si_bottom_cell': 'Si Bottom Cell',
    # PET  (Polyethylene terephthalate)
    'pet': 'PET',
    'polyethylene terephthalate': 'PET',
}

# ════════════════════════════════════════════════════════════════
# CONDUCTING / TCO MATERIAL  (substrate electrode layer)
# ════════════════════════════════════════════════════════════════

conducting_material_aliases = {
    # Plain ITO  (ito / ITO (Full) / ITO (patterned))
    'ito': 'ITO',
    'ito (full)': 'ITO (full)',
    'ito (patterned)': 'ITO (patterned)',
    # AR-ITO variants  (AR ITO / ARC_ITO / ITO-AR / ITO_ARC)
    'ar ito': 'AR-ITO',
    'arc_ito': 'AR-ITO',
    'ito-ar': 'AR-ITO',
    'ito_arc': 'AR-ITO',
    # Purple ITO
    'purple ito': 'Purple ITO',
    'ito-purple': 'Purple ITO',
    # Quartz  (appears in conducting_material column)
    'quartz': 'Quartz',
    # Full names
    'indium tin oxide': 'ITO',
}

# ════════════════════════════════════════════════════════════════
# EVAPORATION CHAMBER / LOCATION
# ════════════════════════════════════════════════════════════════

# evaporation_location_aliases = {
#     # CSMB
#     'csmb/ evap': 'CSMB/Evap',
#     # HySprint Evap  (HyEvap / Hysprint Evap)
#     'hyevap': 'HySprint Evap',
#     'hysprint evap': 'HySprint Evap',
#     # HyVap  (hyvap / Hyvap / HYVAP / HyVap → all lowercase "hyvap")
#     'hyvap': 'HyVap',
#     # HyVap Box  (HyVapBox / HZB-HyVap-Box)
#     'hyvapbox': 'HyVap Box',
#     'hzb-hyvap-box': 'HyVap Box',
#     # IRIS  (Iris Evap / IRIS Evap)
#     'iris': 'IRIS',
#     'iris evap': 'IRIS',
#     # IRIS Pero5 Evaporation
#     'iris hzbgloveboxes pero5evaporation': 'IRIS Pero5 Evaporation',
#     'iris-pero5 evaporation': 'IRIS Pero5 Evaporation',
#     # Pero5 Evaporation  (with / without GB suffix)
#     'pero5 evaporation gb': 'Pero5 Evaporation',
#     # ProtoVap
#     'protovap': 'ProtoVap',
# }

evaporation_location_aliases = {}  # populate once equipment names are finalised


class NamingNormalizer:
    def __init__(self, normalization_dict: dict, regex_rules: list = None):
        """
        Args:
            normalization_dict: dict mapping alias strings to their canonical names.
                Keys are matched case-insensitively (spaces are preserved for matching).
            regex_rules: optional list of ``(pattern, canonical_name)`` tuples used
                as full-match fallbacks when no exact alias is found.  Patterns are
                compiled case-insensitively.  Useful for Excel serial increments::

                    [(r'N\\d+', 'Nitrogen'), (r'C6[1-9]|C7[0-5]', 'C60')]
        """
        self.normalization_dict = {k.lower(): v for k, v in normalization_dict.items()}
        self.regex_rules = [
            (re.compile(p, re.IGNORECASE), v) for p, v in (regex_rules or [])
        ]

    def normalize(self, input_value: str):
        """Return the canonical name for input_value, or input_value unchanged if not
        found.

        Lookup order:
        1. Exact case-insensitive dict match.
        2. Full-match against each regex rule in order.
        3. Return input_value unchanged.

        Args:
            input_value: The raw string to normalise.

        Returns:
            The canonical name when a match is found, otherwise the original value.
            Returns None when input_value is None.
        """
        if input_value is None:
            return None
        key = input_value.strip().lower()
        if key in self.normalization_dict:
            return self.normalization_dict[key]
        for pattern, canonical in self.regex_rules:
            if pattern.fullmatch(input_value.strip()):
                return canonical
        return input_value


layer_type_normalizer = NamingNormalizer(layer_type_aliases)
layer_material_name_normalizer = NamingNormalizer(
    layer_material_name_aliases,
    regex_rules=[
        (r'C6[1-9]|C7[0-5]', 'C60'),  # Excel-serialised C61-C75
    ],
)
solvent_normalizer = NamingNormalizer(solvent_aliases)
solute_normalizer = NamingNormalizer(solute_aliases)
additive_normalizer = NamingNormalizer(additive_aliases)
atmosphere_normalizer = NamingNormalizer(
    atmosphere_aliases,
    regex_rules=[
        (r'N\d+', 'Nitrogen'),  # Excel-serialised N3, N4 … N13
    ],
)
anti_solvent_normalizer = NamingNormalizer(anti_solvent_aliases)
substrate_normalizer = NamingNormalizer(substrate_aliases)
conducting_material_normalizer = NamingNormalizer(conducting_material_aliases)
evaporation_location_normalizer = NamingNormalizer(evaporation_location_aliases)