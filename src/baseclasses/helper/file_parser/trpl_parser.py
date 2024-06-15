def get_trpl_measurement(file_obj):

    bin_line = -1
    count_line = -1
    counts = []
    time = []
    for l_idx, raw_line in enumerate(file_obj):
        line = raw_line.strip()
        if line.startswith("#ns/bin"):
            bin_line = l_idx + 1
        if l_idx == bin_line:
            ns_per_bin = float(line)
        if line.startswith("#counts"):
            count_line = l_idx + 1
        if l_idx >= count_line and count_line >= 0:
            counts.append(float(line))
            time.append(
                float(
                    (l_idx + 1 - count_line)
                    * ns_per_bin) if ns_per_bin > 0 else float(
                    (l_idx + 1 - count_line)))
    return {"counts": counts, "time": time, "ns_per_bin": ns_per_bin}
