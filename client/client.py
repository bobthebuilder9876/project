#!/usr/bin/python
import ftplib
import os
from datetime import datetime
from time import sleep

last = datetime(2022, 8, 5, 14, 25, 00) # PLACEHOLDER - Date/Time of last FTP pull
interval = 10 # PLACEHOLDER - Regular FTP pull inteval (seconds)
host = "127.0.0.1" # PLACEHOLDER - Server hostname
port = 21 # PLACEHOLDER - Server port
user = "devuser" # PLACEHOLDER - Server username
pswd = "verysecurepassword1234" # PLACEHOLDER - Server password

tmpdir = "tmp"
gooddir = "good"
baddir = "bad"

while True:
    if (datetime.now() - last).total_seconds() >= interval:
        try:
            # Connect & Login
            ftp = ftplib.FTP()
            ftp.set_debuglevel(1)
            ftp.connect(host, port)
            ftp.login(user, pswd)

            # Get list of CSVs on server
            mlsd = ftp.mlsd(facts=[])
            csvs = []
            for each in mlsd:
                if each[1]["type"] == "file" and each[0].split('.')[-1] == "csv" and 'r' in each[1]["perm"]:
                    csvs.append(each[0])

            # Make temporary files directory (if doesn't already exist)
            if not os.path.isdir(tmpdir):
                os.makedirs(tmpdir)

            # Download CSVs from server
            for filename in csvs:
                # Skip downloading if file with same name already exists in temporary files directory
                if os.path.exists(tmpdir + "/" + filename):
                    continue
                with open(tmpdir + "/" + filename, 'wb') as f:
                    ftp.retrbinary('RETR ' + filename, f.write)

            # Close connection
            ftp.close()

            # Update last download time
            last = datetime.now()
        # Bad response
        except ftplib.error_reply as e:
            continue
        # Temporary error
        except ftplib.error_temp as e:
            continue
        # Permanent error
        except ftplib.error_perm as e:
            code = str(e)[:3]
            if code == "530": # Auth failed
                print("Invalid login details.")
            else:
                raise e
        # Unknown error
        except ftplib.error_proto as e:
            continue
        except OSError:
            continue
        except EOFError:
            continue
    else:
        sleep(5)
