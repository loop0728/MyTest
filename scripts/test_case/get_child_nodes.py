def parse_dts(dts_file, current_node='', indent=0):
    child_nodes = []

    with open(dts_file, 'r') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith(' ' * (indent + 2)):
                node_name = line.split()[0]
                child_nodes.append(node_name)
                child_nodes.extend(parse_dts(dts_file, node_name, indent + 2))
            elif indent == 0 and line.startswith('}'):
                break

    return child_nodes

dts_path = 'base.dts'
root_node = 'cpus'
all_child_nodes = parse_dts(dts_file=dts_path, current_node=root_node)

print(f"All child nodes of {root_node}: {all_child_nodes}")

