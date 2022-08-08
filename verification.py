import csv
import re

def csv_to_list(file):
    try:
        with open(file, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
            return(data)
    except:
        return None

def correct_header(data):
    header = data[0]
    correct_header = ['batch_id', 'timestamp', 'reading1', 'reading2', 'reading3', 'reading4', 'reading5', 'reading6', 'reading7', 'reading8', 'reading9', 'reading10']
    if header == correct_header:
        return(True)
    else:
        return(False)

def unique_batch_id(data):
    lst = []
    for i in range (1,11):
        if data[i][0] in lst:
            return(False)
        else:
            lst.append(data[i][0])
    return(True)

def suitable_values(data):
    for i in range (1,11):
        for j in range(2,12):
            if re.search("^[0-9]\.[0-9][0-9]?[0-9]?$", data[i][j]) == None:
                return False
            value = float(data[i][j]) # After regex so if format not valid no error
            if value > 9.9:
                return False
    return(True)

def non_empty_file(data): #Strictly non-empty, a space counts as non-empty
    if data == ([]):
        return(False)
    else:
        return(True)

def correct_columns(data):
    for i in range (0,11):
        if len(data[i]) != 12:
            return(False)
    else:
        return(True)

def name_valid(file):
    if re.search("^MED_DATA_[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))(([0-1][0-9]|2[0-4]))(([0-5][0-9])|(60))(([0-5][0-9])|(60))\.csv$", file) == None:
        return False
    else:
        return(True)

def file_valid(file):
    data = csv_to_list(file)
    if data == None:
        return ["Wrong File Format"]
    lst = []
    if not name_valid(file):
        lst.append("Invalid Name")
    if not non_empty_file(data):
        return ["Empty File"]
    if not correct_columns(data):
        return ["Missing Column"]
    if not unique_batch_id(data):
        lst.append("Duplicate ID")
        print("ID")
    if not correct_header(data):
        lst.append("Incorrect Header")
        print("header")
    if not suitable_values(data):
        print("value")
        lst.append("Unsuitable Value")
    return(lst)
