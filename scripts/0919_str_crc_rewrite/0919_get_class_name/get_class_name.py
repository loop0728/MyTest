import ast

def get_class_names(filename):
    with open(filename, "r") as source:
        source_contents = source.read()

    # 解析源代码为 AST
    tree = ast.parse(source_contents)

    # 存储找到的类名称
    class_names = []

    # 遍历 AST 节点
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_names.append(node.name)

    return class_names

# 调用函数并打印类名称
filename = "/home/koda.xu/self_test/testSystemApp/0913_mount_path/getMountPath.py"
class_names = get_class_names(filename)
print(class_names)


#case_name = "Str_stress_3"
case_name = "Str"
class_name = case_name.split("_")[0]
print(class_name)

