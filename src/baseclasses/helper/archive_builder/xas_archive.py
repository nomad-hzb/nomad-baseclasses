from datetime import datetime

from baseclasses.characterizations.xas import SiliconDriftDetector


def get_xas_archive(data, dateline, entry_class):
    if dateline is not None:
        datetime_object = datetime.strptime(dateline, '#D\t%a %b %d\t%H:%M:%S\t%Y')
        entry_class.datetime = datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')

    entry_class.energy = data.get('#monoE')
    entry_class.seconds = data.get('Seconds')
    entry_class.k0 = data.get('K0')
    entry_class.k1 = data.get('K1')
    entry_class.k3 = data.get('K3')

    kmc3_data = []
    for index in range(1, 14):
        kmc3_data.append(
            SiliconDriftDetector(
                fluo=data.get(f'fluo{index}'),
                icr=data.get(f'icr{index}'),
                ocr=data.get(f'ocr{index}'),
                tlt=data.get(f'tlt{index}'),
                lt=data.get(f'lt{index}'),
                rt=data.get(f'rt{index}'),
            )
        )
    entry_class.sdd_parameters = kmc3_data
