import re

def parse_dts_file(dts_file):
    freq = 0
    parse_cpufreq_ready = 0
    parse_volt_ready = 0
    freq_volt_list = []

    with open(dts_file, 'r') as file:
        for line in file:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='replace').strip()
            pattern = re.compile(r'opp[\d]{2}')
            match = pattern.search(line)
            if match:
                parse_cpufreq_ready = 1
                #parse_volt_ready = 1
                continue

            if parse_cpufreq_ready == 1 and "opp-hz" in line:
                opp_hz = line.strip().split('=')
                freq = opp_hz[1].strip().strip('<>;').split()[1]
                parse_cpufreq_ready = 0
                parse_volt_ready = 1

            if parse_volt_ready == 1 and "opp-microvolt" in line:
                opp_microvolt = line.strip().split('=')
                volts = opp_microvolt[1].strip().strip('<>;').split()
                cur_volt = volts[0]
                fast_volt = volts[1]
                slow_volt = volts[2]
                freq_volt_map = [freq, cur_volt, slow_volt, fast_volt]
                freq_volt_list.append(freq_volt_map)
                parse_volt_ready = 0

    return freq_volt_list

dts_path = '../base.dts'
node = 'opp00'
prop_name = 'opp-hz'

freq_volt_list = parse_dts_file(dts_file=dts_path)

print(f"freq_volt_map: {freq_volt_list}")


# 文件路径
file_path = '../base.dts'

# 正则表达式，用于匹配 base_voltage 属性
pattern = re.compile(r'opp[\d]{2} {')

print(f"xxxxxx")
# 读取并解析文件
try:
    with open(file_path, 'r') as file:
        content = file.read()
        print(f"yyyyy")
        matches = pattern.findall(content)
        for match in matches:
            print(f"{match}")

except FileNotFoundError:
    print(f"The file {file_path} was not found.")
except IOError as e:
    print(f"An I/O error occurred: {e.strerror}")
