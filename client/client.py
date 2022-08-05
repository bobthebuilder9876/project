#!/usr/bin/python
from ftplib import FTP, error_perm

interval = 10 # PLACEHOLDER - Regular FTP pull inteval (seconds)
host = "127.0.0.1" # PLACEHOLDER - Server hostname
port = 21 # PLACEHOLDER - Server port
user = "devuser" # PLACEHOLDER - Server username
pswd = "verysecurepassword1234" # PLACEHOLDER - Server password

try:
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login(user, pswd)
    print("Login successful.")
    print(ftp.dir())

except error_perm as e:
    code = str(e)[:3]
    if code == "530": # Auth failed
        print("Invalid login details.")
