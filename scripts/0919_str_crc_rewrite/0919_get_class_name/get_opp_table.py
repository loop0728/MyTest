import re

def get_opp_table_from_dts(dts_file):
    """get opp table from dts
    Args:
        dts_file (str): the path of dts file
    Returns:
        freq_volt_list (list): freq-cur_vol-min_vol-max_vol mapping list

        freq_volt_list format is :
        [
            [freq, cur_volt, fast_volt, slow_volt],
            [freq, cur_volt, fast_volt, slow_volt],
            ...
        ]
    """
    parse_opp_node_ready = 0
    parse_cpufreq_done = 0
    parse_volt_done = 0
    freq_volt_list = []
    opp_item = {
        'freq': 0,
        'cur_volt': 0,
        'fast_volt': 0,
        'slow_volt': 0
    }

    with open(dts_file, 'r') as file:
        for line in file:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            pattern = re.compile(r'opp[\d]{2} {')
            match = pattern.search(line)
            if match:
                parse_opp_node_ready = 1
                continue

            if parse_opp_node_ready == 1 and "opp-hz" in line:
                opp_hz = line.strip().split('=')
                opp_item['freq'] = int(opp_hz[1].strip().strip('<>;').split()[1], 16)
                parse_cpufreq_done = 1
                continue

            if parse_opp_node_ready == 1 and "opp-microvolt" in line:
                opp_microvolt = line.strip().split('=')
                volts = opp_microvolt[1].strip().strip('<>;').split()
                opp_item['cur_volt'] = int(volts[0], 16)
                opp_item['fast_volt'] = int(volts[1], 16)
                opp_item['slow_volt'] = int(volts[2], 16)
                parse_volt_done = 1
                continue

            if parse_cpufreq_done == 1 and parse_volt_done == 1:
                freq_volt_list.append(list(opp_item.values()))
                #opp_array = list(opp_item.values())
                #freq_volt_list.append(opp_array)
                parse_cpufreq_done = 0
                parse_volt_done = 0
                parse_opp_node_ready = 0

    freq_volt_list.sort(key=lambda x: x[0])
    return freq_volt_list

my_opp_table = get_opp_table_from_dts("fdt.dts")
print(my_opp_table)
