import pandas as pd


def get_mpp_hysprint_samples(entry_self, data):
    from baseclasses.solar_energy import JVData, PixelData, SampleData

    samples = []
    for sample_idx, sample in enumerate(data['samples']):
        df = sample['data']
        sample_entry = SampleData()
        if entry_self.samples is not None and len(entry_self.samples) == len(
            data['samples']
        ):
            sample_entry = entry_self.samples[sample_idx]

        sample_entry.name = f"Sample {sample['id']} (in Box)"
        sample_entry.time = df.groupby(
            pd.Grouper(
                key='Timestamp', freq=f'{entry_self.averaging_grouping_minutes}Min'
            )
        )['Duration_h'].mean()
        sample_entry.temperature = df.groupby(
            pd.Grouper(
                key='Timestamp', freq=f'{entry_self.averaging_grouping_minutes}Min'
            )
        )['InTemperatur'].mean()
        sample_entry.radiation = df.groupby(
            pd.Grouper(
                key='Timestamp', freq=f'{entry_self.averaging_grouping_minutes}Min'
            )
        )['InEinstrahlung'].mean()

        pixels = []
        for pixel_idx, pixel in enumerate(sample['pixels']):
            df = pixel['data']
            pixel_entry = PixelData()
            if sample_entry.pixels is not None and len(sample_entry.pixels) == len(
                sample['pixels']
            ):
                pixel_entry = sample_entry.pixels[pixel_idx]
            pixel_entry.name = f"Pixel {pixel['id']}"
            df_tmp = (
                df[['Timestamp', 'Duration_h', 'MPPT_V', 'MPPT_EFF', 'MPPT_J']]
                .groupby(
                    pd.Grouper(
                        key='Timestamp',
                        freq=f'{entry_self.averaging_grouping_minutes}Min',
                    )
                )
                .mean()
            )
            pixel_entry.time = df_tmp['Duration_h']
            pixel_entry.voltage = df_tmp['MPPT_V']
            pixel_entry.efficiency = df_tmp['MPPT_EFF'] / entry_self.pixel_area
            pixel_entry.current_density = df_tmp['MPPT_J'] / entry_self.pixel_area

            jvs = []
            for scan_direction in ['data_jv_for', 'data_jv_rev']:
                df = pixel[scan_direction]
                jv_entry = JVData(
                    name=scan_direction[-3:],
                    time=df['Duration_h'],
                    efficiency=df['n'],
                    v_oc=df['V_oc'],
                    j_sc=df['J_sc'] / entry_self.pixel_area,
                    fill_factor=df['FF'],
                )
                jvs.append(jv_entry)
            pixel_entry.jv_data = jvs
            pixels.append(pixel_entry)
        sample_entry.pixels = pixels
        samples.append(sample_entry)
    return samples
