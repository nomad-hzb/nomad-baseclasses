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

import re
import string

import numpy as np
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.metainfo import MEnum, Quantity, Section, SubSection

from .. import BaseMeasurement
from ..helper.add_solar_cell import add_solar_cell
from ..helper.naming_normalizer import scan_direction_normalizer

# Curve names arriving from different instruments/parsers use wildly different
# conventions for the same information, e.g. 'Pixel_1_forward', 'b_rev',
# 'a_Forward_Dark', '958.1a_loc2_forward.txt'. parse_jv_curve_name extracts a
# normalized pixel_id ('pixel_<n>') and scan_direction ('forward'/'reverse')
# from cell_name so curves can be queried/tagged consistently regardless of
# which plugin/parser produced them, without requiring every parser to be
# updated. Formatting artifacts inserted by our own parsers (not instrument
# data) are skipped when hunting for the pixel token near a direction word.
_JV_NAME_FILLER_TOKENS = {
    'loc1',
    'loc2',
    'loc3',
    'txt',
    'jv',
    'csv',
    'iv',
    'dark',
    'light',
}
_JV_PIXEL_FUSED_RE = re.compile(r'(?:pixel|px|p)(\d{1,2})$')
_LETTER_TO_PIXEL_NUMBER = {c: str(i + 1) for i, c in enumerate(string.ascii_lowercase)}


def _match_explicit_pixel_token(token, prev_token):
    # 'Pixel1'/'P1' fused, or 'Pixel'/'1' as separate tokens - safe to
    # recognize unconditionally, no direction anchor needed: the literal
    # word 'pixel'/'px'/'p' rarely appears by accident.
    low = token.lower()
    fused = _JV_PIXEL_FUSED_RE.fullmatch(low)
    if fused:
        return f'pixel_{fused.group(1)}'
    if re.fullmatch(r'\d{1,2}', low) and prev_token and prev_token.lower() in (
        'pixel',
        'px',
        'p',
    ):
        return f'pixel_{low}'
    return None


def _match_jv_pixel_token(token, prev_token):
    # Like _match_explicit_pixel_token, plus a bare single letter - only
    # safe when anchored next to a confirmed direction token (see caller),
    # since a lone letter is otherwise too likely to be incidental.
    explicit = _match_explicit_pixel_token(token, prev_token)
    if explicit:
        return explicit
    if re.fullmatch(r'[a-z]', token.lower()):
        return f'pixel_{_LETTER_TO_PIXEL_NUMBER[token.lower()]}'
    return None


def parse_jv_curve_name(name):
    """
    Derive (pixel_id, scan_direction) from a free-text JV curve name. Returns
    (None, None) parts whenever they can't be determined with confidence -
    never guesses a value that isn't backed by a recognizable pattern.
    """
    if not name:
        return None, None
    tokens = [t for t in re.split(r'[\s_.\-]+', name) if t]

    direction = None
    direction_idx = None
    for i, token in enumerate(tokens):
        normalized = scan_direction_normalizer.normalize(token)
        if normalized in ('forward', 'reverse'):
            direction, direction_idx = normalized, i
            break

    pixel_id = None
    if direction_idx is not None:
        # Walk backward from the direction token, skipping known filler
        # tokens, and try the first real token as the pixel candidate.
        j = direction_idx - 1
        while j >= 0 and tokens[j].lower() in _JV_NAME_FILLER_TOKENS:
            j -= 1
        if j >= 0:
            prev_token = tokens[j - 1] if j - 1 >= 0 else None
            pixel_id = _match_jv_pixel_token(tokens[j], prev_token)

    if pixel_id is None:
        # Unconditional fallback: only the explicit 'pixel'/'px'/'p' + digit
        # pattern is safe without a direction anchor nearby - a bare letter
        # alone is too likely to be incidental (sample ids, dates, ...).
        for i, token in enumerate(tokens):
            prev_token = tokens[i - 1] if i - 1 >= 0 else None
            pixel_id = _match_explicit_pixel_token(token, prev_token)
            if pixel_id:
                break

    return pixel_id, direction


class SolarCellJV(PlotSection):
    m_def = Section(
        label_quantity='cell_name',
        a_plotly_graph_object=[
            {'data': {'x': '#voltage', 'y': '#current_density'}},
            {'data': {'x': '#voltage', 'y': '#current_density'}},
        ],
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    certified_values = Quantity(
        type=bool,
        shape=[],
        description="""
            TRUE if the IV data is measured by an independent and certification 
            institute.
            If your solar simulator is calibrated by a calibrated reference diode,
            that does not count as a certified result.
        """,
        a_eln=dict(component='BoolEditQuantity'),
    )

    certification_institute = Quantity(
        type=str,
        shape=[],
        description="""
            The name of the certification institute that has measured the certified 
            device.
            Example:
            Newport
            NIM, National Institute of Metrology of China
            KIER, Korea Institute of Energy Research
        """,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(
                suggestions=sorted(
                    [
                        'National Institute ofMetrology, China',
                        'Quality supervision＆Testing Center of Chemical＆Physical Power Sources of Information Industry',  # noqa E501
                        'CREST, Photovoltaic Meaasurement and calibration Laboratory at Universit of Loughborough',  # noqa E501
                        'Photovoltaic and Wind Power Systems Quality Test Center, Chinese Academy of Sciences',  # noqa E501
                        'NREL',
                        'Institute of Metrology (NIM) of China',
                        'PVEVL, National Central University, Taiwan',
                        'NIM, National Institute of Metrology of China',
                        'Fraunhofer ISE',
                        'SIMIT, Shanghai Institute of Microsystem and Information Technology',  # noqa E501
                        'Newport',
                        'CSIRO, PV Performance Lab at Monash University',
                        'AIST, National Institute of Advanced Industrial Science and Technology',  # noqa E501
                        'CPVT, National Center of Supervision and Inspection on Solar Photovoltaic Products Quality of China',  # noqa E501
                        'KIER, Korea Institute of Energy Research',
                        'Newport Corporation',
                        'Solar Power Lab at Arizona State University',
                    ]
                )
            ),
        ),
    )

    light_intensity = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001129',
            'https://purl.archive.org/tfsco/TFSCO_00002034',
        ],
        type=np.dtype(np.float64),
        unit=('mW/cm**2'),
        shape=[],
        default=100.0,
        description="""
            The light intensity during the IV measurement
            - If there are uncertainties, only state the best estimate, e.g. write
            100 and not 90-100.
            - Standard AM 1.5 illumination correspond to 100 mW/cm2
            - If you need to convert from illumination given in lux; at 550 nm, 
            1 mW/cm2 corresponds to 6830 lux. Be aware that the conversion change
            with the spectrum used. As a rule of thumb for general fluorescent/LED
            light sources, around 0.31mW corresponded to 1000 lux. If your light
            intensity is measured in lux, it probably means that your light spectra
            deviates quite a lot from AM 1.5, wherefore it is very important that you
            also specify the light spectra in the next column.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    open_circuit_voltage = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001034',
            'https://purl.archive.org/tfsco/TFSCO_00002063',
        ],
        type=np.dtype(np.float64),
        unit='V',
        shape=[],
        description="""
            Open circuit voltage.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    short_circuit_current_density = Quantity(
        type=np.dtype(np.float64),
        unit='mA / cm**2',
        shape=[],
        description="""
            Short circuit current density.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    fill_factor = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001107',
            'https://purl.archive.org/tfsco/TFSCO_00002050',
        ],
        type=np.dtype(np.float64),
        shape=[],
        description="""
            Fill factor.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    efficiency = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001037'],
        type=np.dtype(np.float64),
        shape=[],
        description="""
            Power conversion efficiency.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    potential_at_maximum_power_point = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001106',
            'https://purl.archive.org/tfsco/TFSCO_00002064',
        ],
        type=np.dtype(np.float64),
        unit='V',
        shape=[],
        description="""
            The potential at the maximum power point, Vmp.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    current_density_at_maximun_power_point = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001105',
            'https://purl.archive.org/tfsco/TFSCO_00005061',
        ],
        type=np.dtype(np.float64),
        unit='mA / cm**2',
        shape=[],
        description="""
            The current density at the maximum power point, *Jmp*.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    series_resistance = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001104',
            'https://purl.archive.org/tfsco/TFSCO_00002100',
        ],
        type=np.dtype(np.float64),
        unit='ohm*cm**2',
        shape=[],
        description="""
            The series resistance as extracted from the *J-V* curve.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    shunt_resistance = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001103',
            'https://purl.archive.org/tfsco/TFSCO_00002099',
        ],
        type=np.dtype(np.float64),
        unit='ohm*cm**2',
        shape=[],
        description="""
            The shunt resistance as extracted from the *J-V* curve.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    def derive_n_values(self):
        if self.current_density is not None:
            return len(self.current_density)
        if self.voltage is not None:
            return len(self.voltage)
        else:
            return 0

    n_values = Quantity(type=int, derived=derive_n_values)

    def update_results(self, archive):
        if self.open_circuit_voltage is not None:
            archive.results.properties.optoelectronic.solar_cell.open_circuit_voltage = self.open_circuit_voltage
        if self.short_circuit_current_density is not None:
            archive.results.properties.optoelectronic.solar_cell.short_circuit_current_density = self.short_circuit_current_density
        if self.fill_factor is not None:
            archive.results.properties.optoelectronic.solar_cell.fill_factor = (
                self.fill_factor
            )
        if self.efficiency is not None:
            archive.results.properties.optoelectronic.solar_cell.efficiency = (
                self.efficiency
            )
        if self.light_intensity is not None:
            archive.results.properties.optoelectronic.solar_cell.illumination_intensity = self.light_intensity

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        add_solar_cell(archive)
        self.update_results(archive)


class SolarCellJVCurve(SolarCellJV):
    def cell_params(self):
        """
        Calculates basic solar cell parametes form a current density (mA/cm**2)
        voltage (V) curve.

        Returns:
            Voc (V) open circuit voltage
            Jsc (mA/cm**2) short circuit current density
            FF fill factor in absolute values (0-1)
            efficiency power conversion efficiency in percentage (0-100)
        """
        from scipy import interpolate

        j_v_interpolated = interpolate.interp1d(self.current_density, self.voltage)
        Voc = j_v_interpolated(0).item()
        v_j_interpolated = interpolate.interp1d(self.voltage, self.current_density)
        Isc = v_j_interpolated(0).item()
        if Isc >= 0:
            idx = np.argmax(self.voltage * self.current_density)
        else:
            idx = np.argmin(self.voltage * self.current_density)
        Vmp = self.voltage[idx]
        Imp = self.current_density[idx]
        Isc = abs(Isc)
        FF = abs(Vmp.magnitude * Imp.magnitude / (Voc * Isc))
        efficiency = Voc * FF * Isc
        return Voc, Isc, FF, efficiency

    cell_name = Quantity(
        type=str,
        shape=[],
        description='Cell identification name.',
        a_eln=dict(component='StringEditQuantity'),
    )

    pixel_id = Quantity(
        type=str,
        shape=[],
        description=(
            'Normalized pixel identifier ("pixel_<n>"), auto-derived from '
            'cell_name during normalization regardless of which plugin/parser '
            'produced it - see parse_jv_curve_name(). Left unset when cell_name '
            "doesn't contain a recognizable pixel pattern, or when this curve "
            'is the only one in its measurement (nothing to disambiguate).'
        ),
    )

    scan_direction = Quantity(
        type=MEnum('forward', 'reverse'),
        shape=[],
        description=(
            'Scan direction, auto-derived from cell_name during normalization - '
            'see parse_jv_curve_name(). Left unset when cell_name does not '
            'contain a recognizable forward/reverse token.'
        ),
    )

    current_density = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00000064',
            'https://purl.archive.org/tfsco/TFSCO_00005061',
        ],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='mA/cm^2',
        description='Current density array of the *JV* curve.',
    )

    voltage = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001464',
            'https://purl.archive.org/tfsco/TFSCO_00005005',
        ],
        type=np.dtype(np.float64),
        shape=['n_values'],
        unit='V',
        description='Voltage array of the of the *JV* curve.',
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        parsed_pixel_id, parsed_direction = parse_jv_curve_name(self.cell_name)
        if self.pixel_id is None:
            self.pixel_id = parsed_pixel_id
        if self.scan_direction is None:
            self.scan_direction = parsed_direction
        if (
            self.current_density is not None
            and self.efficiency is None
            and not self.dark
        ):
            if self.voltage is not None:
                (
                    self.open_circuit_voltage,
                    self.short_circuit_current_density,
                    self.fill_factor,
                    self.efficiency,
                ) = self.cell_params()
                self.update_results(archive)


class SolarCellJVCurveCustom(SolarCellJVCurve):
    m_def = Section(
        label_quantity='cell_name',
        a_eln=dict(hide=['data_file', 'certified_values', 'certification_institute']),
    )

    dark = Quantity(type=bool, default=False, a_eln=dict(component='BoolEditQuantity'))


class SolarCellJVCurveDarkCustom(SolarCellJVCurveCustom):
    m_def = Section(
        label_quantity='cell_name',
        a_eln=dict(
            hide=[
                'data_file',
                'certified_values',
                'certification_institute',
                'light_intensity',
                'open_circuit_voltage',
                'short_circuit_current_density',
                'fill_factor',
                'efficiency',
                'potential_at_maximum_power_point',
                'current_density_at_maximun_power_point',
                'series_resistance',
                'shunt_resistance',
            ]
        ),
    )


class JVMeasurement(BaseMeasurement):
    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00000088'],
        label_quantity='data_file',
        validate=False,
    )

    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'),
    )

    active_area = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00001004',
            'https://purl.archive.org/tfsco/TFSCO_00002097',
        ],
        type=np.dtype(np.float64),
        unit=('cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='cm^2',
            props=dict(minValue=0),
        ),
    )

    intensity = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00001128'],
        type=np.dtype(np.float64),
        unit=('mW/cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mW/cm^2',
            props=dict(minValue=0),
        ),
    )

    integration_time = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002076',
            'https://purl.archive.org/tfsco/TFSCO_00002093',
        ],
        type=np.dtype(np.float64),
        unit=('ms'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ms',
            props=dict(minValue=0),
        ),
    )

    settling_time = Quantity(
        links=[
            'https://purl.archive.org/tfsco/TFSCO_00002077',
            'https://purl.archive.org/tfsco/TFSCO_00002092',
        ],
        type=np.dtype(np.float64),
        unit=('ms'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ms',
            props=dict(minValue=0),
        ),
    )

    averaging = Quantity(
        type=np.dtype(np.float64), shape=[], a_eln=dict(component='NumberEditQuantity')
    )

    compliance = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002078'],
        type=np.dtype(np.float64),
        unit=('mA/cm^2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mA/cm^2',
            props=dict(minValue=0),
        ),
    )

    jv_curve = SubSection(
        links=['http://purl.obolibrary.org/obo/OBI_0000299'],
        section_def=SolarCellJVCurveCustom,
        repeats=True,
        label_quantity='cell_name',
    )

    def normalize(self, archive, logger):
        self.method = 'JV Measurement'
        super().normalize(archive, logger)

        if len(self.jv_curve) == 1:
            # pixel_id exists to disambiguate between multiple pixels in one
            # measurement - meaningless (and, for messy filename-derived
            # names, riskier to guess) when there's only one curve.
            self.jv_curve[0].pixel_id = None

        max_idx = -1
        eff = -1
        for i, curve in enumerate(self.jv_curve):
            if (
                curve.efficiency is not None
                and curve.efficiency > eff
                and not curve.dark
            ):
                eff = curve.efficiency
                max_idx = i
        if max_idx >= 0:
            add_solar_cell(archive)
            solar_cell = archive.results.properties.optoelectronic.solar_cell
            solar_cell.open_circuit_voltage = self.jv_curve[
                max_idx
            ].open_circuit_voltage
            solar_cell.short_circuit_current_density = self.jv_curve[
                max_idx
            ].short_circuit_current_density
            solar_cell.fill_factor = self.jv_curve[max_idx].fill_factor
            solar_cell.efficiency = self.jv_curve[max_idx].efficiency
            solar_cell.illumination_intensity = self.jv_curve[max_idx].light_intensity

        self.reprocess_connected_samples(archive, logger)

    def reprocess_connected_samples(self, archive, logger):
        """
        Samples derive cached fields (e.g. best efficiency, jv_history_*) from all
        JV measurements that reference them, but only recompute those fields when the
        sample itself is (re)processed. Without this, editing/reprocessing a JV
        measurement after its sample was last processed leaves the sample stale
        until someone manually reprocesses it. Touch each connected sample's raw
        file so it gets queued for reprocessing too.
        """
        if not self.samples:
            return
        for sample_ref in self.samples:
            lab_id = getattr(sample_ref, 'lab_id', None)
            if not lab_id:
                continue
            file_name = f'{lab_id}.archive.json'
            try:
                if archive.m_context.raw_path_exists(file_name):
                    archive.m_context.process_updated_raw_file(
                        file_name, allow_modify=True
                    )
            except Exception:
                if logger:
                    logger.debug(
                        'Could not trigger reprocessing of connected sample.',
                        exc_info=True,
                    )
