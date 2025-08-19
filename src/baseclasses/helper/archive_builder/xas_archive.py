from datetime import datetime

from baseclasses.characterizations.xas import SiliconDriftDetector


def get_xas_archive(data, dateline, entry_class):
    if dateline is not None:
        if dateline.startswith('#D'):
            datetime_object = datetime.strptime(dateline, '#D\t%a %b %d\t%H:%M:%S\t%Y')
        elif dateline.startswith('# start_time:'):
            datetime_object = datetime.strptime(
                dateline, '# start_time: %Y-%m-%d %H:%M:%S.%f'
            )
        else:
            raise ValueError('Unknown Date format')
        entry_class.datetime = datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')

    entry_class.energy = (
        data['#monoE']
        if '#monoE' in data.columns
        else data['mono_eV'] / 1000
        if 'mono_eV' in data.columns
        else data['monoE_eV'] / 1000
        if 'monoE_eV' in data.columns
        else None
    )
    entry_class.seconds = (
        data['Seconds']
        if 'Seconds' in data.columns
        else data['time_ms'] / 1000
        if 'time_ms' in data.columns
        else None
    )
    entry_class.k0 = (
        data['K0']
        if 'K0' in data.columns
        else data['I0_A']
        if 'I0_A' in data.columns
        else None
    )
    entry_class.k1 = (
        data['K1']
        if 'K1' in data.columns
        else data['I1_A']
        if 'I1_A' in data.columns
        else None
    )
    entry_class.k3 = (
        data['K3']
        if 'K3' in data.columns
        else data['I2_A']
        if 'I2_A' in data.columns
        else None
    )

    kmc3_data = []

    for index in range(0, 13):
        kmc3_data.append(
            SiliconDriftDetector(
                fluo=data.get(f'fluo.{index}'),
                icr=data.get(f'ICR.{index}'),
                ocr=data.get(f'OCR.{index}'),
                tlt=data.get(f'TLT.{index}'),
                lt=data.get(f'LT.{index}'),
                rt=data.get(f'RT.{index}'),
            )
        )
    entry_class.sdd_parameters = kmc3_data
