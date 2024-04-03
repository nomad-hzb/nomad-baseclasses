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

from .cleaning import Cleaning, SolutionCleaning
from .constantpotential import ConstantPotential
from .cyclicvoltammetry import CyclicVoltammetry, CVProperties
from .linear_sweep_voltammetry import LinearSweepVoltammetry, LSVProperties
from .chronoamperometry import Chronoamperometry
from .chronopotentiometry import Chronopotentiometry
from .chronocoulometry import Chronocoulometry
from .opencircuitvoltage import OpenCircuitVoltage, OCVProperties
from .electorchemical_impedance_spectroscopy import ElectrochemicalImpedanceSpectroscopy, EISProperties
from .opticalmicroscopy import OpticalMicorscopy
from .photocurrent import PhotoCurrent
from .cesample import CESample, SampleIDCENOME, SubstrateProperties, Purging, export_lab_id
from .cesample import CENSLISample, get_next_project_sample_number, SubstanceWithConcentration
from .cesample import CENOMESample, Electrode, Electrolyte, ElectroChemicalCell, ElectroChemicalSetup, Environment, Equipment, CatalystSynthesis
from .preparation_protocoll import PreparationProtocol
from .diamondsample import DiamondSample
# from .waterbath import WaterBath
from .voltammetry import VoltammetryCycle, Voltammetry, VoltammetryCycleWithPlot
from .potentiostat_measurement import PotentiostatMeasurement, PotentiostatSetup
from .phasefluorometryoxygen import PhaseFluorometryOxygen
from .pumpratemeasurement import PumpRateMeasurement
from .uvvis import UVvisDataConcentration, UVvisMeasurementConcentration, UVvisConcentrationDetection
