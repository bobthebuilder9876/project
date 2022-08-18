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

logBuf = []

# Convert date/time in filename to datetime object
def toDateTime(filename):
    return datetime(int(filename[9:13]), int(filename[13:15]), int(filename[15:17]), int(filename[17:19]), int(filename[19:21]), int(filename[21:23]))

# Read Config File
def readConfig():
    change = False
    try:
        with open("config.txt", "r") as file:
            lines = file.readlines()
            for counter in range(len(lines)):
                match counter:
                    case 0:
                        try:
                            if (len(lines[counter]) == 14):
                                dt = int(lines[counter])
                                config[counter] = datetime(lines[counter][0:4], lines[counter][4:6], lines[counter][6:8], lines[counter][8:10], lines[counter][10:12], lines[counter][12:14])
                            else:
                                raise ValueError
                        except ValueError:
                            config[counter] = datetime.now() - timedelta(seconds=config[1])
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
                            except:
                                config[counter] = "tmp"
                                os.makedirs(config[counter])
                                change = True

                    case 7:
                        config[counter] = lines[counter]
                        if (not os.path.isdir(config[counter])):
                            try:
                                os.makedirs(config[counter])
                            except:
                                config[counter] = "good"
                                os.makedirs(config[counter])
                                change = True
                    case 8:
                        config[counter] = lines[counter]
                        if (not os.path.isdir(config[counter])):
                            try:
                                os.makedirs(config[counter])
                            except:
                                config[counter] = "bad"
                                os.makedirs(config[counter])
                                change = True
                    case 9:
                        config[counter] = lines[counter]
                        if (not os.path.exists(config[counter])):
                            try:
                                os.makedirs(os.path.dirname(config[counter]))
                            except:
                                config[counter] = "logs.csv"
                                change = True


        if change:
            writeConfig()
        return True
    except:
        return False

# Write Config File
def writeConfig():
    with open("config.txt", "w") as file:
        out = config
        out[0] = str(config[0].year + config[0].month + config[0].day + config[0].hour + config[0].minute + config[0].second)
        out[1] = str(config[1])
        out[3] = str(config[3])
        file.writelines(out)

# Read Manual Data Download Commands
def readInstant():
    try:
        with open("daterange.csv", "r") as file:
            txt = file.read().split(',')
            if len(txt) == 2:
                if re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", txt[0]) != None:
                    txt[0] = datetime(txt[0:4], txt[4:6], txt[6:8], 0, 0, 0)

                    if re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", txt[1]) != None:
                        txt[1] = datetime(txt[0:4], txt[4:6], txt[6:8], 23, 59, 59)
                        return txt
        return None
    except:
        return None

# Save error logs to CSV
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
                        if (instantPull != None and dt >= instantPull[0] and dt <= instantPull[1]) or datetime >= config[0]:
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
                    errs = file_valid(file[0])
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
                        logBuf.append([filename] + errs);

                # Update last download time and disable forced pull
                config[0] = datetime.now()
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

        # Write contents of error log buffer to file
        if len(logBuf) > 0:
            writeCSV(config[9], logBuf)
            logBuf = []

main()
