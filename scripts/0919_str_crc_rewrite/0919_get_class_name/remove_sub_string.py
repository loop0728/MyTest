import re
original_string = "Hello, World! This is a test string. Another test."
substrings_to_remove = ["World!", "Another"]

for substring in substrings_to_remove:
    original_string = original_string.replace(substring, "")

print(original_string)  # 输出: "Hello,  This is a test string.  test."


# 原始字符串
original_string3 = "Hello, World! This is a test string. sssssss sdajdhaklda Another test."
original_string2 = "Hello, World! This is a test string. param=xxx,xxx Another test."

# 定义正则表达式模式，匹配 'param=' 后跟任何字符（包括逗号），直到空格或字符串末尾
pattern = r"param=[^ ]* "

# 使用 re.sub() 替换匹配的部分为空字符串
modified_string = re.sub(pattern, "", original_string2)

print(original_string2)
print(modified_string)  # 输出: "Hello, World! This is a test string. Another test."

modified_string3 = re.sub(pattern, "", original_string3)
print(original_string3)
print(modified_string3)
