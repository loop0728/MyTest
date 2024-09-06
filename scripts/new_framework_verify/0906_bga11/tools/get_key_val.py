# 定义字符串
s = "<0xde2b0 0xd9490 0xde2b0>"

# 移除尖括号并分割字符串
elements = s.strip('<>').split()

# 获取第三个元素的十六进制字符串
third_element_hex = elements[2]

# 转换为十进制数值
third_element_dec = int(third_element_hex, 16)

print(third_element_dec)

