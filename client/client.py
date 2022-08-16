#!/usr/bin/python
import ftplib
import os
import shutil
import csv
from datetime import datetime
from time import sleep

def validate(filename):
    return ["error"]

def writeCSV(logs, queue):
    try:
        with open(logs, "a") as file:
            writer = csv.writer(file)
            while len(queue) > 0:
                writer.write(queue[0])
                queue.pop(0)
    except:
        return

def main():
    last = datetime(2022, 8, 5, 14, 25, 00) # PLACEHOLDER - Date/Time of last FTP pull
    interval = 10 # PLACEHOLDER - Regular FTP pull inteval (seconds)

    host = "127.0.0.1" # PLACEHOLDER - Server hostname
    port = 21 # PLACEHOLDER - Server port
    user = "devuser" # PLACEHOLDER - Server username
    pswd = "verysecurepassword1234" # PLACEHOLDER - Server password

    tmpdir = "tmp" # PLACEHOLDER - Working directory
    gooddir = "good" # PLACEHOLDER - Success directory
    baddir = "bad" # PLACEHOLDER - Fail directory

    logs = "logs.csv" # PLACEHOLDER - CSV logs file
    logBuf = []

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
                    if each[1]["type"] == "file" and each[0].split('.')[-1] == "csv" and "r" in each[1]["perm"]:
                        csvs.append(each[0])

                # Make directories (if don't already exist)
                if not os.path.isdir(tmpdir):
                    os.makedirs(tmpdir)

                if not os.path.isdir(gooddir):
                    os.makedirs(gooddir)

                if not os.path.isdir(baddir):
                    os.makedirs(baddir)

                # Download CSVs from server
                for filename in csvs:
                    # Skip downloading if file with same name already exists in temporary files directory
                    if os.path.exists(tmpdir + "/" + filename):
                        continue
                    with open(tmpdir + "/" + filename, "wb") as f:
                        ftp.retrbinary("RETR " + "/" + filename, f.write)

                # Close connection
                ftp.close()

                for filename in csvs:
                    errs = validate(filename)
                    if errs == []:
                        shutil.move(tmpdir + "/" + filename, gooddir + "/" + filename)
                    else:
                        shutil.move(tmpdir + "/" + filename, baddir + "/" + filename)
                        logBuf.append([filename] + errs);

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

        if len(logBuf) > 0:
            writeCSV(logs, logBuf)

main()
