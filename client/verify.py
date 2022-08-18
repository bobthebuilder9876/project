import csv
import re

#this function uses the csv library functions to take an argument of a file location and returns the contents of the file as a 2d list
#if there is an error here such as not csv it will return None and later in the program this error is returned
def csv_to_list(file):
    try:
        with open(file, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
            return(data)
    except:
        return None

#compares the headers of the file to what the header should be
def correct_header(data):
    header = data[0]
    correct_header = ['batch_id', 'timestamp', 'reading1', 'reading2', 'reading3', 'reading4', 'reading5', 'reading6', 'reading7', 'reading8', 'reading9', 'reading10']
    if header == correct_header:
        return(True)
    else:
        return(False)

#cycles through the first element in each row and adds them to a list, compares each new element to those already in the list to make sure they're unique 
def unique_batch_id(data):
    lst = []
    for i in range (1,11):
        if data[i][0] in lst:
            return(False)
        else:
            lst.append(data[i][0])
    return(True)

#cycles through all areas where the value should be and makes sure that they are <9.9 and have between 1 and 3 decimal places
def suitable_values(data):
    for i in range (1,11):
        for j in range(2,12):
            if re.search("^[0-9]\.[0-9][0-9]?[0-9]?$", data[i][j]) == None:
                return False
            value = float(data[i][j]) # After regex so if format not valid no error (as guaranteed to be suitable)
            if value > 9.9:
                return False
    return(True)

#checks the file is not empty
def non_empty_file(data): #Strictly non-empty, a space counts as non-empty
    if data == ([]):
        return(False)
    else:
        return(True)

#checks that there are the correct number of columns in each row
def correct_columns(data):
    for i in range (0,11):
        if len(data[i]) != 12:
            return(False)
    else:
        return(True)

#uses regex to make sure that the filenames meet the set criteria
#the date section is not perfect (for example the 31st february is a valid date)
def name_valid(file):
    if re.search("^MED_DATA_[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))(([0-1][0-9]|2[0-4]))(([0-5][0-9])|(60))(([0-5][0-9])|(60))\.csv$", file) == None:
        return False
    else:
        return(True)

#overall function that calls each of the above components to give an overall validation check of the file
#if valid returns an empty list
#if not it returns a list containing the error(s) 
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
    if not correct_header(data):
        lst.append("Incorrect Header")
    if not suitable_values(data):
        lst.append("Unsuitable Value")
    return(lst)
