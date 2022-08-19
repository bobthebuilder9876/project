#!/usr/bin/python
import ftplib
import os
import shutil
import csv
from datetime import datetime, timedelta
from time import sleep
from verify import name_valid, file_valid
import re

config = [None] * 10

"""
0 - Date/Time of last FTP pull
1 - Regular FTP pull inteval (seconds)
2 - Server hostname
3 - Server port
4 - Server username
5 - Server password
6 - Working directory
7 - Success directory
8 - Fail directory
9 - CSV logs file

"""

# Convert date/time in filename to datetime object
def toDateTime(filename):
    return datetime(int(filename[9:13]), int(filename[13:15]), int(filename[15:17]), int(filename[17:19]), int(filename[19:21]), int(filename[21:23]))

# Read Config File
def readConfig():
    change = False
    try:
        # Read config file
        file = open("config.txt", "r")
        lines = file.readlines()
        if len(lines) < len(config):
            # Populate missing lines with empty strings
            lines += [""] * (len(config) - len(lines))
        file.close()

        # Populate config list (see above for contents details)
        for counter in range(len(config)):
            lines[counter] = lines[counter].strip()
            match counter:
                case 0:
                    try:
                        if (len(lines[counter]) == 14):
                            config[counter] = datetime(int(lines[counter][0:4]), int(lines[counter][4:6]), int(lines[counter][6:8]), int(lines[counter][8:10]), int(lines[counter][10:12]), int(lines[counter][12:]))
                        else:
                            raise ValueError
                    except ValueError:
                        config[counter] = datetime(1, 1, 1, 0, 0, 0)
                        change = True
                case 1:
                    try:
                        config[counter] = int(lines[counter])
                    except ValueError:
                        config[counter] = 10
                        change = True
                case 2:
                    eles = lines[counter].split(".")
                    try:
                        if len(eles) == 4:
                            for each in eles:
                                if int(each) > 255 or int(each) < 0:
                                    raise ValueError

                            config[counter] = lines[counter]
                        else:
                            raise ValueError
                    except ValueError:
                        config[counter] = "127.0.0.1"
                        change = True
                case 3:
                    try:
                        config[counter] = int(lines[counter])
                    except ValueError:
                        config[counter] = 21
                        change = True
                case 4:
                    config[counter] = lines[counter]
                case 5:
                    config[counter] = lines[counter]
                case 6:
                    config[counter] = lines[counter]
                    if (not os.path.isdir(config[counter])):
                        try:
                            os.makedirs(config[counter])
                            if (config[counter] in ["", ".", ".."]):
                                raise ValueError
                        except:
                            config[counter] = "tmp"
                            if (not os.path.isdir(config[counter])):
                                os.makedirs(config[counter])
                            change = True

                case 7:
                    config[counter] = lines[counter]
                    if (not os.path.isdir(config[counter])):
                        try:
                            os.makedirs(config[counter])
                            if (config[counter] in ["", ".", ".."]):
                                raise ValueError
                        except:
                            config[counter] = "good"
                            if (not os.path.isdir(config[counter])):
                                os.makedirs(config[counter])
                            change = True
                case 8:
                    config[counter] = lines[counter]
                    if (not os.path.isdir(config[counter])):
                        try:
                            os.makedirs(config[counter])
                            if (config[counter] in ["", ".", ".."]):
                                raise ValueError
                        except:
                            config[counter] = "bad"
                            if (not os.path.isdir(config[counter])):
                                os.makedirs(config[counter])
                            change = True
                case 9:
                    config[counter] = lines[counter]
                    if (not os.path.isdir(os.path.dirname(config[counter]))):
                        try:
                            os.makedirs(os.path.dirname(config[counter]))
                        except:
                            config[counter] = "./logs.csv"
                            if (not os.path.isdir(os.path.dirname(config[counter]))):
                                os.makedirs(os.path.dirname(config[counter]))
                            change = True


        # If config was changed, save changes
        if change:
            writeConfig()
        return True
    except OSError as e:
        print(e)
        return False

# Write Config File
def writeConfig():
    with open("config.txt", "w") as file:
        # Stringify non-string data
        out = config.copy()
        out[0] = config[0].strftime("%Y%m%d%H%M%S")
        out[1] = str(config[1])
        out[3] = str(config[3])

        for each in out:
            file.write(each + "\n")

# Read Manual Data Download Commands
def readInstant():
    try:
        file = open("daterange.csv", "r")
        txt = file.read().split(',')
        file.close()
        
        if len(txt) == 2:
            # Start date
            if re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", txt[0]) != None:
                txt[0] = datetime(int(txt[0][0:4]), int(txt[0][4:6]), int(txt[0][6:]), 0, 0, 0)

                # End date
                if re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", txt[1]) != None:
                    txt[1] = datetime(int(txt[1][0:4]), int(txt[1][4:6]), int(txt[1][6:]), 23, 59, 59)
                    os.remove("daterange.csv")
                    return txt
        return None
    except:
        return None

# Save error logs to CSV
def writeCSV(logs, queue):
    try:
        with open(logs, "a+") as file:
            writer = csv.writer(file)
            writer.writerows(queue)
            queue.clear()
    except Exception as e:
        print(e)
        return


def main():
    logBuf = []

    while True:
        instantPull = readInstant()
        # Only pull from server if config is useable and (timer has fired or user requested data)
        if readConfig() and ((datetime.now() - config[0]).total_seconds() >= config[1] or instantPull != None):
            try:
                # Connect & Login
                ftp = ftplib.FTP()
                ftp.set_debuglevel(1)
                ftp.connect(config[2], config[3])
                ftp.login(config[4], config[5])

                # Get list of CSVs on server
                mlsd = ftp.mlsd(facts=[])
                csvs = []
                for each in mlsd:
                    if each[1]["type"] == "file" and each[0].split('.')[-1] == "csv" and "r" in each[1]["perm"]:
                        csvs.append(each[0])

                # Make directories (if don't already exist)
                if not os.path.isdir(config[6]):
                    os.makedirs(config[6]) # Working Directory

                if not os.path.isdir(config[7]):
                    os.makedirs(config[7]) # Success Directory

                if not os.path.isdir(config[8]):
                    os.makedirs(config[8]) # Fail Directory

                # Download CSVs from server
                i = 0
                while i < len(csvs):
                    success = False
                    filename = csvs[i]
                    # Only download if filename is valid and file is new or was requested
                    if name_valid(filename):
                        dt = toDateTime(filename)
                        if (instantPull != None and dt >= instantPull[0] and dt <= instantPull[1]) or dt >= config[0]:
                            # Download file
                            with open(config[6] + "/" + filename, "wb") as f:
                                ftp.retrbinary("RETR " + "/" + filename, f.write)
                                csvs[i] = (filename, dt)
                                i += 1
                                success = True

                    # Remove filenames not selected for download
                    if not success:
                        csvs.pop(i)

                # Close connection
                ftp.close()

                # Check file is good and archive in yyyy/mm/dd directory
                for file in csvs:
                    errs = file_valid(config[6] + "/" + file[0])
                    dtPath = "/" + str(file[1].year) + "/" + str(file[1].month) + "/" + str(file[1].day)
                    # No errors = Good
                    if errs == []:
                        try:
                            shutil.move(config[6] + "/" + file[0], config[7] + dtPath + "/" + file[0])
                        except IOError as err:
                            os.makedirs(config[7] + dtPath)
                            shutil.move(config[6] + "/" + file[0], config[7] + dtPath + "/" + file[0])
                    # Errors = Bad
                    else:
                        try:
                            shutil.move(config[6] + "/" + file[0], config[8] + dtPath + "/" + file[0])
                        except IOError as err:
                            os.makedirs(config[8] + dtPath)
                            shutil.move(config[6] + "/" + file[0], config[8] + dtPath + "/" + file[0])

                        # Store pending error logs in buffer
                        logBuf.append([file[0]] + errs);

                # Update last download time and disable forced pull
                config[0] = datetime.now()
                writeConfig()
            # Bad response
            except ftplib.error_reply as e:
                print(e)
                continue
            # Temporary error
            except ftplib.error_temp as e:
                print(e)
                continue
            # Permanent error
            except ftplib.error_perm as e:
                print(e)
                continue
            # Unknown error
            except ftplib.error_proto as e:
                print(e)
                continue
            except OSError as e:
                print(e)
                continue
            except EOFError as e:
                print(e)
                continue

        # Write contents of error log buffer to file
        if len(logBuf) > 0:
            writeCSV(config[9], logBuf)
            logBuf = []

        # Wait 5 secs before trying again
        sleep(5)

main()
