### 获取链接指向的目标文件或目录的绝对路径   
`readlink -f xxx 2>/dev/null`   
该命令用于获取 xxx 文件的绝对路径，并将任何错误输出重定向到 /dev/null，以便在命令执行时不显示错误信息。   

### 命令说明
`readlink -f` 用于解析符号链接并返回目标文件或目录的绝对路径。在这种情况下，readlink -f xxx 将返回 xxx 文件的绝对路径。   
`2>/dev/null` 部分将标准错误输出（stderr）重定向到 /dev/null，这意味着如果发生任何错误，错误消息将被丢弃，不会显示在终端上。   

如果link有指向实际的目标文件，最后返回目标文件的绝对路径；   
如果link没有指向实际的文件，最后返回link指向的目标文件的绝对路径；   
如果link文件本身并不存在，最后返回命令中输入的link文件的绝对路径。   

### 测试   
测试脚本：   
```
#!/bin/sh

readconf=$(readlink -f linkFile 2> /dev/null)
echo $readconf

readconf2=$(readlink -f linkXXX 2> /dev/null)
echo $readconf2

readconf3=$(readlink -f xxx 2> /dev/null)
echo $readconf3
```

测试结果：  
```
koda.xu@szbcl06402:~/my_git/MyTest/shells/readlink/getAbsolutFile$ ls -l
total 12
-rw-r--r-- 1 koda.xu domain users 1983 Dec  1 14:57 getAbsolutFile.md
lrwxrwxrwx 1 koda.xu domain users   10 Dec  1 12:02 linkFile -> targetFile
-rw-r--r-- 1 koda.xu domain users   18 Dec  1 12:02 targetFile
-rwxrwxrwx 1 koda.xu domain users  195 Dec  1 15:02 test.sh
koda.xu@szbcl06402:~/my_git/MyTest/shells/readlink/getAbsolutFile$ ln -fs abc linkXXX
koda.xu@szbcl06402:~/my_git/MyTest/shells/readlink/getAbsolutFile$ ls -l
total 12
-rw-r--r-- 1 koda.xu domain users 1983 Dec  1 14:57 getAbsolutFile.md
lrwxrwxrwx 1 koda.xu domain users   10 Dec  1 12:02 linkFile -> targetFile
lrwxrwxrwx 1 koda.xu domain users    3 Dec  1 15:17 linkXXX -> abc
-rw-r--r-- 1 koda.xu domain users   18 Dec  1 12:02 targetFile
-rwxrwxrwx 1 koda.xu domain users  195 Dec  1 15:02 test.sh
koda.xu@szbcl06402:~/my_git/MyTest/shells/readlink/getAbsolutFile$ ./test.sh
/home/koda.xu/my_git/MyTest/shells/readlink/getAbsolutFile/targetFile
/home/koda.xu/my_git/MyTest/shells/readlink/getAbsolutFile/abc
/home/koda.xu/my_git/MyTest/shells/readlink/getAbsolutFile/xxx
```


