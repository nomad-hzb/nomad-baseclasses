from datetime import datetime

import pandas as pd
from nomad.datamodel.metainfo.basesections import CompositeSystemReference
from nomad.units import ureg

from baseclasses import LayerProperties, PubChemPureSubstanceSectionCustom
from baseclasses.atmosphere import Atmosphere, GloveboxAtmosphere
from baseclasses.material_processes_misc import (
    AirKnifeGasQuenching,
    Annealing,
    AntiSolventQuenching,
    CoronaCleaning,
    GasFlowAssistedVacuumDrying,
    GasQuenchingWithNozzle,
    LaminationSettings,
    PlasmaCleaning,
    SolutionCleaning,
    UVCleaning,
    VacuumQuenching,
)
from baseclasses.material_processes_misc.annealing import IRAnnealing
from baseclasses.material_processes_misc.laser_scribing import LaserScribingProperties
from baseclasses.product_info import ProductInfo
from baseclasses.solar_energy.carbonpaste import CarbonPasteLayerProperties
from baseclasses.solution import Solution, SolutionChemical, SolutionWaschingFiltration
from baseclasses.vapour_based_deposition.atomic_layer_deposition import (
    ALDMaterial,
    ALDPropertiesIris,
)
from baseclasses.vapour_based_deposition.close_space_sublimation import CSSProcess
from baseclasses.vapour_based_deposition.evaporation import (
    InorganicEvaporation,
    OrganicEvaporation,
    PerovskiteEvaporation,
)
from baseclasses.vapour_based_deposition.sputtering import SputteringProcess
from baseclasses.wet_chemical_deposition import PrecursorSolution
from baseclasses.wet_chemical_deposition.blade_coating import BladeCoatingProperties
from baseclasses.wet_chemical_deposition.dip_coating import DipCoatingProperties
from baseclasses.wet_chemical_deposition.gravure_printing import (
    GravurePrintingProperties,
)
from baseclasses.wet_chemical_deposition.inkjet_printing import (
    InkjetPrintingProperties,
    LP50NozzleVoltageProfile,
    NotionNozzleVoltageProfile,
    NozzleVoltageProfile,
    PrintHeadPath,
    PrintHeadProperties,
)
from baseclasses.wet_chemical_deposition.screen_printing import (
    MeshProperties,
    ScreenPrintingProperties,
)
from baseclasses.wet_chemical_deposition.slot_die_coating import (
    SlotDieCoatingProperties,
)
from baseclasses.wet_chemical_deposition.spin_coating import SpinCoatingRecipeSteps


def create_product_info(data, prefix):
    """
    Create a ProductInfo object with data for a specific chemical prefix.

    Args:
        data: pandas Series containing the experimental data
        prefix: Chemical prefix (e.g., 'Solvent 1', 'Solute 2', 'Additive 1')

    Returns:
        ProductInfo object with populated fields
    """
    return ProductInfo(
        product_number=get_value(data, f'{prefix} Product Number', None, False),
        lot_number=get_value(data, f'{prefix} Lot Number', None, False),
        product_volume=get_value(
            data, f'{prefix} Delivered Product Volume [ml]', None, unit='ml'
        ),
        product_weight=get_value(
            data, f'{prefix} Delivered Product Weight [g]', None, unit='g'
        ),
        shipping_date=get_datetime(data, f'{prefix} Shipping Date'),
        opening_date=get_datetime(data, f'{prefix} Opening Date'),
        supplier=get_value(data, f'{prefix} Supplier', None, False),
        product_description=get_value(
            data, f'{prefix} Product Description', None, False
        ),
        cost=get_value(data, f'{prefix} Cost [EUR]', None, True),
    )


def get_entry_id_from_file_name(file_name, upload_id):
    from nomad.utils import hash

    return hash(upload_id, file_name)


def get_reference(upload_id, file_name):
    entry_id = get_entry_id_from_file_name(file_name, upload_id)
    return f'../uploads/{upload_id}/archive/{entry_id}#data'


def get_value(data, key, default=None, number=True, unit=None, factor=1.0):
    if not isinstance(key, list):
        key = [key]
    if unit and not isinstance(unit, list):
        unit = [unit]
    if factor and not isinstance(factor, list):
        factor = [factor] * len(key)

    try:
        if not unit:
            for k, f in zip(key, factor):
                if k not in data:
                    continue
                if pd.isna(data[k]):
                    return default
                if number:
                    return float(data[k]) * f
                return str(data[k]).strip()
        if unit:
            for k, u, f in zip(key, unit, factor):
                if k not in data:
                    continue
                if pd.isna(data[k]):
                    return default
                if number and u:
                    Q_ = ureg.Quantity
                    return Q_(float(data[k]) * f, ureg(u))
        return default
    except Exception as e:
        raise e


def get_datetime(data, key):
    """
    Parse datetime from data using multiple date formats.

    Args:
        data: Dictionary containing the date value
        key: Key to access the date value in data

    Returns:
        str: Formatted datetime string in NOMAD format ('%Y-%m-%d %H:%M:%S.%f')
        None: If key is missing, value is NaN, or parsing fails
    """
    import pandas as pd

    if key not in data or pd.isna(data[key]):
        return None

    date_value = str(data[key]).strip()

    # List of supported date formats to try (with and without time)
    date_formats = [
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%d.%m.%Y',
        '%Y-%m-%d',  # ISO date
        '%d-%m-%y',
        '%d/%m/%y',
        '%Y-%m-%d %H:%M:%S',  # ISO with time
        '%Y-%m-%d %H:%M:%S.%f',
        '%d-%m-%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%d.%m.%Y %H:%M:%S',
    ]

    for date_format in date_formats:
        try:
            dt = datetime.strptime(date_value, date_format)
            return dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            continue

    # Try pandas as a fallback (handles many formats)
    try:
        dt = pd.to_datetime(date_value)
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')
    except Exception:
        pass

    print(
        f"Warning: Could not parse date '{date_value}' with key '{key}'. Tried formats: {date_formats}"
    )
    return None


def map_basic_sample(data, substrate_name, upload_id, sample_class):
    archive = sample_class(
        datetime=get_datetime(data, 'Date'),
        name=data['Nomad ID'],
        lab_id=data['Nomad ID'],
        substrate=get_reference(upload_id, substrate_name) if substrate_name else None,
        description=get_value(data, 'Variation', None, False),
        number_of_junctions=get_value(data, 'Number of junctions', None),
    )
    return (data['Nomad ID'], archive)


def map_batch(batch_ids, batch_id, upload_id, batch_class):
    archive = batch_class(
        name=batch_id,
        lab_id=batch_id,
        entities=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in batch_ids
        ],
    )
    return (batch_id, archive)


def map_annealing(data):
    annealing = Annealing()
    if get_value(data, 'IR annealing power [W]', None, unit='W') is not None:
        annealing = IRAnnealing(
            power=get_value(data, 'IR annealing power [W]', None, unit='W'),
            distance=get_value(data, 'IR annealing distance [mm]', None, unit='mm'),
        )
    annealing.temperature = get_value(
        data, 'Annealing temperature [°C]', None, unit='°C'
    )
    annealing.time = get_value(data, 'Annealing time [min]', None, unit='minute')
    annealing.atmosphere = get_value(
        data, ['Annealing athmosphere', 'Annealing atmosphere'], None, False
    )
    annealing.datetime = (get_datetime(data, 'Datetime'),)
    return annealing


def map_atmosphere(data):
    atmosphere = Atmosphere()
    if  get_value(data, 'GB oxygen level [ppm]', None) is not None:
        atmosphere = GloveboxAtmosphere(
            oxygen_level_ppm = get_value(data, 'GB oxygen level [ppm]', None)
        )
    atmosphere.relative_humidity = get_value(
        data, ['rel. humidity [%]', 'Room/GB humidity [%]'], None
        )
    atmosphere.temperature =  get_value(
        data, 'Room temperature [°C]', None, unit='°C'
        )

    # # Check if we have any atmosphere-related data
    # gb_oxygen = get_value(data, 'GB oxygen level [ppm]', None)
    # humidity = get_value(data, ['rel. humidity [%]', 'Room/GB humidity [%]'], None)
    # temperature = get_value(data, 'Room temperature [°C]', None, unit='°C')
    
    # # If no atmosphere data exists, return None
    # if all(val is None for val in [gb_oxygen, humidity, temperature]):
    #     return None
    
    # # Create appropriate atmosphere type based on available data
    # if gb_oxygen is not None:
    #     # Glovebox atmosphere - only has oxygen level and temperature
    #     atmosphere = GloveboxAtmosphere(
    #         oxygen_level_ppm=gb_oxygen,
    #         temperature=temperature,
    #     )
    # else:
    #     # Regular atmosphere - can have humidity, temperature
    #     atmosphere = Atmosphere(
    #         relative_humidity=humidity,
    #         temperature=temperature,
    #     )
    
    return atmosphere


def map_layer(data):
    # Common properties for all layer types
    common_layer_props = {
        'layer_type': get_value(data, 'Layer type', None, False),
        'layer_material_name': get_value(data, 'Material name', None, False),
        'layer_thickness': get_value(data, 'Layer thickness [nm]', None, unit='nm'),
        'layer_chemical_id': get_value(data, 'Layer chemical ID', None, False),
        'product_info': create_product_info(data, 'Layer'),
    }

    # Guard clause: handle Carbon Paste Layer early
    if 'Carbon Paste Layer' in get_value(data, 'Layer type', '', False):
        return [
            CarbonPasteLayerProperties(
                **common_layer_props,
                drying_time=get_value(data, 'Drying Time [s]', None, unit='s'),
            )
        ]

    # Default case: regular LayerProperties
    return [
        LayerProperties(
            **common_layer_props,
            layer_transmission=get_value(data, 'Transmission [%]', None, True),
            layer_morphology=get_value(data, 'Morphology', None, False),
            layer_sheet_resistance=get_value(
                data, 'Sheet Resistance [Ohms/square]', None, True
            ),
        )
    ]


def map_solutions(data):
    filtration = None

    if get_value(data, 'Filter Material', None, False):
        filtration = SolutionWaschingFiltration(
            washing_technique='Filtration',
            filter_material=get_value(data, 'Filter Material', None, False),
            filter_pore_size=get_value(data, 'Filter Pore Size [um]', None, unit='um'),
        )

    solvents = []
    solutes = []
    additives = []
    for col in data.index:
        if col.lower().startswith('solvent'):
            solvents.append(' '.join(col.split(' ')[:2]))
        if col.lower().startswith('solute'):
            solutes.append(' '.join(col.split(' ')[:2]))
        if col.lower().startswith('additive'):
            additives.append(' '.join(col.split(' ')[:2]))

    final_solvents = []
    final_solutes = []
    final_additives = []

    for solvent in sorted(set(solvents)):
        final_solvents.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'{solvent} name', None, False),
                    load_data=False,
                    product_info=create_product_info(data, solvent),
                ),
                chemical_volume=get_value(
                    data, f'{solvent} volume [uL]', None, unit='uL'
                ),
                amount_relative=get_value(data, f'{solvent} relative amount', None),
                chemical_id=get_value(data, f'{solvent} chemical ID', None, False),
            ),
        )
    for solute in sorted(set(solutes)):
        final_solutes.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(
                        data, [f'{solute} type', f'{solute} name'], None, False
                    ),
                    load_data=False,
                    product_info=create_product_info(data, solute),
                ),
                concentration_mol=get_value(
                    data, f'{solute} Concentration [mM]', None, unit='mM'
                ),
                concentration_mass=get_value(
                    data,
                    [
                        f'{solute} Concentration [wt%]',
                        f'{solute} Concentration [mg/ml]',
                    ],
                    None,
                    unit=['mg/ml', 'mg/ml'],
                    factor=[10, 1],
                ),
                amount_relative=get_value(data, f'{solute} relative amount', None),
                chemical_id=get_value(data, f'{solute} chemical ID', None, False),
            ),
        )
    for additive in sorted(set(additives)):
        final_additives.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, [f'{additive} name'], None, False),
                    load_data=False,
                    product_info=create_product_info(data, additive),
                ),
                concentration_mol=get_value(
                    data, f'{additive} Concentration [mM]', None, unit='mM'
                ),
                concentration_mass=get_value(
                    data,
                    [
                        f'{additive} Concentration [wt%]',
                        f'{additive} Concentration [mg/ml]',
                    ],
                    None,
                    unit=['mg/ml', 'mg/ml'],
                    factor=[10, 1],
                ),
                amount_relative=get_value(data, f'{additive} relative amount', None),
                chemical_id=get_value(data, f'{additive} chemical ID', None, False),
            )
        )

    archive = Solution(
        solvent=final_solvents,
        solute=final_solutes,
        additive=final_additives,
        filtration=filtration,
    )

    return archive


def map_anti_solvent_quenching(data):
    """Map anti-solvent quenching data to AntiSolventQuenching object."""
    if not get_value(data, 'Anti solvent name', None, False):
        return None

    return AntiSolventQuenching(
        anti_solvent_volume=get_value(
            data, 'Anti solvent volume [ml]', None, unit='mL'
        ),
        anti_solvent_dropping_time=get_value(
            data, 'Anti solvent dropping time [s]', None, unit='s'
        ),
        anti_solvent_dropping_height=get_value(
            data, 'Anti solvent dropping heigt [mm]', None, unit='mm'
        ),
        anti_solvent_dropping_flow_rate=get_value(
            data,
            [
                'Anti solvent dropping speed [ul/s]',
                'Anti solvent dropping speed [uL/s]',
            ],
            None,
            unit=['uL/s', 'uL/s'],
        ),
        anti_solvent_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Anti solvent name', None, False), load_data=False
        ),
    )


def map_vacuum_quenching(data):
    """Map vacuum quenching data to VacuumQuenching object."""
    if not get_value(data, 'Vacuum quenching duration [s]', None, unit='s'):
        return None

    return VacuumQuenching(
        start_time=get_value(data, 'Vacuum quenching start time [s]', None, unit='s'),
        duration=get_value(data, 'Vacuum quenching duration [s]', None, unit='s'),
        pressure=get_value(data, 'Vacuum quenching pressure [bar]', None, unit='bar'),
    )


def map_gas_quenching_with_nozzle(data):
    """Map gas quenching with nozzle data to GasQuenchingWithNozzle object."""
    if not get_value(data, 'Gas', None, False):
        return None

    return GasQuenchingWithNozzle(
        starting_delay=get_value(data, 'Gas quenching start time [s]', None, unit='s'),
        flow_rate=get_value(data, 'Gas quenching flow rate [ml/s]', None, unit='ml/s'),
        height=get_value(data, 'Gas quenching height [mm]', None, unit='mm'),
        duration=get_value(data, 'Gas quenching duration [s]', None, unit='s'),
        pressure=get_value(data, 'Gas quenching pressure [bar]', None, unit='bar'),
        velocity=get_value(data, 'Gas quenching velocity [m/s]', None, unit='m/s'),
        nozzle_shape=get_value(data, 'Nozzle shape', None, False),
        nozzle_size=get_value(data, 'Nozzle size [mm²]', None, False),
        gas=get_value(data, 'Gas', None, False),
    )


def map_air_knife_gas_quenching(data):
    """Map air knife gas quenching data to AirKnifeGasQuenching object."""
    if not get_value(data, 'Air knife angle [°]', None, unit='°'):
        return None

    return AirKnifeGasQuenching(
        air_knife_angle=get_value(data, 'Air knife angle [°]', None, unit='°'),
        bead_volume=get_value(data, 'Bead volume [mm/s]', None, unit='mm/s'),
        drying_speed=get_value(data, 'Drying speed [cm/min]', None, unit='cm/minute'),
        air_knife_distance_to_thin_film=get_value(
            data, 'Air knife gap [cm]', None, unit='cm'
        ),
        drying_gas_temperature=get_value(
            data,
            ['Drying gas temperature [°]', 'Drying gas temperature [°C]'],
            None,
            unit=['°C', '°C'],
        ),
        heat_transfer_coefficient=get_value(
            data,
            'Heat transfer coefficient [W m^-2 K^-1]',
            None,
            unit='W/(K*m**2)',
        ),
    )


def map_gas_flow_assisted_vacuum_drying(data):
    """Map GAVD data to GasFlowAssistedVacuumDrying object."""
    if (
        not get_value(data, 'GAVD Gas', None, False)
        and not get_value(data, 'GAVD start time [s]', None, unit='s')
        and not get_value(data, 'Nozzle type', None, False)
    ):
        return None

    return GasFlowAssistedVacuumDrying(
        vacuum_properties=VacuumQuenching(
            start_time=get_value(data, 'GAVD start time [s]', None, unit='s'),
            pressure=get_value(data, 'GAVD vacuum pressure [mbar]', None, unit='mbar'),
            temperature=get_value(data, 'GAVD temperature [°C]', None, unit='°C'),
            duration=get_value(data, 'GAVD vacuum time [s]', None, unit='s'),
        ),
        gas_quenching_properties=GasQuenchingWithNozzle(
            duration=get_value(data, 'Gas flow duration [s]', None, unit='s'),
            pressure=get_value(
                data,
                ['Gas flow pressure [bar]', 'Gas flow pressure [mbar]'],
                None,
                unit=['bar', 'mbar'],
            ),
            nozzle_shape=get_value(data, 'Nozzle shape', None, False),
            nozzle_type=get_value(data, 'Nozzle type', None, False),
            gas=get_value(data, 'GAVD Gas', None, False),
        ),
        comment=get_value(data, 'GAVD comment', None, False),
    )


def map_spin_coating(i, j, lab_ids, data, upload_id, sc_class):
    archive = sc_class(
        name='spin coating ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value(
                    data,
                    'Viscosity [mPa*s]',
                    None,
                    unit=['mPa*s'],
                ),
                solution_contact_angle=get_value(
                    data,
                    'Contact angle [°]',
                    None,
                    unit=['°'],
                ),
            )
        ],
        annealing=map_annealing(data),
        atmosphere=map_atmosphere(data),
        recipe_steps=[
            SpinCoatingRecipeSteps(
                speed=get_value(data, f'Rotation speed {step}[rpm]', None, unit='rpm'),
                time=get_value(data, f'Rotation time {step}[s]', None, unit='s'),
                acceleration=get_value(
                    data, f'Acceleration {step}[rpm/s]', None, unit='rpm/s'
                ),
            )
            for step in ['', '1 ', '2 ', '3 ', '4 ']
            if get_value(data, f'Rotation time {step}[s]')
        ],
    )

    # Set quenching based on available data
    archive.quenching = (
        map_anti_solvent_quenching(data)
        or map_vacuum_quenching(data)
        or map_gas_quenching_with_nozzle(data)
    )

    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_spin_coating_{material}', archive)


def map_blade_coating(i, j, lab_ids, data, upload_id, blade_coating_class):
    archive = blade_coating_class(
        name='blade coating ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value(
                    data,
                    'Viscosity [mPa*s]',
                    None,
                    unit=['mPa*s'],
                ),
                solution_contact_angle=get_value(
                    data,
                    'Contact angle [°]',
                    None,
                    unit=['°'],
                ),
            )
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
        annealing=map_annealing(data),
        properties=BladeCoatingProperties(
            blade_speed=get_value(data, 'Blade Speed [mm/s]', None, unit='mm/s'),
            dispensed_volume=get_value(
                data, 'Dispensed Ink Volume [uL]', None, unit='uL'
            ),
            blade_substrate_gap=get_value(data, 'Blade Gap [um]', None, unit='um'),
            blade_size=get_value(data, 'Blade Size', None, False),
            coating_width=get_value(data, 'Coating Width [mm]', None, unit='mm'),
            coating_length=get_value(data, 'Coating Length [mm]', None, unit='mm'),
            dead_length=get_value(data, 'Dead Length [mm]', None, unit='mm'),
            bed_temperature=get_value(data, 'Bed Temperature [°C]', None, unit='°C'),
            ink_temperature=get_value(data, 'Ink Temperature [°C]', None, unit='°C'),
        ),
    )

    # Set quenching based on available data
    archive.quenching = (
        map_vacuum_quenching(data)
        or map_gas_quenching_with_nozzle(data)
        or map_air_knife_gas_quenching(data)
    )

    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_blade_coating_{material}', archive)


def map_gravure_printing(i, j, lab_ids, data, upload_id, gravure_printing_class):
    archive = gravure_printing_class(
        name='gravure printing ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value(
                    data,
                    'Viscosity [mPa*s]',
                    None,
                    unit=['mPa*s'],
                ),
                solution_contact_angle=get_value(
                    data,
                    'Contact angle [°]',
                    None,
                    unit=['°'],
                ),
            )
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
        annealing=map_annealing(data),
        properties=GravurePrintingProperties(
            gp_coating_speed=get_value(
                data, 'Coating Speed [m/min]', None, True, unit='m/minute'
            ),
            screen_ruling=get_value(data, 'Screen Ruling [lines/cm]', None, True, None),
            gp_method=get_value(data, 'R2R or S2S', '', False),
            gp_direction=get_value(data, 'Forward or Reverse', '', False),
            cell_type=get_value(data, 'Cell Type', None, False),
            ink_temperature=get_value(data, 'Ink Temperature [°C]', None, unit='°C'),
        ),
    )

    # Set quenching based on available data
    archive.quenching = map_anti_solvent_quenching(data) or map_air_knife_gas_quenching(
        data
    )

    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_gravure_printing_{material}', archive)


def map_sdc(i, j, lab_ids, data, upload_id, sdc_class):
    archive = sdc_class(
        name='slot die coating ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value(
                    data,
                    'Viscosity [mPa*s]',
                    None,
                    unit=['mPa*s'],
                ),
                solution_contact_angle=get_value(
                    data,
                    'Contact angle [°]',
                    None,
                    unit=['°'],
                ),
            )
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
        annealing=map_annealing(data),
        properties=SlotDieCoatingProperties(
            coating_run=get_value(data, 'Coating run', None, False),
            flow_rate=get_value(
                data,
                ['Flow rate [uL/min]', 'Flow rate [ul/min]'],
                None,
                unit=['uL/minute', 'uL/minute'],
            ),
            slot_die_head_distance_to_thinfilm=get_value(
                data, 'Head gap [mm]', unit='mm'
            ),
            slot_die_head_speed=get_value(data, 'Speed [mm/s]', unit='mm/s'),
            coated_area=get_value(data, 'Coated area [mm²]', unit='mm**2'),
            temperature=get_value(
                data, 'Chuck heating temperature [°C]', None, unit='°C'
            ),
        ),
        quenching=map_air_knife_gas_quenching(data),
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_slot_die_coating_{material}', archive)


def map_inkjet_printing(i, j, lab_ids, data, upload_id, inkjet_class):
    location = get_value(data, 'Tool/GB name', '', False)
    archive = inkjet_class(
        name='inkjet printing ' + get_value(data, 'Material name', '', False),
        location=location,
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),
                solution_volume=get_value(
                    data,
                    [
                        'Solution volume [um]',
                        'Solution volume [uL]',
                    ],  # the um (wrong unit) is for parsing the typo in case of old excels
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value(
                    data,
                    'Viscosity [mPa*s]',
                    None,
                    unit=['mPa*s'],
                ),
                solution_contact_angle=get_value(
                    data,
                    'Contact angle [°]',
                    None,
                    unit=['°'],
                ),
            )
        ],
        layer=map_layer(data),
        nozzle_voltage_profile=NozzleVoltageProfile(
            config_file=get_value(data, 'Nozzle voltage config file', None, False)
        ),
        properties=InkjetPrintingProperties(
            printing_run=get_value(data, 'Printing run', None, False),
            image_used=get_value(data, 'Image used', None, False),
            print_head_properties=PrintHeadProperties(
                number_of_active_print_nozzles=get_value(
                    data, 'Number of active nozzles', None
                ),
                active_nozzles=get_value(data, 'Active nozzles', None, False),
                print_nozzle_drop_frequency=get_value(
                    data, 'Droplet per second [1/s]', None, unit='1/s'
                ),
                print_head_angle=get_value(
                    data, 'Print head angle [deg]', None, unit='deg'
                ),
                print_speed=get_value(data, 'Printing speed [mm/s]', None, unit='mm/s'),
                print_nozzle_drop_volume=get_value(
                    data,
                    ['Droplet volume [pl]', 'Droplet volume [pL]'],
                    None,
                    unit=['pL', 'pL'],
                ),
                print_head_temperature=get_value(
                    data, 'Nozzle temperature [°C]', None, unit='°C'
                ),
                print_head_distance_to_substrate=get_value(
                    data, 'Dropping Height [mm]', None, unit='mm'
                ),
                print_head_name=get_value(data, 'Printhead name', None, False),
            ),
            cartridge_pressure=get_value(
                data,
                ['Ink reservoir pressure [bar]', 'Ink reservoir pressure [mbar]'],
                None,
                unit=['bar', 'mbar'],
            ),
            substrate_temperature=get_value(
                data, 'Table temperature [°C]', None, unit='°C'
            ),
            drop_density=get_value(
                data,
                ['Droplet density [dpi]', 'Droplet density X [dpi]'],
                None,
                unit=['1/in', '1/in'],
            ),
            drop_density_y=get_value(
                data, 'Droplet density Y [dpi]', None, unit='1/in'
            ),
            printed_area=get_value(data, 'Printed area [mm²]', None, unit='mm**2'),
            substrate_height=get_value(
                data, 'Substrate thickness [mm]', None, unit='mm'
            ),
        ),
        print_head_path=PrintHeadPath(
            quality_factor=get_value(data, 'Quality factor', None, False),
            step_size=get_value(data, 'Step size', None, False),
            directional=get_value(data, 'Printing direction', None, False),
            swaths=get_value(data, 'Number of swaths', None),
        ),
        atmosphere=map_atmosphere(data),
        annealing=map_annealing(data),
    )

    # Set quenching based on available data
    archive.quenching = map_gas_flow_assisted_vacuum_drying(data)

    if location in ['Pixdro', 'iLPixdro']:  # printer param
        voltage_a = get_value(data, 'Wf Level 1[V]', None, unit='V')
        voltage_b = get_value(data, 'Wf Level 2[V]', None, unit='V')
        voltage_c = get_value(data, 'Wf Level 3[V]', None, unit='V')
        archive.nozzle_voltage_profile = LP50NozzleVoltageProfile(
            number_of_pulses=get_value(data, 'Wf Number of Pulses', None),
            voltage_a=voltage_a,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_a=voltage_a
            / get_value(data, 'Wf Rise 1[V/us]', None, unit='V/us')
            if voltage_a
            else None,
            peak_time_a=get_value(data, 'Wf Width 1[us]', None, unit=['us']),
            fall_edge_a=voltage_a
            / get_value(data, 'Wf Fall 1[V/us]', None, unit='V/us')
            if voltage_a
            else None,
            time_space_a=get_value(data, 'Wf Space 1[us]', None, unit=['us']),
            voltage_b=voltage_b,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_b=voltage_b
            / get_value(data, 'Wf Rise 2[V/us]', None, unit='V/us')
            if voltage_b
            else None,
            peak_time_b=get_value(data, 'Wf Width 2[us]', None, unit=['us']),
            fall_edge_b=voltage_b
            / get_value(data, 'Wf Fall 2[V/us]', None, unit='V/us')
            if voltage_b
            else None,
            time_space_b=get_value(data, 'Wf Space 2[us]', None, unit=['us']),
            voltage_c=voltage_c,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_c=voltage_c
            / get_value(data, 'Wf Rise 3[V/us]', None, unit='V/us')
            if voltage_c
            else None,
            peak_time_c=get_value(data, 'Wf Width 3[us]', None, unit=['us']),
            fall_edge_c=voltage_c
            / get_value(data, 'Wf Fall 3[V/us]', None, unit='V/us')
            if voltage_c
            else None,
            time_space_c=get_value(data, 'Wf Space 3[us]', None, unit=['us']),
        )

    if location in ['iLNotion', 'Notion']:  # printer param
        archive.nozzle_voltage_profile = NotionNozzleVoltageProfile(
            number_of_pulses=get_value(data, 'Wf Number of Pulses', None),
            # for loop over number of pulses with changing _a suffix of variales below
            delay_time_a=get_value(data, 'Wf Delay Time [us]', None, unit='us'),
            rise_edge_a=get_value(data, 'Wf Rise Time [us]', None, unit='us'),
            peak_time_a=get_value(data, 'Wf Hold Time [us]', None, unit='us'),
            fall_edge_a=get_value(data, 'Wf Fall Time [us]', None, unit='us'),
            time_space_a=get_value(data, 'Wf Relax Time [us]', None, unit='us'),
            voltage_a=get_value(data, 'Wf Voltage [V]', None, unit='V'),
            # multipulse_a=get_value(data, 'Wf Multipulse [1/0]', None, False),
            number_of_greylevels_a=get_value(data, 'Wf Number Greylevels', None),
            grey_level_0_pulse_a=get_value(
                data, 'Wf Grey Level 0 Use Pulse [1/0]', None
            ),
            grey_level_1_pulse_a=get_value(
                data, 'Wf Grey Level 1 Use Pulse [1/0]', None
            ),
        )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_inkjet_printing_{material}', archive)


def map_screen_printing(i, j, lab_ids, data, upload_id, screen_printing_class):
    archive = screen_printing_class(
        name='screen printing ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value(
                    data,
                    'Viscosity [mPa*s]',
                    None,
                    unit=['mPa*s'],
                ),
                solution_contact_angle=get_value(
                    data,
                    'Contact angle [°]',
                    None,
                    unit=['°'],
                ),
            )
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
        annealing=map_annealing(data),
        properties=ScreenPrintingProperties(
            screen_mesh=MeshProperties(
                mesh_material=get_value(data, 'Mesh material', None, False),
                mesh_count=get_value(data, 'Mesh count [meshes/cm]', None),
                mesh_thickness=get_value(data, 'Mesh thickness [um]', None, unit='um'),
                thread_diameter=get_value(
                    data, 'Thread diameter [um]', None, unit='um'
                ),
                mesh_opening=get_value(data, 'Mesh opening [um]', None, unit='um'),
                mesh_tension=get_value(data, 'Mesh tension [N/cm]', None, unit='N/cm'),
                mesh_angle=get_value(data, 'Mesh angle [°]', None, unit='°'),
            ),
            emulsion_material=get_value(data, 'Emulsion material', None, False),
            emulsion_thickness=get_value(
                data, 'Emulsion thickness [um]', None, unit='um'
            ),
            squeegee_material=get_value(data, 'Squeegee material', None, False),
            squeegee_shape=get_value(data, 'Squeegee shape', None, False),
            squeegee_angle=get_value(data, 'Squeegee angle [°]', None, unit='°'),
            sp_speed=get_value(data, 'Printing speed [mm/s]', None, unit='mm/s'),
            sp_direction=get_value(data, 'Printing direction', None, False),
            sp_pressure=get_value(data, 'Printing pressure [bar]', None, unit='bar'),
            snap_off=get_value(data, 'Snap-off distance [mm]', None, unit='mm'),
            sp_method=get_value(data, 'Printing method', None, False),
        ),
    )

    # Set quenching based on available data
    archive.quenching = (
        map_vacuum_quenching(data)
        or map_gas_quenching_with_nozzle(data)
        or map_air_knife_gas_quenching(data)
    )

    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_screen_printing_{material}', archive)


def map_lamination(i, j, lab_ids, data, upload_id, lamination_class):
    archive = lamination_class(
        name='Lamination',
        location=get_value(data, 'Tool/GB name', '', False),
        # Hier muss man evtl was anpassen, da das Lamination ja als letztes von zwei halbstacks ist...
        position_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        settings=LaminationSettings(
            temperature=get_value(data, 'Temperature [°C]', None),
            pressure=get_value(data, 'Pressure [MPa]', None),
            force=get_value(data, 'Force [N]', None),
            area=get_value(data, 'Area [mm²]', None),
            time=get_value(data, 'Time [s]', None),
            heat_up_time=get_value(data, 'Heat up time [s]', None),
            cool_down_time=get_value(data, 'Cool down time [s]', None),
            stamp_material=get_value(data, 'Stamp Material', '', False),
            stamp_thickness=get_value(data, 'Stamp Thickness [mm]', None),
            stamp_area=get_value(data, 'Stamp Area [mm²]', None),
        ),
    )
    return (f'{i}_{j}_lamination', archive)


def map_cleaning(i, j, lab_ids, data, upload_id, cleaning_class):
    archive = cleaning_class(
        name='Cleaning',
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        location=get_value(data, 'Tool/GB name', '', False),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        cleaning=[
            SolutionCleaning(
                time=get_value(
                    data,
                    [f'Time {i} [s]', f'Time {i} [min]'],
                    None,
                    unit=['s', 'minute'],
                ),
                temperature=get_value(data, f'Temperature {i} [°C]', None, unit='°C'),
                solvent_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'Solvent {i}', None, False), load_data=False
                ),
            )
            for i in range(10)
            if get_value(data, f'Solvent {i}', None, False)
        ],
        cleaning_uv=[
            UVCleaning(
                time=get_value(
                    data,
                    ['UV-Ozone Time [s]', 'UV-Ozone Time [min]'],
                    None,
                    unit=['s', 'minute'],
                )
            )
        ],
        cleaning_plasma=[
            PlasmaCleaning(
                time=get_value(
                    data,
                    ['Gas-Plasma Time [s]', 'Gas-Plasma Time [min]'],
                    None,
                    unit=['s', 'minute'],
                ),
                power=get_value(data, 'Gas-Plasma Power [W]', None, unit='W'),
                plasma_type=get_value(data, 'Gas-Plasma Gas', None, False),
            )
        ],
        cleaning_corona=[
            CoronaCleaning(
                time=get_value(
                    data,
                    ['Corona Time [s]', 'Corona Time [min]'],
                    None,
                    unit=['s', 'minute'],
                ),
                power=get_value(data, 'Corona Power [W]', None, unit='W'),
            )
        ],
    )

    return (f'{i}_{j}_cleaning', archive)


def map_substrate(data, substrate_class):
    # Create LayerProperties for substrate_properties
    substrate_props = [
        LayerProperties(
            layer_thickness=get_value(data, 'TCO thickness [nm]', None, unit=['nm']),
            layer_transmission=get_value(data, 'Transmission [%]', None),
            layer_sheet_resistance=get_value(
                data, 'Sheet Resistance [Ohms/square]', None, unit=['ohm']
            ),
            layer_type='Substrate Conductive Layer',
            layer_material_name=get_value(
                data, 'Substrate conductive layer', '', False
            ),
        )
    ]
    archive = substrate_class(
        datetime=get_datetime(data, 'Date'),
        name='Substrate '
        + get_value(data, 'Sample dimension', '', False)
        + ' '
        + get_value(data, 'Substrate material', '', False)
        + ' '
        + get_value(data, 'Substrate conductive layer', '', False),
        solar_cell_area=get_value(data, 'Sample area [cm^2]', None, unit=['cm**2']),
        pixel_area=get_value(
            data, ['Pixel area', 'Pixel area [cm^2]'], None, unit=['cm**2', 'cm**2']
        ),
        number_of_pixels=get_value(data, 'Number of pixels', None),
        substrate=get_value(data, 'Substrate material', '', False),
        description=get_value(data, 'Notes', '', False),
        lab_id=get_value(data, 'Bottom Cell Name', '', False),
        conducting_material=[get_value(data, 'Substrate conductive layer', '', False)],
        substrate_properties=substrate_props,
    )
    return archive


def map_evaporation(
    i, j, lab_ids, data, upload_id, evaporation_class, coevaporation=False
):
    material = get_value(data, 'Material name', '', False)
    file_name = (
        f'{i}_{j}_coevaporation_{material}'
        if coevaporation
        else f'{i}_{j}_evaporation_{material}'
    )
    archive = evaporation_class(
        name='evaporation ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', '', False),
        co_evaporation=coevaporation,
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
    )
    evaporations = []
    for mat in ['', ' 1', ' 2', ' 3', ' 4']:
        if pd.isna(data.get(f'Material name{mat}')) or (
            f'Material name{mat}' == 'Material name' and coevaporation
        ):
            continue
        evaporation = None
        if coevaporation:
            evaporation = PerovskiteEvaporation()
        if (
            get_value(data, 'Organic', '', False).lower().startswith('n')
            or get_value(data, 'Organic', '', False).lower().startswith('0')
            or get_value(data, 'Organic', '', False).lower().startswith('f')
        ):
            evaporation = InorganicEvaporation()

        if (
            get_value(data, 'Organic', '', False).lower().startswith('y')
            or get_value(data, 'Organic', '', False).lower().startswith('1')
            or get_value(data, 'Organic', '', False).lower().startswith('t')
        ):
            evaporation = OrganicEvaporation()
            if get_value(data, 'Temperature [°C]', None):
                evaporation.temparature = [
                    get_value(data, 'Temperature [°C]', None)
                ] * 2

        if not evaporation:
            return (file_name, archive)

        if get_value(data, f'Source temperature start{mat}[°C]', None) and get_value(
            data, f'Source temperature end{mat}[°C]', None
        ):
            evaporation.temparature = [
                get_value(data, f'Source temperature start{mat}[°C]', None, unit='°C'),
                get_value(data, f'Source temperature end{mat}[°C]', None, unit='°C'),
            ]

        evaporation.thickness = get_value(data, f'Thickness{mat} [nm]', unit='nm')
        evaporation.start_rate = get_value(
            data, f'Rate start{mat} [angstrom/s]', unit='angstrom/s'
        )
        evaporation.target_rate = get_value(
            data,
            [f'Rate{mat} [angstrom/s]', f'Rate target{mat} [angstrom/s]'],
            unit=['angstrom/s', 'angstrom/s'],
        )
        evaporation.substrate_temparature = get_value(
            data, f'Substrate temperature{mat} [°C]', unit='°C'
        )
        evaporation.pressure = get_value(
            data,
            [f'Base pressure{mat} [bar]', f'Base pressure{mat} [mbar]'],
            None,
            unit=['bar', 'mbar'],
        )
        evaporation.pressure_start = get_value(
            data,
            [f'Pressure start{mat} [bar]', f'Pressure start{mat} [mbar]'],
            None,
            unit=['bar', 'mbar'],
        )
        evaporation.pressure_end = get_value(
            data,
            [f'Pressure end{mat} [bar]', f'Pressure end{mat} [mbar]'],
            None,
            unit=['bar', 'mbar'],
        )
        evaporation.tooling_factor = get_value(data, f'Tooling factor{mat}')

        evaporation.chemical_2 = PubChemPureSubstanceSectionCustom(
            name=get_value(data, f'Material name{mat}', None, False), load_data=False
        )
        evaporations.append(evaporation)

    organic_value = get_value(data, 'Organic', '', False).lower()
    if organic_value.startswith(('n', '0', 'f')):
        archive.inorganic_evaporation = evaporations
    elif organic_value.startswith(('y', '1', 't')):
        archive.organic_evaporation = evaporations
    elif coevaporation:
        archive.perovskite_evaporation = evaporations
    return (file_name, archive)


def map_annealing_class(i, j, lab_ids, data, upload_id, annealing_class):
    archive = annealing_class(
        name='Thermal Annealing',
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        location=get_value(data, 'Tool/GB name', '', False),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        annealing=map_annealing(data),
        atmosphere=Atmosphere(
            relative_humidity=get_value(data, 'Relative humidity [%]', None),
        ),
    )
    return (f'{i}_{j}_annealing', archive)


def map_sputtering(i, j, lab_ids, data, upload_id, sputter_class):
    archive = sputter_class(
        name='sputtering ' + get_value(data, 'Material name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        location=get_value(data, 'Tool/GB name', '', False),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
    )
    process = SputteringProcess(
        thickness=get_value(data, 'Thickness [nm]', unit='nm'),
        gas_flow_rate=get_value(data, 'Gas flow rate [cm^3/min]', unit='cm**3/minute'),
        rotation_rate=get_value(data, 'Rotation rate [rpm]'),
        power=get_value(data, 'Power [W]', unit='W'),
        temperature=get_value(data, 'Temperature [°C]', unit='°C'),
        deposition_time=get_value(data, 'Deposition time [s]', unit='s'),
        burn_in_time=get_value(data, 'Burn in time [s]', unit='s'),
        pressure=get_value(data, 'Pressure [mbar]', unit='mbar'),
        target_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Material name', None, False), load_data=False
        ),
        gas_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Gas', None, False), load_data=False
        ),
    )
    archive.processes = [process]
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_sputtering_{material}', archive)


def map_close_space_sublimation(i, j, lab_ids, data, upload_id, css_class):
    material = get_value(data, 'Material name', '', False)
    archive = css_class(
        name='Close Space Sublimation ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
    )
    archive.process = CSSProcess(
        thickness=get_value(data, 'Thickness [nm]', unit='nm'),
        substrate_temperature=get_value(data, 'Substrate temperature [°C]', unit='°C'),
        source_temperature=get_value(data, 'Source temperature [°C]', unit='°C'),
        substrate_source_distance=get_value(
            data, 'Substrate source distance [mm]', unit='mm'
        ),
        deposition_time=get_value(data, 'Deposition Time [s]', unit='s'),
        carrier_gas=get_value(data, 'Carrier gas', None, False),
        pressure=get_value(data, 'Process pressure [bar]', None, unit='bar'),
        chemical_2=PubChemPureSubstanceSectionCustom(
            name=get_value(data, 'Material name', None, False), load_data=False
        ),
        material_state=get_value(data, 'Material state', None, False),
    )

    return (f'{i}_{j}_close_space_subimation_{material}', archive)


def map_dip_coating(i, j, lab_ids, data, upload_id, dc_class):
    archive = dc_class(
        name='dip coating ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value(
                    data,
                    'Viscosity [mPa*s]',
                    None,
                    unit=['mPa*s'],
                ),
                solution_contact_angle=get_value(
                    data,
                    'Contact angle [°]',
                    None,
                    unit=['°'],
                ),
            )
        ],
        layer=map_layer(data),
        properties=DipCoatingProperties(
            time=get_value(data, 'Dipping duration [s]', unit='s'),
        ),
        annealing=map_annealing(data),
        atmosphere=map_atmosphere(data),
    )
    material = get_value(data, 'Material name', '', False)
    return (f'{i}_{j}_dip_coating_{material}', archive)


def map_laser_scribing(i, j, lab_ids, data, upload_id, laser_class):
    archive = laser_class(
        name='laser scribing',
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        description=get_value(data, 'Notes', None, False),
        recipe_file=get_value(data, 'Recipe file', None, False),
        patterning=get_value(data, 'Patterning Step', None, False),
        layout=get_value(data, 'Layout', None, False),
        properties=LaserScribingProperties(
            laser_wavelength=get_value(data, 'Laser wavelength [nm]', None),
            laser_pulse_time=get_value(data, 'Laser pulse time [ps]', None),
            laser_pulse_frequency=get_value(data, 'Laser pulse frequency [kHz]', None),
            speed=get_value(data, 'Speed [mm/s]', None),
            fluence=get_value(data, 'Fluence [J/cm2]', None),
            power_in_percent=get_value(data, 'Power [%]', None),
            cell_width=get_value(data, 'Width of cell [mm]', None),
            dead_area=get_value(data, 'Dead area [cm2]', None),
            number_of_cells=get_value(data, 'Number of cells', None),
        ),
    )

    return (f'{i}_{j}_laser_scribing', archive)


def map_atomic_layer_deposition(i, j, lab_ids, data, upload_id, ald_class):
    archive = ald_class(
        name='atomic layer deposition '
        + get_value(data, 'Material name', '', number=False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', '', number=False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
        properties=ALDPropertiesIris(
            source=get_value(data, 'Source', None, number=False),
            thickness=get_value(data, 'Thickness [nm]', None),
            temperature=get_value(
                data,
                ['Temperature [°C]', 'Reactor Temperature [°C]'],
                None,
                unit=['°C', '°C'],
            ),
            rate=get_value(data, 'Rate [A/s]', None),
            time=get_value(data, 'Time [s]', None),
            number_of_cycles=get_value(data, 'Number of cycles', None),
            material=ALDMaterial(
                material=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, 'Precursor 1', None, number=False),
                    load_data=False,
                ),
                pulse_duration=get_value(data, 'Pulse duration 1 [s]', None),
                pulse_flow_rate=get_value(data, 'Pulse flow rate 1 [ccm]', None),
                manifold_temperature=get_value(
                    data,
                    [
                        'Manifold Temperature [°C]',
                        'Manifold temperature [°C]',
                        'Manifold temperature 1 [°C]',
                    ],
                    None,
                    unit=['°C', '°C', '°C'],
                ),
                purge_duration=get_value(data, 'Purge duration 1 [s]', None),
                purge_flow_rate=get_value(data, 'Purge flow rate 1 [ccm]', None),
                bottle_temperature=get_value(data, 'Bottle temperature 1 [°C]', None),
            ),
            oxidizer_reducer=ALDMaterial(
                material=PubChemPureSubstanceSectionCustom(
                    name=get_value(
                        data, 'Precursor 2 (Oxidizer/Reducer)', None, number=False
                    ),
                    load_data=False,
                ),
                pulse_duration=get_value(data, 'Pulse duration 2 [s]', None),
                pulse_flow_rate=get_value(data, 'Pulse flow rate 2 [ccm]', None),
                manifold_temperature=get_value(
                    data, 'Manifold temperature 2 [°C]', None
                ),
                purge_duration=get_value(data, 'Purge duration 2 [s]', None),
                purge_flow_rate=get_value(data, 'Purge flow rate 2 [ccm]', None),
                bottle_temperature=get_value(data, 'Bottle temperature 2 [°C]', None),
            ),
        ),
    )
    material = get_value(data, 'Material name', '', number=False)
    return (f'{i}_{j}_ALD_{material}', archive)


def map_generic(i, j, lab_ids, data, upload_id, generic_class):
    archive = generic_class(
        name=get_value(data, 'Name', '', False),
        positon_in_experimental_plan=i,
        datetime=get_datetime(data, 'Datetime'),
        description=get_value(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
    )
    name = get_value(data, 'Name', '', False)
    return (f'{i}_{j}_generic_process_{name.replace(" ", "_")}', archive)
