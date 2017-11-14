from db.base.models import Satellite, Transmitter, Mode, DemodData


def calculate_statistics():
    """View to create statistics endpoint."""
    satellites = Satellite.objects.all()
    transmitters = Transmitter.objects.all()
    modes = Mode.objects.all()

    total_satellites = satellites.count()
    total_transmitters = transmitters.count()
    total_data = DemodData.objects.all().count()
    alive_transmitters = transmitters.filter(alive=True).count()
    alive_transmitters_percentage = '{0}%'.format(round((float(alive_transmitters) /
                                                         float(total_transmitters)) * 100, 2))

    mode_label = []
    mode_data = []
    for mode in modes:
        tr = transmitters.filter(mode=mode).count()
        mode_label.append(mode.name)
        mode_data.append(tr)

    band_label = []
    band_data = []

    # <30.000.000 - HF
    filtered = transmitters.filter(downlink_low__lt=30000000).count()
    band_label.append('HF')
    band_data.append(filtered)

    # 30.000.000 ~ 300.000.000 - VHF
    filtered = transmitters.filter(downlink_low__gte=30000000,
                                   downlink_low__lt=300000000).count()
    band_label.append('VHF')
    band_data.append(filtered)

    # 300.000.000 ~ 1.000.000.000 - UHF
    filtered = transmitters.filter(downlink_low__gte=300000000,
                                   downlink_low__lt=1000000000).count()
    band_label.append('UHF')
    band_data.append(filtered)

    # 1G ~ 2G - L
    filtered = transmitters.filter(downlink_low__gte=1000000000,
                                   downlink_low__lt=2000000000).count()
    band_label.append('L')
    band_data.append(filtered)

    # 2G ~ 4G - S
    filtered = transmitters.filter(downlink_low__gte=2000000000,
                                   downlink_low__lt=4000000000).count()
    band_label.append('S')
    band_data.append(filtered)

    # 4G ~ 8G - C
    filtered = transmitters.filter(downlink_low__gte=4000000000,
                                   downlink_low__lt=8000000000).count()
    band_label.append('C')
    band_data.append(filtered)

    # 8G ~ 12G - X
    filtered = transmitters.filter(downlink_low__gte=8000000000,
                                   downlink_low__lt=12000000000).count()
    band_label.append('X')
    band_data.append(filtered)

    # 12G ~ 18G - Ku
    filtered = transmitters.filter(downlink_low__gte=12000000000,
                                   downlink_low__lt=18000000000).count()
    band_label.append('Ku')
    band_data.append(filtered)

    # 18G ~ 27G - K
    filtered = transmitters.filter(downlink_low__gte=18000000000,
                                   downlink_low__lt=27000000000).count()
    band_label.append('K')
    band_data.append(filtered)

    # 27G ~ 40G - Ka
    filtered = transmitters.filter(downlink_low__gte=27000000000,
                                   downlink_low__lt=40000000000).count()
    band_label.append('Ka')
    band_data.append(filtered)

    mode_data_sorted, mode_label_sorted = zip(*sorted(zip(mode_data, mode_label), reverse=True))
    band_data_sorted, band_label_sorted = zip(*sorted(zip(band_data, band_label), reverse=True))

    statistics = {
        'total_satellites': total_satellites,
        'total_data': total_data,
        'transmitters': total_transmitters,
        'transmitters_alive': alive_transmitters_percentage,
        'mode_label': mode_label_sorted,
        'mode_data': mode_data_sorted,
        'band_label': band_label_sorted,
        'band_data': band_data_sorted
    }
    return statistics
