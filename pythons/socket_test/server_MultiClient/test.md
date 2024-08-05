```
koda.xu@szbcl06402:~/my_git/MyTest/pythons/socket_test/server_MultiClient$ python3 server.py &
[1] 27978
koda.xu@szbcl06402:~/my_git/MyTest/pythons/socket_test/server_MultiClient$ Server listening on 127.0.0.1:12345

koda.xu@szbcl06402:~/my_git/MyTest/pythons/socket_test/server_MultiClient$ python3 client.py
Enter message to send (or 'quit' to exit): Connected to ('127.0.0.1', 56360)
miaomiaomiao
Received from ('127.0.0.1', 56360): miaomiaomiao
Received: miaomiaomiao
Enter message to send (or 'quit' to exit): xxx
Received from ('127.0.0.1', 56360): xxx
Received: xxx
Enter message to send (or 'quit' to exit): 111
Received from ('127.0.0.1', 56360): 111
Received: 111
Enter message to send (or 'quit' to exit): qqq
Received from ('127.0.0.1', 56360): qqq
Received: qqq
Enter message to send (or 'quit' to exit):
```
