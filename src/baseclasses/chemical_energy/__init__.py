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

from .cesample import (
    CatalystSynthesis,
    CENOMESample,
    CENSLISample,
    CESample,
    ElectroChemicalCell,
    ElectroChemicalSetup,
    Electrode,
    Electrolyte,
    Environment,
    Equipment,
    ExpectedStructure,
    Purging,
    ReferenceElectrode,
    SampleIDCENESD,
    SampleIDCENOME,
    SubstanceWithConcentration,
    SubstrateProperties,
    export_lab_id,
    get_next_project_sample_number,
)
from .chronoamperometry import Chronoamperometry
from .chronocoulometry import Chronocoulometry
from .chronopotentiometry import Chronopotentiometry
from .cleaning import Cleaning, SolutionCleaning
from .constantpotential import ConstantPotential
from .cyclicvoltammetry import CVProperties, CyclicVoltammetry
from .diamondsample import DiamondSample
from .electrochemical_impedance_spectroscopy import (
    EISProperties,
    EISPropertiesWithData,
    ElectrochemicalImpedanceSpectroscopy,
    ElectrochemicalImpedanceSpectroscopyMultiple,
)
from .electrolyser_performance import (
    ElectrolyserPerformanceEvaluation,
    ElectrolyserProperties,
    NESDElectrode,
)
from .galvanodynamic_sweep import GalvanodynamicSweep, LSGProperties
from .general_process import GeneralProcess
from .linear_sweep_voltammetry import LinearSweepVoltammetry, LSVProperties
from .massspectrometry import (
    Massspectrometry,
    MassspectrometrySettings,
    MassspectrometrySpectrum,
)
from .neccelectrode import CENECCElectrode, CENECCElectrodeID, CENECCElectrodeRecipe
from .nome_cp_analysis import CPAnalysis
from .opencircuitvoltage import OCVProperties, OpenCircuitVoltage
from .opticalmicroscopy import OpticalMicorscopy
from .phasefluorometryoxygen import PhaseFluorometryOxygen
from .photocurrent import PhotoCurrent
from .potentiometry_gaschromatography import (
    GasChromatographyMeasurement,
    GasFEResults,
    NECCExperimentalProperties,
    NECCFeedGas,
    NECCPotentiostatMeasurement,
    PotentiometryGasChromatographyMeasurement,
    PotentiometryGasChromatographyResults,
    ThermocoupleMeasurement,
)
from .potentiostat_measurement import PotentiostatMeasurement, PotentiostatSetup
from .preparation_protocoll import PreparationProtocol
from .pumpratemeasurement import PumpRateMeasurement
from .uvvismeasurementconcentration import UVvisDataConcentration

# from .waterbath import WaterBath
from .voltammetry import Voltammetry, VoltammetryCycle, VoltammetryCycleWithPlot
