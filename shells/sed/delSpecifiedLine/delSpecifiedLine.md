### 删除指定字符串所在行
`sed -e '/xxx/d' testfile > tmpfile`  
该命令表示从名为testfile的文件中删除包含字符串"xxx"的行，并将结果输出到名为tmpfile的文件中。

命令说明：   
`sed`：表示要执行sed命令。   
`-e`：表示后面跟着的是要执行的sed命令。   
`'/xxx/d'`：是一个sed命令，其中/xxx/是一个模式匹配，表示匹配包含"xxx"的行，d是sed命令，表示删除匹配到的行。   
`testfile`：要进行处理的输入文件名。  
`\>`：输出重定向符号，用于将命令的输出结果重定向到文件。   
`tmpfile`：输出结果被重定向到的文件名。   
因此，执行该命令后，sed命令会读取testfile文件的内容，删除包含"xxx"的行，并将结果写入tmpfile文件中。如果tmpfile文件不存在，则会创建一个新的文件；如果已存在，则会覆盖原有内容。   

请注意，在执行这个命令之后，原始文件testfile不会受到任何更改，删除操作只会在输出文件tmpfile中进行。   
如果要在原始文件testfile上修改，可以将tmpfile再写回testfile:   
`cat tmpfile > testfile`

