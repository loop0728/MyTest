import subprocess

tool = f"./dtc"
dts_filename = f"fdt.dts"
command = [tool, '-I', 'fs', '-O', 'dts', 'base', '-o', dts_filename]
# 运行一个命令并等待其完成
result = subprocess.run(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 打印命令的输出
#print('stdout:', result.stdout)

# 打印命令的错误输出
#print('stderr:', result.stderr)

# 检查命令是否成功执行
if result.returncode == 0:
    print('Success')
else:
    print('Error: Return code', result.returncode)
