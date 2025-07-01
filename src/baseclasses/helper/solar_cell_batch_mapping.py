import re
import unittest
from datetime import datetime

import pandas as pd
from nomad.datamodel.metainfo.basesections import CompositeSystemReference
from nomad.units import ureg

from baseclasses import LayerProperties, PubChemPureSubstanceSectionCustom
from baseclasses.atmosphere import Atmosphere
from baseclasses.material_processes_misc import (
    AirKnifeGasQuenching,
    Annealing,
    AntiSolventQuenching,
    GasFlowAssistedVacuumDrying,
    GasQuenchingWithNozzle,
    PlasmaCleaning,
    SolutionCleaning,
    UVCleaning,
    VacuumQuenching,
)
from baseclasses.material_processes_misc.laser_scribing import LaserScribingProperties
from baseclasses.solar_energy.carbonpaste import CarbonPasteLayerProperties
from baseclasses.solution import Solution, SolutionChemical
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
from baseclasses.wet_chemical_deposition.dip_coating import DipCoatingProperties
from baseclasses.wet_chemical_deposition.inkjet_printing import (
    InkjetPrintingProperties,
    LP50NozzleVoltageProfile,
    NotionNozzleVoltageProfile,
    NozzleVoltageProfile,
    PrintHeadPath,
    PrintHeadProperties,
)
from baseclasses.wet_chemical_deposition.slot_die_coating import (
    SlotDieCoatingProperties,
)
from baseclasses.wet_chemical_deposition.spin_coating import SpinCoatingRecipeSteps


def get_entry_id_from_file_name(file_name, upload_id):
    from nomad.utils import hash

    return hash(upload_id, file_name)


def get_reference(upload_id, file_name):
    entry_id = get_entry_id_from_file_name(file_name, upload_id)
    return f'../uploads/{upload_id}/archive/{entry_id}#data'


def get_value(data, key, default=None, number=True, unit=None):
    if not isinstance(key, list):
        key = [key]
    if unit and not isinstance(unit, list):
        unit = [unit]

    try:
        if not unit:
            for k in key:
                if k not in data:
                    continue
                if pd.isna(data[k]):
                    return default
                if number:
                    return float(data[k])
                return str(data[k]).strip()
        if unit:
            for k, u in zip(key, unit):
                if k not in data:
                    continue
                if pd.isna(data[k]):
                    return default
                if number and u:
                    Q_ = ureg.Quantity
                    return Q_(float(data[k]), ureg(u))
        return default
    except Exception as e:
        raise e


def _find_matching_columns(data, keys):
    """Find all columns that match any of the given keys."""
    matching_columns = []
    for col in data.index:
        for k in keys:
            if k in col:
                matching_columns.append(col)
                break
    return matching_columns


def _parse_unit_from_column(column_name, pattern):
    """Extract unit from column name using regex pattern."""
    match = re.search(pattern, column_name, re.IGNORECASE)
    if match and match.group(1):
        return match.group(1)
    return None


def _normalize_time_units(unit_string):
    """Convert 'min' to 'minute' in unit strings for proper Pint parsing."""
    if unit_string == 'min':
        return 'minute'
    elif '/min' in unit_string:
        return unit_string.replace('/min', '/minute')
    elif 'min' in unit_string and ('/' in unit_string or '^' in unit_string):
        # Handle composite units like cm^3/min
        return unit_string.replace('min', 'minute')
    return unit_string


def _validate_dimension(quantity, dimensions):
    """Check if quantity matches any of the allowed dimensions."""
    if not dimensions:
        return True

    if not isinstance(dimensions, list):
        dimensions = [dimensions]

    for dim in dimensions:
        if quantity.check(dim):
            return True
    return False


def _process_matching_columns(
    data, matching_columns, pattern, dimension=None, target_unit=None, number=True
):
    """
    Process matching columns to find one with valid dimension and/or convert units.

    Args:
        data: The data series
        matching_columns: List of column names to process
        pattern: Regex pattern for unit extraction
        dimension: Optional dimension(s) to validate against
        target_unit: Optional target unit for conversion
        number: Whether to return numeric values

    Returns:
        tuple: (success, result) where success is bool and result is the processed value
    """
    for column_name in matching_columns:
        if pd.isna(data[column_name]):
            continue

        unit_from_file = _parse_unit_from_column(column_name, pattern)
        if not unit_from_file:
            continue

        # Handle time unit normalization if needed
        if dimension and 'time' in str(dimension):
            unit_from_file = _normalize_time_units(unit_from_file)

        try:
            # Create quantity
            Q_ = ureg.Quantity(float(data[column_name]), ureg(unit_from_file))

            # Validate dimension if specified
            if dimension and not _validate_dimension(Q_, dimension):
                continue

            # Convert to target unit if specified
            if target_unit:
                return True, Q_.to(target_unit)
            # Return quantity or string based on number parameter
            elif number:
                return True, Q_
            else:
                return True, str(data[column_name]).strip()

        except Exception:
            continue

    return False, None


def _handle_simple_case(data, keys, default, number):
    """Handle the simple case: no unit conversion, no dimension validation."""
    for k in keys:
        if k not in data:
            continue
        if pd.isna(data[k]):
            return default
        if number:
            return float(data[k])
        return str(data[k]).strip()
    return default


def get_value_dynamically(
    data, key, default=None, number=True, unit=None, dimension=None
):
    """
    Dynamically extract values from data with unit parsing from column names.

    This function searches for column names that match the given key(s) and
    automatically extracts unit information from square brackets in the column name.
    It can validate dimensions and convert units as needed. When multiple columns
    match the same key, it tries each one until it finds a valid match.

    Args:
        data (pd.Series): Row of data from a DataFrame with column names as index
        key (str or list): Key(s) to search for in column names. If list, tries each key
        default (any, optional): Default value to return if key not found or data is NaN.
            Defaults to None.
        number (bool, optional): Whether to convert the value to float. Defaults to True.
        unit (str, optional): Target unit to convert the value to. If provided, the function
            will parse the unit from the column name and convert to this target unit.
        dimension (str or list, optional): Expected physical dimension(s) (e.g., 'temperature', 'length').
            Used to validate that the parsed unit has the correct dimensionality.
            If list, any matching dimension is acceptable.

    Returns:
        float, str, pint.Quantity, or default:
            - If unit is None: returns float (if number=True) or string, after dimension validation
            - If unit is provided: returns pint.Quantity converted to target unit
            - Returns default if key not found, value is NaN, or no valid match found

    Raises:
        ValueError: If no column found with valid dimension when dimension is specified
        Exception: Re-raises any other exceptions that occur during processing

    Example:
        >>> data = pd.Series({'Temperature [°C]': 25.5, 'Pressure [bar]': 1.2})
        >>> get_value_dynamically(data, 'Temperature', unit='K', dimension='temperature')
        <Quantity(298.65, 'kelvin')>

        >>> # Multiple matching columns - finds the one with valid dimension
        >>> data = pd.Series({'Solute concentration [M]': 0.1, 'Solute concentration [mg/mL]': 50})
        >>> get_value_dynamically(data, 'Solute concentration', unit='mM', dimension='concentration')
        <Quantity(100.0, 'millimolar')>

    Note:
        - Uses regex pattern to extract units from column names in format "Key [unit]"
        - Supports dimension validation using Pint's dimensionality checking
        - When multiple columns match the same key, tries each until finding valid dimension
        - For dimension parameter, use physical dimension names like 'temperature', 'length', etc.
    """

    # Normalize inputs
    if not isinstance(key, list):
        key = [key]
    if dimension and not isinstance(dimension, list):
        dimension = [dimension]

    pattern = rf'^(?:{"|".join(key)})\s*\[(.*?)\]$'

    try:
        # Handle simple case: no unit conversion, no dimension validation
        if not unit and not dimension:
            return _handle_simple_case(data, key, default, number)

        # Find all matching columns for complex cases
        matching_columns = _find_matching_columns(data, key)
        if not matching_columns:
            return default

        # Handle dimension validation without unit conversion
        if not unit and dimension:
            success, result = _process_matching_columns(
                data, matching_columns, pattern, dimension=dimension, number=number
            )
            return result if success else default

        # Handle unit conversion (with optional dimension validation)
        if unit:
            success, result = _process_matching_columns(
                data, matching_columns, pattern, dimension=dimension, target_unit=unit
            )

            if success:
                return result

            # Handle fallback cases
            has_any_values = any(not pd.isna(data[col]) for col in matching_columns)

            if not has_any_values:
                return default
            elif dimension:
                print(
                    f'No column found matching key {key} with valid dimension {dimension}. '
                    f'Available columns: {_find_matching_columns(data, key)}'
                )
                return default
            else:
                # No dimension constraint, try direct conversion
                for column_name in matching_columns:
                    if not pd.isna(data[column_name]):
                        try:
                            Q_ = ureg.Quantity(float(data[column_name]), ureg(unit))
                            return Q_
                        except Exception:
                            continue
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
    # Check if key exists and value is not NaN
    if key not in data or pd.isna(data[key]):
        return None

    # List of supported date formats to try
    date_formats = [
        '%d-%m-%Y',  # 25-12-2024
        '%d/%m/%Y',  # 25/12/2024
        '%d.%m.%Y',  # 25.12.2024
        '%Y-%m-%d',  # 2024-12-25 (ISO format)
        '%d-%m-%y',  # 25-12-24 (2-digit year)
        '%d/%m/%y',  # 25/12/24 (2-digit year)
    ]

    date_value = str(data[key]).strip()

    # Try each format until one works
    for date_format in date_formats:
        try:
            datetime_object = datetime.strptime(date_value, date_format)
            # Convert to NOMAD format with midnight time
            return datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            continue  # Try next format

    # If no format worked, log warning and return None
    print(
        f"Warning: Could not parse date '{date_value}' with key '{key}'. Supported formats: {date_formats}"
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
    return Annealing(
        temperature=get_value_dynamically(
            data, 'Annealing temperature', None, unit='°C', dimension='[temperature]'
        ),
        time=get_value(data, 'Annealing time [min]', None, unit='minute'),
        atmosphere=get_value_dynamically(
            data, ['Annealing athmosphere', 'Annealing atmosphere'], None, False
        ),
    )


def map_atmosphere(data):
    return Atmosphere(
        oxygen_level_ppm=get_value_dynamically(data, 'GB oxygen level [ppm]', None),
        relative_humidity=get_value_dynamically(
            data, ['rel. humidity [%]', 'Room/GB humidity [%]'], None
        ),
        temperature=get_value_dynamically(
            data, 'Room temperature', None, unit='°C', dimension='[temperature]'
        ),
    )


def map_layer(data):
    if 'Carbon Paste Layer' in get_value_dynamically(data, 'Layer type', '', False):
        return [
            CarbonPasteLayerProperties(
                layer_type=get_value_dynamically(data, 'Layer type', None, False),
                layer_material_name=get_value_dynamically(
                    data, 'Material name', None, False
                ),
                layer_thickness=get_value_dynamically(
                    data, 'Layer thickness', None, unit='nm', dimension='[length]'
                ),
                supplier=get_value_dynamically(data, 'Supplier', None, False),
                batch=get_value_dynamically(data, 'Batch', None, False),
                drying_time=get_value_dynamically(
                    data, 'Drying Time', None, unit='s', dimension='[time]'
                ),
                cost=get_value_dynamically(data, 'Cost [EUR]', None, True),
            )
        ]
    else:
        return [
            LayerProperties(
                layer_type=get_value_dynamically(data, 'Layer type', None, False),
                layer_material_name=get_value_dynamically(
                    data, 'Material name', None, False
                ),
                layer_thickness=get_value_dynamically(
                    data, 'Layer thickness', None, unit='nm', dimension='[length]'
                ),
                layer_transmission=get_value_dynamically(
                    data, 'Transmission [%]', None, True
                ),
                layer_morphology=get_value_dynamically(data, 'Morphology', None, False),
                layer_sheet_resistance=get_value_dynamically(
                    data, 'Sheet Resistance [Ohms/square]', None, True
                ),
            )
        ]


def map_solutions(data):
    solvents = []
    solutes = []
    for col in data.index:
        if col.lower().startswith('solvent'):
            solvents.append(' '.join(col.split(' ')[:2]))
        if col.lower().startswith('solute'):
            solutes.append(' '.join(col.split(' ')[:2]))

    final_solvents = []
    final_solutes = []
    for solvent in sorted(set(solvents)):
        final_solvents.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value_dynamically(data, f'{solvent} name', None, False),
                    load_data=False,
                ),
                chemical_volume=get_value_dynamically(
                    data, f'{solvent} volume', None, unit='uL', dimension='[volume]'
                ),
                amount_relative=get_value_dynamically(
                    data, f'{solvent} relative amount', None
                ),
                chemical_id=get_value_dynamically(
                    data, f'{solvent} chemical ID', None, False
                ),
            )
        )
    for solute in sorted(set(solutes)):
        final_solutes.append(
            SolutionChemical(
                chemical_2=PubChemPureSubstanceSectionCustom(
                    name=get_value_dynamically(
                        data, [f'{solute} type', f'{solute} name'], None, False
                    ),
                    load_data=False,
                ),
                concentration_mol=get_value_dynamically(
                    data,
                    f'{solute} Concentration',
                    None,
                    unit='mM',
                    dimension='[concentration]',
                ),
                concentration_mass=get_value(
                    data,
                    [
                        f'{solute} Concentration [wt%]',
                        f'{solute} Concentration [mg/ml]',
                    ],
                    None,
                    unit=['wt%', 'mg/ml'],
                ),
                amount_relative=get_value_dynamically(
                    data, f'{solute} relative amount', None
                ),
                chemical_id=get_value_dynamically(
                    data, f'{solute} chemical ID', None, False
                ),
            )
        )

    archive = Solution(solvent=final_solvents, solute=final_solutes)

    return archive


def map_spin_coating(i, j, lab_ids, data, upload_id, sc_class):
    archive = sc_class(
        name='spin coating ' + get_value_dynamically(data, 'Material name', '', False),
        location=get_value_dynamically(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value_dynamically(data, 'Notes', '', False),
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
                solution_viscosity=get_value_dynamically(
                    data,
                    'Viscosity',
                    None,
                    unit=['mPa*s'],
                    dimension='[viscosity]',
                ),
                solution_contact_angle=get_value_dynamically(
                    data,
                    'Contact angle',
                    None,
                    unit=['°'],
                    dimension='[angle]',
                ),
            )
        ],
        annealing=map_annealing(data),
        atmosphere=map_atmosphere(data),
        recipe_steps=[
            SpinCoatingRecipeSteps(
                speed=get_value_dynamically(
                    data,
                    f'Rotation speed {step}',
                    None,
                    unit='rpm',
                    dimension='[frequency]',
                ),
                time=get_value_dynamically(
                    data, f'Rotation time {step}', None, unit='s', dimension='[time]'
                ),
                acceleration=get_value_dynamically(
                    data,
                    f'Acceleration {step}',
                    None,
                    unit='rpm/s',
                    dimension='[frequency]/[time]',
                ),
            )
            for step in ['', '1 ', '2 ', '3 ', '4 ']
            if get_value_dynamically(data, f'Rotation time {step}[s]')
        ],
    )
    if get_value_dynamically(data, 'Anti solvent name', None, False):
        archive.quenching = AntiSolventQuenching(
            anti_solvent_volume=get_value_dynamically(
                data, 'Anti solvent volume', None, unit='mL', dimension='[volume]'
            ),
            anti_solvent_dropping_time=get_value_dynamically(
                data, 'Anti solvent dropping time', None, unit='s', dimension='[time]'
            ),
            anti_solvent_dropping_height=get_value_dynamically(
                data,
                ['Anti solvent dropping height', 'Anti solvent dropping heigt'],
                None,
                unit='mm',
                dimension='[length]',
            ),
            anti_solvent_dropping_flow_rate=get_value_dynamically(
                data,
                'Anti solvent dropping speed',
                None,
                unit='uL/s',
                dimension='[volume]/[time]',
            ),
            anti_solvent_2=PubChemPureSubstanceSectionCustom(
                name=get_value_dynamically(data, 'Anti solvent name', None, False),
                load_data=False,
            ),
        )

    if get_value_dynamically(
        data, 'Vacuum quenching duration', None, unit='s', dimension='[time]'
    ):
        archive.quenching = VacuumQuenching(
            start_time=get_value_dynamically(
                data, 'Vacuum quenching start time', None, unit='s', dimension='[time]'
            ),
            duration=get_value_dynamically(
                data, 'Vacuum quenching duration', None, unit='s', dimension='[time]'
            ),
            pressure=get_value_dynamically(
                data,
                'Vacuum quenching pressure',
                None,
                unit='bar',
                dimension='[pressure]',
            ),
        )

    if get_value_dynamically(data, 'Gas', None, False):
        archive.quenching = GasQuenchingWithNozzle(
            starting_delay=get_value_dynamically(
                data, 'Gas quenching start time', None, unit='s', dimension='[time]'
            ),
            flow_rate=get_value_dynamically(
                data,
                'Gas quenching flow rate',
                None,
                unit='mL/s',
                dimension='[volume]/[time]',
            ),
            height=get_value_dynamically(
                data, 'Gas quenching height', None, unit='mm', dimension='[length]'
            ),
            duration=get_value_dynamically(
                data, 'Gas quenching duration', None, unit='s', dimension='[time]'
            ),
            pressure=get_value_dynamically(
                data, 'Gas quenching pressure', None, unit='bar', dimension='[pressure]'
            ),
            velocity=get_value_dynamically(
                data,
                'Gas quenching velocity',
                None,
                unit='m/s',
                dimension='[length]/[time]',
            ),
            nozzle_shape=get_value_dynamically(data, 'Nozzle shape', None, False),
            nozzle_size=get_value_dynamically(data, 'Nozzle size [mm²]', None, False),
            gas=get_value_dynamically(data, 'Gas', None, False),
        )

    material = get_value_dynamically(data, 'Material name', '', False)
    return (f'{i}_{j}_spin_coating_{material}', archive)


def map_sdc(i, j, lab_ids, data, upload_id, sdc_class):
    archive = sdc_class(
        name='slot die coating '
        + get_value_dynamically(data, 'Material name', '', False),
        location=get_value_dynamically(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value_dynamically(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=get_value(
                    data,
                    ['Solution volume [um]', 'Solution volume [uL]'],
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value_dynamically(
                    data,
                    'Viscosity',
                    None,
                    unit=['mPa*s'],
                    dimension='[viscosity]',
                ),
                solution_contact_angle=get_value_dynamically(
                    data,
                    'Contact angle',
                    None,
                    unit=['°'],
                    dimension='[angle]',
                ),
            )
        ],
        layer=map_layer(data),
        atmosphere=map_atmosphere(data),
        annealing=map_annealing(data),
        properties=SlotDieCoatingProperties(
            coating_run=get_value_dynamically(data, 'Coating run', None, False),
            flow_rate=get_value_dynamically(
                data,
                'Flow rate',
                None,
                unit='uL/minute',
                dimension='[volume]/[time]',
            ),
            slot_die_head_distance_to_thinfilm=get_value_dynamically(
                data, 'Head gap', unit='mm', dimension='[length]'
            ),
            slot_die_head_speed=get_value_dynamically(
                data, 'Speed', unit='mm/s', dimension='[length]/[time]'
            ),
            coated_area=get_value(data, 'Coated area [mm²]', unit='mm**2'),
        ),
        quenching=AirKnifeGasQuenching(
            air_knife_angle=get_value(data, 'Air knife angle [°]', None),
            # is this the same as (drying) gas flow rate/velocity?
            bead_volume=get_value_dynamically(
                data, 'Bead volume', None, unit='mm/s', dimension='[length]/[time]'
            ),
            drying_speed=get_value_dynamically(
                data,
                'Drying speed',
                None,
                unit='cm/minute',
                dimension='[length]/[time]',
            ),
            air_knife_distance_to_thin_film=get_value_dynamically(
                data, 'Air knife gap', None, unit='cm', dimension='[length]'
            ),
            drying_gas_temperature=get_value(
                data,
                ['Drying gas temperature [°]', 'Drying gas temperature [°C]'],
                None,
                unit=['°C', '°C'],
            ),
            heat_transfer_coefficient=get_value_dynamically(
                data,
                'Heat transfer coefficient',
                None,
                unit='W/(K*m**2)',
                dimension='[power]/[temperature]/[area]',
            ),
        ),
    )
    material = get_value_dynamically(data, 'Material name', '', False)
    return (f'{i}_{j}_slot_die_coating_{material}', archive)


def map_inkjet_printing(i, j, lab_ids, data, upload_id, inkjet_class):
    location = get_value_dynamically(data, 'Tool/GB name', '', False)
    archive = inkjet_class(
        name='inkjet printing '
        + get_value_dynamically(data, 'Material name', '', False),
        location=location,
        positon_in_experimental_plan=i,
        description=get_value_dynamically(data, 'Notes', None, False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        solution=[
            PrecursorSolution(
                solution_details=map_solutions(data),  # check unit
                # check unit
                solution_volume=get_value(
                    data,
                    [
                        'Solution volume [um]',
                        'Solution volume [uL]',
                    ],  # the um (wrong unit) is for parsing the typo in case of old excels
                    None,
                    unit=['uL', 'uL'],
                ),
                solution_viscosity=get_value_dynamically(
                    data,
                    'Viscosity',
                    None,
                    unit='mPa*s',
                    dimension='[viscosity]',
                ),
                solution_contact_angle=get_value_dynamically(
                    data,
                    'Contact angle',
                    None,
                    unit='°',
                    dimension='[angle]',
                ),
            )
        ],
        layer=map_layer(data),
        nozzle_voltage_profile=NozzleVoltageProfile(
            config_file=get_value_dynamically(
                data, 'Nozzle voltage config file', None, False
            )
        ),
        properties=InkjetPrintingProperties(
            printing_run=get_value_dynamically(data, 'Printing run', None, False),
            image_used=get_value_dynamically(data, 'Image used', None, False),
            print_head_properties=PrintHeadProperties(
                number_of_active_print_nozzles=get_value_dynamically(
                    data, 'Number of active nozzles', None
                ),
                active_nozzles=get_value_dynamically(
                    data, 'Active nozzles', None, False
                ),
                print_nozzle_drop_frequency=get_value_dynamically(
                    data,
                    'Droplet per second',
                    None,
                    unit='1/s',
                    dimension='[frequency]',
                ),
                print_head_angle=get_value_dynamically(
                    data, 'Print head angle', None, unit='deg', dimension='[angle]'
                ),
                print_speed=get_value_dynamically(
                    data,
                    'Printing speed',
                    None,
                    unit='mm/s',
                    dimension='[length]/[time]',
                ),
                print_nozzle_drop_volume=get_value_dynamically(
                    data,
                    'Droplet volume',
                    None,
                    unit='pL',
                    dimension='[volume]',
                ),
                print_head_temperature=get_value_dynamically(
                    data,
                    'Nozzle temperature',
                    None,
                    unit='°C',
                    dimension='[temperature]',
                ),
                print_head_distance_to_substrate=get_value_dynamically(
                    data, 'Dropping Height', None, unit='mm', dimension='[length]'
                ),
                print_head_name=get_value_dynamically(
                    data, 'Printhead name', None, False
                ),
            ),
            cartridge_pressure=get_value_dynamically(
                data,
                'Ink reservoir pressure',
                None,
                dimension='[pressure]',
            ),
            substrate_temperature=get_value_dynamically(
                data, 'Table temperature', None, unit='°C', dimension='[temperature]'
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
            quality_factor=get_value_dynamically(data, 'Quality factor', None, False),
            step_size=get_value_dynamically(data, 'Step size', None, False),
            directional=get_value_dynamically(data, 'Printing direction', None, False),
            swaths=get_value_dynamically(data, 'Number of swaths', None),
        ),
        atmosphere=map_atmosphere(data),
        annealing=map_annealing(data),
    )

    if get_value_dynamically(data, 'GAVD Gas', None, False):
        archive.quenching = GasFlowAssistedVacuumDrying(
            vacuum_properties=VacuumQuenching(
                start_time=get_value_dynamically(
                    data, 'GAVD start time', None, unit='s', dimension='[time]'
                ),
                pressure=get_value_dynamically(
                    data,
                    'GAVD vacuum pressure',
                    None,
                    unit='mbar',
                    dimension='[pressure]',
                ),
                temperature=get_value_dynamically(
                    data, 'GAVD temperature', None, unit='°C', dimension='[temperature]'
                ),
                duration=get_value_dynamically(
                    data, 'GAVD vacuum time', None, unit='s', dimension='[time]'
                ),
            ),
            gas_quenching_properties=GasQuenchingWithNozzle(
                duration=get_value_dynamically(
                    data, 'Gas flow duration', None, unit='s', dimension='[time]'
                ),
                pressure=get_value_dynamically(
                    data,
                    'Gas flow pressure',
                    None,
                    dimension='[pressure]',
                ),
                nozzle_shape=get_value_dynamically(data, 'Nozzle shape', None, False),
                nozzle_type=get_value_dynamically(data, 'Nozzle type', None, False),
                gas=get_value_dynamically(data, 'GAVD Gas', None, False),
            ),
            comment=get_value_dynamically(data, 'GAVD comment', None, False),
        )

    if location in ['Pixdro', 'iLPixdro']:  # printer param
        voltage_a = get_value_dynamically(
            data, 'Wf Level 1', None, unit='V', dimension='[voltage]'
        )
        voltage_b = get_value_dynamically(
            data, 'Wf Level 2', None, unit='V', dimension='[voltage]'
        )
        voltage_c = get_value_dynamically(
            data, 'Wf Level 3', None, unit='V', dimension='[voltage]'
        )
        archive.nozzle_voltage_profile = LP50NozzleVoltageProfile(
            number_of_pulses=get_value_dynamically(
                data, 'Wf Number of Pulses', None, False
            ),
            voltage_a=voltage_a,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_a=voltage_a
            / get_value_dynamically(
                data, 'Wf Rise 1', None, unit='V/us', dimension='[voltage]/[time]'
            )
            if voltage_a
            else None,
            peak_time_a=get_value_dynamically(
                data, 'Wf Width 1', None, unit='us', dimension='[time]'
            ),
            fall_edge_a=voltage_a
            / get_value_dynamically(
                data, 'Wf Fall 1', None, unit='V/us', dimension='[voltage]/[time]'
            )
            if voltage_a
            else None,
            time_space_a=get_value_dynamically(
                data, 'Wf Space 1', None, unit='us', dimension='[time]'
            ),
            voltage_b=voltage_b,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_b=voltage_b
            / get_value_dynamically(
                data, 'Wf Rise 2', None, unit='V/us', dimension='[voltage]/[time]'
            )
            if voltage_b
            else None,
            peak_time_b=get_value_dynamically(
                data, 'Wf Width 2', None, unit='us', dimension='[time]'
            ),
            fall_edge_b=voltage_b
            / get_value_dynamically(
                data, 'Wf Fall 2', None, unit='V/us', dimension='[voltage]/[time]'
            )
            if voltage_b
            else None,
            time_space_b=get_value_dynamically(
                data, 'Wf Space 2', None, unit='us', dimension='[time]'
            ),
            voltage_c=voltage_c,
            # umrechnen time [us] = V_level [V]/ rise[V/us]
            rise_edge_c=voltage_c
            / get_value_dynamically(
                data, 'Wf Rise 3', None, unit='V/us', dimension='[voltage]/[time]'
            )
            if voltage_c
            else None,
            peak_time_c=get_value_dynamically(
                data, 'Wf Width 3', None, unit='us', dimension='[time]'
            ),
            fall_edge_c=voltage_c
            / get_value_dynamically(
                data, 'Wf Fall 3', None, unit='V/us', dimension='[voltage]/[time]'
            )
            if voltage_c
            else None,
            time_space_c=get_value_dynamically(
                data, 'Wf Space 3', None, unit='us', dimension='[time]'
            ),
        )

    if location in ['iLNotion', 'Notion']:  # printer param
        archive.nozzle_voltage_profile = NotionNozzleVoltageProfile(
            number_of_pulses=get_value_dynamically(data, 'Wf Number of Pulses', None),
            # for loop over number of pulses with changing _a suffix of variales below
            delay_time_a=get_value_dynamically(
                data, 'Wf Delay Time', None, unit='us', dimension='[time]'
            ),
            rise_edge_a=get_value_dynamically(
                data, 'Wf Rise Time', None, unit='us', dimension='[time]'
            ),
            peak_time_a=get_value_dynamically(
                data, 'Wf Hold Time', None, unit='us', dimension='[time]'
            ),
            fall_edge_a=get_value_dynamically(
                data, 'Wf Fall Time', None, unit='us', dimension='[time]'
            ),
            time_space_a=get_value_dynamically(
                data, 'Wf Relax Time', None, unit='us', dimension='[time]'
            ),
            voltage_a=get_value_dynamically(
                data, 'Wf Voltage', None, unit='V', dimension='[voltage]'
            ),
            # multipulse_a=get_value(data, 'Wf Multipulse [1/0]', None, False),
            number_of_greylevels_a=get_value_dynamically(
                data, 'Wf Number Greylevels', None
            ),
            grey_level_0_pulse_a=get_value_dynamically(
                data, 'Wf Grey Level 0 Use Pulse [1/0]', None
            ),
            grey_level_1_pulse_a=get_value_dynamically(
                data, 'Wf Grey Level 1 Use Pulse [1/0]', None
            ),
        )
    material = get_value_dynamically(data, 'Material name', '', False)
    return (f'{i}_{j}_inkjet_printing_{material}', archive)


def map_cleaning(i, j, lab_ids, data, upload_id, cleaning_class):
    archive = cleaning_class(
        name='Cleaning',
        positon_in_experimental_plan=i,
        location=get_value_dynamically(data, 'Tool/GB name', '', False),
        description=get_value_dynamically(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        cleaning=[
            SolutionCleaning(
                time=get_value_dynamically(
                    data,
                    f'Time {i}',
                    None,
                    dimension='[time]',
                ),
                temperature=get_value_dynamically(
                    data, f'Temperature {i}', None, unit='°C', dimension='[temperature]'
                ),
                solvent_2=PubChemPureSubstanceSectionCustom(
                    name=get_value(data, f'Solvent {i}', None, False), load_data=False
                ),
            )
            for i in range(10)
            if get_value_dynamically(data, f'Solvent {i}', None, False)
        ],
        cleaning_uv=[
            UVCleaning(
                time=get_value_dynamically(
                    data,
                    'UV-Ozone Time',
                    None,
                    dimension='[time]',
                )
            )
        ],
        cleaning_plasma=[
            PlasmaCleaning(
                time=get_value_dynamically(
                    data,
                    'Gas-Plasma Time',
                    None,
                    dimension='[time]',
                ),
                power=get_value_dynamically(
                    data, 'Gas-Plasma Power', None, unit='W', dimension='[power]'
                ),
                plasma_type=get_value_dynamically(data, 'Gas-Plasma Gas', None, False),
            )
        ],
    )
    return (f'{i}_{j}_cleaning', archive)


def map_substrate(data, substrate_class):
    # Create LayerProperties for substrate_properties
    substrate_props = [
        LayerProperties(
            layer_thickness=get_value_dynamically(
                data, 'TCO thickness', None, unit='nm', dimension='[length]'
            ),
            layer_transmission=get_value_dynamically(data, 'Transmission [%]', None),
            layer_sheet_resistance=get_value(
                data, 'Sheet Resistance [Ohms/square]', None, unit=['ohm']
            ),
            layer_type='Substrate Conductive Layer',
            layer_material_name=get_value_dynamically(
                data, 'Substrate conductive layer', '', False
            ),
        )
    ]
    archive = substrate_class(
        datetime=get_datetime(data, 'Date'),
        name='Substrate '
        + get_value_dynamically(data, 'Sample dimension', '', False)
        + ' '
        + get_value_dynamically(data, 'Substrate material', '', False)
        + ' '
        + get_value_dynamically(data, 'Substrate conductive layer', '', False),
        solar_cell_area=get_value_dynamically(
            data, 'Sample area', None, unit='cm**2', dimension='[area]'
        ),
        pixel_area=get_value_dynamically(
            data, 'Pixel area', None, unit='cm**2', dimension='[area]'
        ),
        number_of_pixels=get_value_dynamically(data, 'Number of pixels', None),
        substrate=get_value_dynamically(data, 'Substrate material', '', False),
        description=get_value_dynamically(data, 'Notes', '', False),
        lab_id=get_value_dynamically(data, 'Bottom Cell Name', '', False),
        conducting_material=[
            get_value_dynamically(data, 'Substrate conductive layer', '', False)
        ],
        substrate_properties=substrate_props,
    )
    return archive


def map_evaporation(
    i, j, lab_ids, data, upload_id, evaporation_class, coevaporation=False
):
    material = get_value_dynamically(data, 'Material name', '', False)
    file_name = (
        f'{i}_{j}_coevaporation_{material}'
        if coevaporation
        else f'{i}_{j}_evaporation_{material}'
    )
    archive = evaporation_class(
        name='evaporation ' + get_value_dynamically(data, 'Material name', '', False),
        location=get_value_dynamically(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
        description=get_value_dynamically(data, 'Notes', '', False),
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
            if (
                get_value_dynamically(
                    data, 'Temperature', None, unit='°C', dimension='[temperature]'
                )
                is not None
            ):
                evaporation.temparature = [
                    get_value_dynamically(
                        data, 'Temperature', None, unit='°C', dimension='[temperature]'
                    ),
                ] * 2

        if not evaporation:
            return (file_name, archive)

        if (
            get_value_dynamically(
                data,
                f'Source temperature start{mat}',
                None,
                unit='°C',
                dimension='[temperature]',
            )
            is not None
            and get_value_dynamically(
                data,
                f'Source temperature end{mat}',
                None,
                unit='°C',
                dimension='[temperature]',
            )
            is not None
        ):
            evaporation.temparature = [
                get_value_dynamically(
                    data,
                    f'Source temperature start{mat}',
                    None,
                    unit='°C',
                    dimension='[temperature]',
                ),
                get_value_dynamically(
                    data,
                    f'Source temperature end{mat}',
                    None,
                    unit='°C',
                    dimension='[temperature]',
                ),
            ]

        evaporation.thickness = get_value_dynamically(
            data, f'Thickness{mat}', unit='nm', dimension='[length]'
        )
        evaporation.start_rate = get_value_dynamically(
            data, f'Rate start{mat}', unit='angstrom/s', dimension='[length]/[time]'
        )
        evaporation.target_rate = get_value_dynamically(
            data,
            [f'Rate{mat}', f'Rate target{mat}'],
            unit='angstrom/s',
            dimension='[length]/[time]',
        )
        evaporation.substrate_temparature = get_value_dynamically(
            data, f'Substrate temperature{mat}', unit='°C', dimension='[temperature]'
        )
        evaporation.pressure = get_value_dynamically(
            data,
            f'Base pressure{mat}',
            None,
            dimension='[pressure]',
        )
        evaporation.pressure_start = get_value_dynamically(
            data,
            f'Pressure start{mat}',
            None,
            dimension='[pressure]',
        )
        evaporation.pressure_end = get_value_dynamically(
            data,
            f'Pressure end{mat}',
            None,
            dimension='[pressure]',
        )
        evaporation.tooling_factor = get_value_dynamically(data, f'Tooling factor{mat}')

        evaporation.chemical_2 = PubChemPureSubstanceSectionCustom(
            name=get_value_dynamically(data, f'Material name{mat}', None, False),
            load_data=False,
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
        location=get_value_dynamically(data, 'Tool/GB name', '', False),
        description=get_value_dynamically(data, 'Notes', '', False),
        samples=[
            CompositeSystemReference(
                reference=get_reference(upload_id, f'{lab_id}.archive.json'),
                lab_id=lab_id,
            )
            for lab_id in lab_ids
        ],
        annealing=map_annealing(data),
        atmosphere=Atmosphere(
            relative_humidity=get_value_dynamically(
                data, 'Relative humidity [%]', None
            ),
        ),
    )
    return (f'{i}_{j}_annealing', archive)


def map_sputtering(i, j, lab_ids, data, upload_id, sputter_class):
    archive = sputter_class(
        name='sputtering ' + get_value_dynamically(data, 'Material name', '', False),
        positon_in_experimental_plan=i,
        location=get_value_dynamically(data, 'Tool/GB name', '', False),
        description=get_value_dynamically(data, 'Notes', '', False),
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
        thickness=get_value_dynamically(
            data, 'Thickness', unit='nm', dimension='[length]'
        ),
        gas_flow_rate=get_value_dynamically(
            data, 'Gas flow rate', unit='cm**3/minute', dimension='[volume]/[time]'
        ),
        rotation_rate=get_value_dynamically(
            data, 'Rotation rate', dimension='[frequency]'
        ),
        power=get_value_dynamically(data, 'Power', unit='W', dimension='[power]'),
        temperature=get_value_dynamically(
            data, 'Temperature', unit='°C', dimension='[temperature]'
        ),
        deposition_time=get_value_dynamically(
            data, 'Deposition time', unit='s', dimension='[time]'
        ),
        burn_in_time=get_value_dynamically(
            data, 'Burn in time', unit='s', dimension='[time]'
        ),
        pressure=get_value_dynamically(
            data, 'Pressure', unit='mbar', dimension='[pressure]'
        ),
        target_2=PubChemPureSubstanceSectionCustom(
            name=get_value_dynamically(data, 'Material name', None, False),
            load_data=False,
        ),
        gas_2=PubChemPureSubstanceSectionCustom(
            name=get_value_dynamically(data, 'Gas', None, False), load_data=False
        ),
    )
    archive.processes = [process]
    material = get_value_dynamically(data, 'Material name', '', False)
    return (f'{i}_{j}_sputtering_{material}', archive)


def map_close_space_sublimation(i, j, lab_ids, data, upload_id, css_class):
    material = get_value(data, 'Material name', '', False)
    archive = css_class(
        name='Close Space Sublimation ' + get_value(data, 'Material name', '', False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
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
                solution_details=map_solutions(data),  # check unit
                # check unit
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
        ),
    )

    return (f'{i}_{j}_laser_scribing', archive)


def map_atomic_layer_deposition(i, j, lab_ids, data, upload_id, ald_class):
    archive = ald_class(
        name='atomic layer deposition '
        + get_value(data, 'Material name', '', number=False),
        location=get_value(data, 'Tool/GB name', '', False),
        positon_in_experimental_plan=i,
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
    return (f'{i}_{j}_generic_process_{name.replace(" ", "_")}', archive)
    return (f'{i}_{j}_generic_process_{name.replace(" ", "_")}', archive)
    return (f'{i}_{j}_generic_process_{name.replace(" ", "_")}', archive)
