def get_date_range():
    import re
    start, end = "0","1"
    #Obtaining suitable start date
    while re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", start) == None:
        start = str(input("Please enter suitable start date in format YYYYMMDD: "))
        if re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", start) == None:
            print("Error: Unsuitable Format")
    #Obtaining suitable end date
    while re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", end) == None:
        end = str(input("Please enter suitable end date in format YYYYMMDD: "))
        if re.search("^[0-9]{4}((0[0-9])|(1[0-2]))(([0-2][0-9])|(3[0-1]))$", end) == None:
            print("Error: Unsuitable Format")
    #Checking if start date is after end
    start_ , end_ = int(start) , int(end)
    if start_ > end_:
        print("Start date is after end date \n")
        get_date_range()
    else:
        #Writes to file in current folder called "daterange.csv"
        #Will create file if not present- if present will overwrite
        #Data is in YYYYMMDD format [start],[end]
        string = start+","+end
        f = open("daterange.csv","w")
        f.write(string)
        f.close()

