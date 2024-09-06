def parse_dts_file(dts_file, node_path, property_name):
    property_value = None
    inside_node = False

    with open(dts_file, 'r') as file:
        for line in file:
            if line.strip().startswith(f"{node_path}/") or line.strip().startswith(f"{node_path} {{"):
                inside_node = True
                continue

            if inside_node and line.strip().endswith("}"):
                break

            if inside_node:
                if f"{property_name} = " in line:
                    parts = line.split(f"{property_name} = ")
                    property_value = parts[1].strip().rstrip(";")
                    break

    return property_value

dts_path = 'base.dts'
node = 'opp00'
prop_name = 'opp-hz'

value = parse_dts_file(dts_file=dts_path, node_path=node, property_name=prop_name)
print(f"The value of {prop_name} is: {value}")

