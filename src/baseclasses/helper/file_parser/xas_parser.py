import pandas as pd


def getHeader(file):
    header = 0
    date_line_found = False
    date_line = None
    with open(file, "r") as f:
        for i, line in enumerate(f):
            if line.startswith("#D") and not date_line_found:
                date_line_found = True
                date_line = line
            if line.startswith("#"):
                continue
            header = i - 1
            break
    return header, date_line.strip()


def get_xas_data(file_obj):
    header, dateline = getHeader(file_obj.name)
    data = pd.read_csv(file_obj.name, header=header, sep="\t")
    return data, dateline
