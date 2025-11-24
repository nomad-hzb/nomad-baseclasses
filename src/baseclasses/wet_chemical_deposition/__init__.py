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

from .blade_coating import BladeCoating
from .crystallization import Crystallization
from .dip_coating import DipCoating
from .dropcast import DropCasting
from .gravure_printing import GravurePrinting
from .inkjet_printing import InkjetPrinting, LP50InkjetPrinting
from .screen_printing import ScreenPrinting
from .slot_die_coating import SlotDieCoating
from .spin_coating import SpinCoating, SpinCoatingRecipe
from .spray_pyrolysis import SprayPyrolysis
from .vaporization_and_dropcasting import VaporizationAndDropCasting
from .wet_chemical_deposition import PrecursorSolution, WetChemicalDeposition
