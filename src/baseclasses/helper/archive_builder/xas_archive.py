from datetime import datetime


def get_xas_archive(data, dateline, entry_class):
    if dateline is not None:
        datetime_object = datetime.strptime(dateline, '#D\t%a %b %d\t%H:%M:%S\t%Y')
        entry_class.datetime = datetime_object.strftime('%Y-%m-%d %H:%M:%S.%f')

    entry_class.energy = data['#monoE']
    entry_class.seconds = data['Seconds']
    entry_class.k0 = data['K0']
    entry_class.k1 = data['K1']
    entry_class.k3 = data['K3']
