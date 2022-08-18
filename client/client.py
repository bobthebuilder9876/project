#!/usr/bin/python
import ftplib
import os
import shutil
import csv
from datetime import datetime, timedelta
from time import sleep
from .verify import name_valid, file_valid

config = [None] * 13

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

pullnow = False # PLACEHOLDER - Trigger manual data pull
pullstart = datetime(2022, 8, 5, 14, 25, 00) # PLACEHOLDER - Start of pull range
pullend = datetime(2022, 8, 12, 14, 25, 00) # PLACEHOLDER - End of pull range-

def toDateTime(filename):
    return datetime(int(filename[9:13]), int(filename[13:15]), int(filename[15:17]), int(filename[17:19]), int(filename[19:21]), int(filename[21:23]))

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

def writeConfig():
    with open("config.txt", "w") as file:
        file.writelines(config)

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
            
        if readConfig() and (datetime.now() - config[0]).total_seconds() >= config[1]:
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
                    if name_valid(filename):
                        dt = toDateTime(filename)
                        if (pullnow and dt >= pullstart and dt <= pullend) or datetime >= config[0]:
                            with open(config[6] + "/" + filename, "wb") as f:
                                ftp.retrbinary("RETR " + "/" + filename, f.write)
                                i += 1
                                csvs[i] = (filename, dt)
                                success = True

                    if not success:
                        csvs.pop(i)

                # Close connection
                ftp.close()

                # Check file is good and archive
                for file in csvs:
                    errs = file_valid(file[0])
                    dtPath = "/" + str(file[1].year) + "/" + str(file[1].month) + "/" + str(file[1].day)
                    if errs == []:
                        try:
                            shutil.move(config[6] + "/" + file[0], config[7] + dtPath + "/" + file[0])
                        except IOError as err:
                            os.makedirs(config[7] + dtPath)
                            shutil.move(config[6] + "/" + file[0], config[7] + dtPath + "/" + file[0])
                    else:
                        try:
                            shutil.move(config[6] + "/" + file[0], config[8] + dtPath + "/" + file[0])
                        except IOError as err:
                            os.makedirs(config[8] + dtPath)
                            shutil.move(config[6] + "/" + file[0], config[8] + dtPath + "/" + file[0])

                        logBuf.append([filename] + errs);

                # Update last download time and disable forced pull
                config[0] = datetime.now()
                pullnow = False
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
            writeCSV(config[9], logBuf)

main()
